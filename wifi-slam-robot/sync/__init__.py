from typing import TypeVar, Generic
from threading import Lock

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


class StateMachine:
    def __init__(self, state_class, initial_state):
        self.lock = Lock()
        self.states = state_class
        self.current_state = initial_state

    def get_state(self):
        return self.current_state

    def set_state(self, new_state):
        if new_state != self.get_state():
            for state in self.states:
                if state == new_state:
                    self.lock.acquire()
                    self.current_state = new_state
                    self.lock.release()
