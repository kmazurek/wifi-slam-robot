import sweeppy
from typing import Iterable


sweep_motor_speed = 3
sweep_sample_rate = 1000


async def sweep_scan_coroutine(usb_port: str) -> Iterable[sweeppy.Scan]:
    with sweeppy.Sweep(usb_port) as sweep:
        sweep.set_motor_speed(sweep_motor_speed)
        sweep.set_sample_rate(sweep_sample_rate)
        sweep.start_scanning()

        for scan in sweep.get_scans():
            yield scan
