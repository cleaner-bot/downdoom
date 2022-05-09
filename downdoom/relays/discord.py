import httpx

from .relay import Relay

_user_agent = "DownDoomAlert (https://github.com/cleaner-bot/downdoom, 0.1.0)"


class DiscordRelay(Relay):
    def __init__(
        self,
        webhook_url: str,
        content: str | None = None,
        aclient: httpx.AsyncClient | None = None,
    ):
        self.webhook_url = webhook_url
        self.content = content

        if aclient is None:
            aclient = httpx.AsyncClient(headers={"user-agent": _user_agent})
        self.aclient = aclient

    async def on_up(self, name: str):
        body = {
            "content": self.content,
            "embeds": [{"title": f"{name} is back!", "color": 0x10B981}],
        }
        await self.execute_webhook(body)

    async def on_down(self, name: str):
        body = {
            "content": self.content,
            "embeds": [{"title": f"{name} is down!", "color": 0xF43F5E}],
        }
        await self.execute_webhook(body)

    async def execute_webhook(self, body):
        await self.aclient.post(self.webhook_url, json=body)
