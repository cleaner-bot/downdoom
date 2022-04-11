
# downdoom

Really simple TCP based down detector with ping/pong.

## server

```py
from downdoom import Server

server = Server(
    ping_interval=30_000,  # 30s (the default)
    host="0.0.0.0",  # default
    port=23000,  # default
)
# add all known services, so they can be detected as being down without ever 
# receiving a ping from them
server.add_service("test_service")


@server.listen_up
def it_went_up(service: str):  # also supports async functions
    print(f"{service} went up")


@server.listen_down
def it_went_down(service: str):
    print(f"{service} went down")


# you can also use
# server.service_up_callbacks (normal list, so you can append, remove etc)
# and server.service_down_callbacks

await server.run()
```

## client

```py
from downdoom import Client

client = Client(
    "test_service",  # service name
    "localhost",  # server host
    port=23000,  # server port (the default)
)

await client.run()
# or run in background:
# >>> task = asyncio.create_task(client.run())
# and then cancel when shutting down/relaoding stuff
# >>> task.cancel()
```

## relays

Send a notification directly into your Discord server. (basically just builtin callbacks)

```py
from downdoom import Server
from downdoom.relays.discord import DiscordRelay


server = Server(...)

...

discordrelay = DiscordRelay(
    "https://discord.com/api/webhooks/962323397348581387/To-Sm8zGS2M9OGf3H7mrpO0hPBe-9b7IeKchhWbnPkaJaaXBQRJQYYfcXiy1GkJqwzx8",
    content="<@633993042755452932>",  # ping someone
)
discordrelay.add_to_server(server)

....
```
