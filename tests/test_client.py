import asyncio

import pytest

from downdoom import Client, Server


@pytest.mark.asyncio
async def test_client() -> None:
    server = Server(ping_interval=500)
    server.add_service("test", -1000)
    client = Client("test", "localhost")

    flag = asyncio.Event()
    server.service_up_callbacks.append(lambda _: flag.set())

    task_server = asyncio.create_task(server.run())
    task_client = asyncio.create_task(client.run())

    await flag.wait()

    task_client.cancel()
    task_server.cancel()
