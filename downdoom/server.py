import asyncio
import logging
import time
import typing

from .interval import INTERVAL

logger = logging.getLogger(__name__)
CallbackType = typing.Callable[[str], typing.Awaitable | None]


class Server:
    last_ping: dict[str, float]
    down_services: set[str]
    service_up_callbacks: list[CallbackType]
    service_down_callbacks: list[CallbackType]

    def __init__(
        self, ping_interval: int = 30_000, host: str = "0.0.0.0", port: int = 23000
    ) -> None:
        self.ping_interval = ping_interval
        self.host = host
        self.port = port

        self.last_ping = {}
        self.down_services = set()
        self.service_up_callbacks = []
        self.service_down_callbacks = []

    def add_service(self, service: str, last_ping: float | None = None) -> None:
        if last_ping is None:
            last_ping = time.monotonic()
        self.last_ping[service] = last_ping

    def listen_up(self, cb: CallbackType) -> CallbackType:
        self.service_up_callbacks.append(cb)
        return cb

    def listen_down(self, cb: CallbackType) -> CallbackType:
        self.service_down_callbacks.append(cb)
        return cb

    async def run(self) -> None:
        await asyncio.gather(self.server(), self.downtimer())

    async def server(self) -> None:
        server = await asyncio.start_server(
            self.handle_connection, self.host, self.port
        )
        listening = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        logger.info(f"downdoom listening on {listening}")

        async with server:
            await server.serve_forever()

    async def handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        service = None
        sequence = 0
        try:
            # get the name of the service
            (service_length,) = await reader.readexactly(1)
            service = (await reader.readexactly(service_length)).decode()

            # send the ping interval (in ms)
            writer.write(INTERVAL.pack(self.ping_interval))
            await writer.drain()

            while True:
                (recv_sequence,) = await reader.readexactly(1)
                writer.write(bytes([(recv_sequence + 1) & 0xFF]))  # pong
                await writer.drain()

                if recv_sequence != (sequence + 1) & 0xFF:  # skipped sequences
                    distance = abs(recv_sequence - sequence)
                    logger.warning(f"service {service!r} skipped {distance} sequences")

                sequence = recv_sequence
                self.last_ping[service] = time.monotonic()
                logger.debug(f"service {service!r} pung at {self.last_ping[service]}")

        except asyncio.IncompleteReadError:
            if service is None:
                origin = writer.get_extra_info("peername")
                logger.info(f"unknown connection closed, origin={origin}")
            else:
                logger.info(f"connection to {service!r} closed")

    async def downtimer(self) -> None:
        while True:
            now = time.monotonic()
            for service, last_ping in self.last_ping.items():
                is_down = now - last_ping >= 0.002 * self.ping_interval
                if (service in self.down_services) != is_down:
                    if is_down:
                        logger.warning(f"{service!r} went down")
                        asyncio.create_task(self.service_is_down(service))
                        self.down_services.add(service)
                    else:
                        logger.info(f"{service!r} is up")
                        asyncio.create_task(self.service_is_up(service))
                        self.down_services.remove(service)

            await asyncio.sleep(self.ping_interval / 1000)

    async def service_is_down(self, service: str) -> None:
        for callback in self.service_down_callbacks:
            result = callback(service)
            if result is not None:
                await result

    async def service_is_up(self, service: str) -> None:
        for callback in self.service_up_callbacks:
            result = callback(service)
            if result is not None:
                await result
