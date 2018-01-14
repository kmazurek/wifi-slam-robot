import requests
from model import WifiSample
from typing import List
from wifi import Cell


def send_request(request: dict, address: str, port: int) -> dict:
    response = requests.post(f'http://{address}:{port}/', json=request)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def scan_wifi_interface(interface: str) -> List[WifiSample]:
    return list(map(lambda cell: WifiSample(cell.ssid, cell.signal), Cell.all(interface)))
