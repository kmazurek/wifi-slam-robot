from typing import AsyncGenerator
import sweeppy


sweep_motor_speed = 3
sweep_sample_rate = 1000


async def sweep_scan_generator(usb_port: str) -> AsyncGenerator[sweeppy.Scan, None]:
    with sweeppy.Sweep(usb_port) as sweep:
        sweep.set_motor_speed(sweep_motor_speed)
        sweep.set_sample_rate(sweep_sample_rate)
        sweep.start_scanning()

        for scan in sweep.get_scans():
            yield scan
