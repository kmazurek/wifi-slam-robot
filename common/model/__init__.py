from enum import Enum
from typing import NamedTuple


class RobotStates(Enum):
    INITIALISING = 0
    MOVING = 1
    STOPPED = 2
    FINISHED = 3


class WifiSample(NamedTuple):
    ssid: str
    signal_strength: int


class SweepSample(NamedTuple):
    angle: int
    distance: int
    signal_strength: int
