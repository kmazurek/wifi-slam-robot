from sync import SyncValue
from threading import Thread, Event
from typing import AsyncGenerator, List
from sweeppy import Sweep

from common.model import SweepSample

sweep_motor_speed = 2
sweep_sample_rate = 750


async def sweep_scan_generator(usb_port: str) -> AsyncGenerator[List[SweepSample], None]:
    with Sweep(usb_port) as sweep:
        sweep.set_motor_speed(sweep_motor_speed)
        sweep.set_sample_rate(sweep_sample_rate)
        sweep.start_scanning()

        for item in sweep.get_scans():
            yield list(map(lambda scan: SweepSample(scan.angle, scan.distance, scan.signal_strength), item.samples))


class SweepThread(Thread):
    def __init__(self, stop_event: Event, output_value: SyncValue[List[SweepSample]], usb_port_path: str):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.name = 'Sweep thread'
        self.output_value = output_value
        self.usb_port_path = usb_port_path

    def run(self):
        print(f'Starting {self.name} . . .')

        with Sweep(self.usb_port_path) as sweep:
            sweep.set_motor_speed(sweep_motor_speed)
            sweep.set_sample_rate(sweep_sample_rate)

            print(f'Sweep motor speed: {sweep.get_motor_speed()} Hz')
            print(f'Sweep sample rate: {sweep.get_sample_rate()} Hz')

            sweep.start_scanning()

            for scan in sweep.get_scans():
                if self.stop_event.is_set():
                    break

                self.output_value.set(scan)

        print('Stopping %s . . .' % self.name)
