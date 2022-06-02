from ..server import Server


class Relay:
    async def on_up(self, name: str) -> None:
        raise NotImplementedError

    async def on_down(self, name: str) -> None:
        raise NotImplementedError

    def add_to_server(self, server: Server) -> None:
        server.service_up_callbacks.append(self.on_up)
        server.service_down_callbacks.append(self.on_down)

    def remove_from_server(self, server: Server) -> None:
        server.service_up_callbacks.remove(self.on_up)
        server.service_down_callbacks.remove(self.on_down)
