import argparse
import asyncio
import functools
import websockets
from sweeppy import Scan

from network.tcp_socket import socket_coroutine
from network.wifi_scan import wifi_scan_generator
from sweep.sweep import sweep_scan_generator
from typing import AsyncGenerator, List
from wifi import Cell


parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('port')
args = parser.parse_args()


def create_packet(wifi_scan: List[Cell], sweep_scan: Scan):
    wifi_items = list(map(lambda cell: (cell.ssid, cell.signal), wifi_scan))
    sweep_items = sweep_scan.samples
    return {'wifi_scan': wifi_items, 'sweep_scan': sweep_items}


async def main(wifi_gen: AsyncGenerator[List[Cell], None], sweep_gen: AsyncGenerator[Scan, None], network_queue):
    while True:
        wifi_scan = await wifi_gen.__anext__()
        sweep_scan = await sweep_gen.__anext__()
        await network_queue.put(create_packet(wifi_scan, sweep_scan))
        await asyncio.sleep(3)

if __name__ == '__main__':
    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    tcp_socket_queue = asyncio.Queue(1)

    print('Listening for TCP connections')
    socket_handler = functools.partial(socket_coroutine, network_queue=tcp_socket_queue)
    start_server = websockets.serve(socket_handler, args.hostname, args.port)

    wifi_gen = wifi_scan_generator('wlan1')
    event_loop.create_task(wifi_gen)
    sweep_gen = sweep_scan_generator('/dev/ttyUSB0')
    event_loop.create_task(sweep_gen)

    event_loop.create_task(main(wifi_gen, sweep_gen, tcp_socket_queue))
    event_loop.run_until_complete(start_server)
    event_loop.run_forever()
