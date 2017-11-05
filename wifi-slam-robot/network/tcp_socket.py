import asyncio
import websockets
import json


async def socket_coroutine(socket: websockets.WebSocketCommonProtocol, path, network_queue: asyncio.Queue):
    while True:
        try:
            data = await network_queue.get()
            await socket.send(f"{json.dumps(data)}")
        finally:
            socket.close()
