from typing import AsyncGenerator, List
from wifi import Cell

from model import WifiSample


def __scan__(interface: str) -> List[WifiSample]:
    return list(map(lambda cell: WifiSample(cell.ssid, cell.signal), Cell.all(interface)))


async def wifi_scan_generator(network_interface: str) -> AsyncGenerator[List[WifiSample], None]:
    while True:
        stuff = __scan__(network_interface)
        yield stuff
