from typing import AsyncGenerator
from typing import List
from typing import Iterable
from wifi import Cell


def __scan__(interface: str) -> List[Cell]:
    result: List[Cell] = []
    for item in Cell.all(interface):
        result.append(item)
    return result


async def wifi_scan_generator(network_interface: str) -> AsyncGenerator[List[Cell], None]:
    while True:
        stuff = __scan__(network_interface)
        print(f'Item in generator: {stuff}')
        yield stuff
