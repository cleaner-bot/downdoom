import asyncio
from unittest import mock
import pytest

from downdoom import Server


@pytest.mark.asyncio
async def test_server_callbacks():
    server = Server()
    
    @server.listen_up
    def test_callback(name: str):
        pass

    server.listen_down(test_callback)
    assert server.service_up_callbacks == [test_callback]
    assert server.service_down_callbacks == [test_callback]

    sync_mock = mock.Mock(return_value=None)
    async_mock = mock.AsyncMock()
    server.service_down_callbacks.extend([sync_mock, async_mock])

    await server.service_is_down("test")

    sync_mock.assert_called_once_with("test")
    async_mock.assert_called_once_with("test")


@pytest.mark.asyncio
async def test_server():
    server = Server(ping_interval=0)
    server.add_service("test")

    flag = asyncio.Event()
    server.service_down_callbacks.append(lambda _: flag.set())
    
    task = asyncio.create_task(server.run())

    await flag.wait()

    task.cancel()
