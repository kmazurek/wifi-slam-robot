from typing import AsyncGenerator, List
import sweeppy

from model import SweepSample

sweep_motor_speed = 3
sweep_sample_rate = 1000


async def sweep_scan_generator(usb_port: str) -> AsyncGenerator[List[SweepSample], None]:
    with sweeppy.Sweep(usb_port) as sweep:
        sweep.set_motor_speed(sweep_motor_speed)
        sweep.set_sample_rate(sweep_sample_rate)
        sweep.start_scanning()

        for item in sweep.get_scans():
            yield list(map(lambda scan: SweepSample(scan.angle, scan.distance, scan.signal_strength), item.samples))
