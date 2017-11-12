import argparse
import asyncio
import functools
import websockets
from network.tcp_socket import socket_coroutine
from network.wifi_scan import wifi_scan_generator
from sweep.sweep import sweep_scan_generator
from typing import AsyncGenerator, List
from wifi import Cell


parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('port')
args = parser.parse_args()


async def main(wifi_generator: AsyncGenerator[List[Cell], None], network_queue):
    while True:
        wifi_scan = await wifi_generator.__anext__()
        await network_queue.put(wifi_scan)
        await asyncio.sleep(3)

if __name__ == '__main__':
    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    tcp_socket_queue = asyncio.Queue()

    print('Listening for TCP connections')
    socket_handler = functools.partial(socket_coroutine, network_queue=tcp_socket_queue)
    start_server = websockets.serve(socket_handler, args.hostname, args.port)

    wifi_gen = wifi_scan_generator('wlan1')
    # sweep_coro = sweep.sweep_scan_coroutine('/dev/ttyUSB0')

    event_loop.create_task(wifi_gen)
    event_loop.create_task(main(wifi_gen, tcp_socket_queue))
    event_loop.run_until_complete(start_server)
    event_loop.run_forever()
