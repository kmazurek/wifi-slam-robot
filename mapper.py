#!/usr/bin/python3

from wifi import Cell
import threading
import ev3dev.ev3 as ev3
import time
import socket


class ScanResult:
    def __init__(self, start=""):
        self.lock = threading.Lock()
        self.value = start

    def get_value(self):
        return self.value

    def set_value(self, new_value):
        self.lock.acquire()
        self.value = new_value
        self.lock.release()


class NetworkThread(threading.Thread):
    def __init__(self, thread_name, sock, stop_event, result):
        threading.Thread.__init__(self)
        self.udp_socket = sock
        self.stop_event = stop_event
        self.name = thread_name
        self.scan_result = result

    def run(self):
        print ("Starting %s" % self.name)

        while not self.stop_event.is_set():
            if not scan_result.get_value() == "":
                self.udp_socket.sendto(str(scan_result.get_value()).encode('utf8'), ("192.168.1.104", 8889))
                scan_result.set_value("")

        print ("Stopping %s" % self.name)


class MotorThread (threading.Thread):
    def __init__(self, thread_name, motor1, motor2, stop_event, pause_event):
        threading.Thread.__init__(self)
        self.motor1 = motor1
        self.motor2 = motor2
        self.stop_event = stop_event
        self.pause_event = pause_event
        self.name = thread_name

    def run(self):
        print ("Starting %s" % self.name)
        self.motor1.run_direct()
        self.motor2.run_direct()

        while not self.stop_event.is_set():
            if self.pause_event.is_set():
                self.motor1.duty_cycle_sp = 0
                self.motor2.duty_cycle_sp = 0
            else:
                self.motor1.duty_cycle_sp = 50
                self.motor2.duty_cycle_sp = 50

        self.motor1.stop()
        self.motor2.stop()

        print ("Exiting %s" % self.name)

def Search():
    network_list = []

    networks = Cell.all('wlan0')

    for network in networks:
        network_list.append(network)

    return network_list

if __name__ == '__main__':
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    scan_result = ScanResult()

    networkStop = threading.Event()
    networkThread = NetworkThread("network thread", udp_socket, networkStop, scan_result)
    networkThread.start()

    motorA = ev3.LargeMotor("outA")
    motorD = ev3.LargeMotor("outD")
    motorStop = threading.Event()
    motorPause = threading.Event()

    motorThread = MotorThread("motor thread", motorA, motorD, motorStop, motorPause)
    motorThread.start()

    btn = ev3.Button()

    scan_index = 0

    while not btn.any():
        time.sleep(3)

        motorPause.set()
        result = ""

        scan_index += 1
        result += "Scan number %d\n" % scan_index

        for cell in Search():
            result += cell.ssid + " " + str(cell.signal) + "\n"
            scan_result.set_value(result)

        motorPause.clear()

    networkStop.set()
    motorStop.set()
