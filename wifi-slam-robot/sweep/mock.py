from model import SweepSample
from random import randint
from sync import SyncValue
from time import sleep
from threading import Thread, Event
from typing import AsyncGenerator, List

degrees_count = 360

max_distance = 4000
max_signal_strength = 255
max_value_deviation = 10

scan_base_len = 420
scan_sections = 36
scan_values = {}


def random_deviation():
    return randint(-max_value_deviation, max_value_deviation)


def __init_scan_values__():
    section_step = degrees_count / scan_sections
    for i in range(scan_sections):
        base_distance = randint(0, max_distance)
        base_signal = randint(0, max_signal_strength)

        start = round(i * section_step)
        end = round(start + section_step)

        for j in range(start, end):
            distance = base_distance + random_deviation()
            signal = base_signal + random_deviation()
            scan_values[j] = (distance, signal)


def __generate_scan__():
    mock_scan = []

    scan_len = scan_base_len + random_deviation()
    step = degrees_count / scan_len
    for i in range(scan_len):
        angle = round(i * step)
        values = scan_values[round(angle)]
        mock_scan.append(SweepSample(angle * 1000, values[0], values[1]))

    return mock_scan


async def mock_scan_generator() -> AsyncGenerator[List[SweepSample], None]:
    __init_scan_values__()

    while True:
        yield __generate_scan__()


class MockSweepThread(Thread):
    def __init__(self, stop_event: Event, output_value: SyncValue[List[SweepSample]]):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.name = 'Mock Sweep thread'
        self.output_value = output_value

    def run(self):
        print(f'Starting {self.name} . . .')
        __init_scan_values__()

        while not self.stop_event.is_set():
            self.output_value.set(__generate_scan__())
            sleep(1)

        print('Stopping %s . . .' % self.name)
