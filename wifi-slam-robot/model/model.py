from typing import NamedTuple


class WifiSample(NamedTuple):
    ssid: str
    signal_strength: int
