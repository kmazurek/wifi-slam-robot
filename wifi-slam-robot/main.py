import argparse
import asyncio
import functools
import websockets

from model import WifiSample, SweepSample
from network.tcp_socket import socket_coroutine
from network.wifi_scan import wifi_scan_generator
from sweep.sweep import sweep_scan_generator
from typing import AsyncGenerator, List


parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('port')
args = parser.parse_args()


async def main(
        wifi_gen: AsyncGenerator[List[WifiSample], None],
        sweep_gen: AsyncGenerator[List[SweepSample], None],
        network_queue):
    while True:
        wifi_scan = await wifi_gen.__anext__()
        sweep_scan = await sweep_gen.__anext__()
        await network_queue.put({'wifi_scan': wifi_scan, 'sweep_scan': sweep_scan})
        await asyncio.sleep(3)

if __name__ == '__main__':
    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    tcp_socket_queue = asyncio.Queue(1)

    print('Listening for TCP connections . . .')
    socket_handler = functools.partial(socket_coroutine, network_queue=tcp_socket_queue)
    start_server = websockets.serve(socket_handler, args.hostname, args.port)
    event_loop.run_until_complete(start_server)

    wifi_gen = wifi_scan_generator('wlan1')
    sweep_gen = sweep_scan_generator('/dev/ttyUSB0')
    event_loop.run_until_complete(main(wifi_gen, sweep_gen, tcp_socket_queue))

    event_loop.run_forever()
