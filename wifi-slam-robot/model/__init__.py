from typing import NamedTuple, TypeVar, Generic
from threading import Lock


class WifiSample(NamedTuple):
    ssid: str
    signal_strength: int


class SweepSample(NamedTuple):
    angle: int
    distance: int
    signal_strength: int


T = TypeVar('T')


class SyncValue(Generic[T]):
    def __init__(self):
        self.lock = Lock()
        self.value: T = None

    def get(self) -> T:
        return self.value

    def set(self, new_value: T):
        self.lock.acquire()
        self.value = new_value
        self.lock.release()
