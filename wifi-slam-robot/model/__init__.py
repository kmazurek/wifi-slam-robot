from typing import NamedTuple


class WifiSample(NamedTuple):
    ssid: str
    signal_strength: int


class SweepSample(NamedTuple):
    angle: int
    distance: int
    signal_strength: int
