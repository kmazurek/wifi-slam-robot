from typing import Iterable
from wifi import Cell


def __scan__(interface: str) -> Iterable[Cell]:
    return Cell.all(str(interface))


async def wifi_scan_coroutine(network_interface: str):
    while True:
        yield __scan__(network_interface)
