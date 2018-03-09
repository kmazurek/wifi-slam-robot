import argparse
from model import RobotStates
from sync import SyncValue, StateMachine
from network import scan_wifi_interface
from network import send_request
from sweep import SweepThread
from sweep.mock import MockSweepThread
from time import sleep
from threading import Event
from typing import List

parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('port')
parser.add_argument('wlan_interface')
parser.add_argument('sweep_port_path')
args = parser.parse_args()


def is_scan_valid(scan: List) -> bool:
    return scan is not None and len(scan) != 0


if __name__ == '__main__':
    # TODO Add motor thread with a stop and pause flag? Or a state machine?
    state_machine = StateMachine(RobotStates, RobotStates.INITIALISING)

    sweep_stop_event = Event()
    sweep_scan_holder = SyncValue()
    sweep_thread = MockSweepThread(sweep_stop_event, sweep_scan_holder)
    sweep_thread.start()

    try:
        while True:
            # TODO Have sweep thread set a flag/state to indicate new value, only process it then?
            sweep_scan = sweep_scan_holder.get()
            wifi_scan = scan_wifi_interface(args.wlan_interface)
            if is_scan_valid(sweep_scan) and is_scan_valid(wifi_scan):
                sample = {'wifi_scan': wifi_scan, 'sweep_scan': sweep_scan}
                # TODO Store scans locally regardless of network result, create a new document for each scanning session
                # TODO Receive heading from server, store it in a sync value
                response = send_request(sample, args.hostname, args.port)
                state_machine.set_state(RobotStates.MOVING)
            sleep(1)
    except KeyboardInterrupt:
        sweep_stop_event.set()
