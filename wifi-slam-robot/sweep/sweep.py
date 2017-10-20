import sweeppy
import threading


class SweepThread(threading.Thread):
    def __init__(self, stop_event, output_buffer, usb_port_path):
        threading.Thread.__init__(self)
        self.stop_event = stop_event
        self.name = 'Sweep thread'
        self.output_buffer = output_buffer
        self.usb_port_path = usb_port_path

    def run(self):
        print('Starting %s . . .' % self.name)

        with sweeppy.Sweep(self.usb_port_path) as sweep:
            speed = sweep.get_motor_speed()
            rate = sweep.get_sample_rate()

            print('Motor Speed: {} Hz'.format(speed))
            print('Sample Rate: {} Hz'.format(rate))

            sweep.start_scanning()

            for scan in sweep.get_scans():
                self.output_buffer.set_value(scan)

        print('Stopping %s . . .' % self.name)


class Buffer:
    def __init__(self):
        self.lock = threading.Lock()
        self.value = None

    def get_value(self):
        return self.value

    def set_value(self, new_value):
        self.lock.acquire()
        self.value = new_value
        self.lock.release()
