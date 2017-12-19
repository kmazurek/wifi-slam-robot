from typing import AsyncGenerator, List
from model import SweepSample
import random

degrees_count = 360

max_distance = 4000
max_signal_strength = 255
max_value_deviation = 10

scan_base_len = 420
scan_sections = 36
scan_values = {}


def random_deviation():
    return random.randint(-max_value_deviation, max_value_deviation)


def __init_scan_values__():
    section_step = degrees_count / scan_sections
    for i in range(scan_sections):
        base_distance = random.randint(0, max_distance)
        base_signal = random.randint(0, max_signal_strength)

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
