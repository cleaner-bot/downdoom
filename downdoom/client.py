import asyncio
import logging

from .interval import INTERVAL

logger = logging.getLogger(__name__)


class Client:
    writer: asyncio.StreamWriter | None = None
    reader: asyncio.StreamReader | None = None
    ping_interval: int | None = None

    def __init__(self, service: str, host: str, port: int = 23000) -> None:
        self.service = service
        self.host = host
        self.port = port
        self.sequence = 0

    async def connect_to_server(self):
        logger.debug(
            f"connecting as {self.service!r} to server at {self.host}:{self.port}"
        )
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        self.writer.write(bytes([len(self.service)]))
        self.writer.write(self.service.encode())
        await self.writer.drain()

        ping_interval_raw = await self.reader.readexactly(INTERVAL.size)
        (self.ping_interval,) = INTERVAL.unpack(ping_interval_raw)
        self.sequence = 1
        logger.info("connected to server")

    async def establish_connection(self):
        while True:
            try:
                await self.connect_to_server()
            except asyncio.IncompleteReadError:
                pass
            except OSError:
                pass
            else:
                break

            logger.debug("failed to connect to server")
            await asyncio.sleep(1)  # backoff

    def connection_lost(self):
        self.writer = self.reader = self.ping_interval = None

    async def run(self):
        while True:
            await self.establish_connection()
            while True:
                try:
                    await self.send_ping()
                except asyncio.IncompleteReadError:
                    break
                except ConnectionError:
                    break
                else:
                    await asyncio.sleep(self.ping_interval / 1000)

            self.connection_lost()

    async def send_ping(self):
        self.writer.write(bytes([self.sequence]))
        await self.writer.drain()

        (recv_sequence,) = await self.reader.readexactly(1)
        if recv_sequence != (self.sequence + 1) & 0xFF:
            distance = abs(recv_sequence - self.sequence)
            logger.warning(f"server skipped {distance} sequences")

        self.sequence = recv_sequence
        logger.debug("pung successfully")
