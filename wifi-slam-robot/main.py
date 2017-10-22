#!/usr/bin/python3
import sys
import time
import socket
import sweeppy
import threading
import json

is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue

from wifi import Cell


def scan(net_interface):
    network_list = []

    networks = Cell.all(str(net_interface))

    for network in networks:
        network_list.append(network)

    return network_list


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
            sweep.set_motor_speed(3)
            sweep.set_sample_rate(1000)
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
        self.lock.acquire()
        result = self.value
        self.value = None
        self.lock.release()
        return result

    def set_value(self, new_value):
        self.lock.acquire()
        self.value = new_value
        self.lock.release()



class TcpSocket:
    def __init__(self, listen_address = '0.0.0.0', listen_port = 8889):
        self.connection = None
        self.listen_address = listen_address
        self.listen_port = listen_port

    def __enter__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return self

    def __exit__(self, *args):
        if self.connection:
            self.connection.close()
        if self.tcp_socket:
            self.tcp_socket.close()

    def listen_and_accept(self):
        print('TCP socket: Listening for incoming connections . . .')
        self.tcp_socket.bind((self.listen_address, self.listen_port))
        self.tcp_socket.listen(1)

        connection, address = self.tcp_socket.accept()
        self.connection = connection
        print('Accepted TCP connection from {}'.format(address))

    def send_data(self, data):
        if self.connection is not None:
            global scan_index
            print("Sending scan with index {} . . .".format(scan_index))
            payload = json.dumps(data)
            bytesSent = self.connection.send((payload + "\n").encode('utf8'))
            print("Bytes sent: {}".format(bytesSent))
            scan_index += 1


class TcpSocketThread(threading.Thread):
    def __init__(self, stop_event, input_queue):
        threading.Thread.__init__(self)
        self.stop_event = stop_event
        self.name = 'TCP socket thread'
        self.input_queue = input_queue

    def run(self):
        print('Starting %s . . .' % self.name)

        with TcpSocket() as socket:
            socket.listen_and_accept()

            while not self.stop_event.is_set():
                data_to_upload = self.input_queue.get()
                if data_to_upload:
                    socket.send_data(data_to_upload)

        print('Stopping %s . . .' % self.name)

scan_index = 0


if __name__ == '__main__':
    tcpThreadStop = threading.Event()
    socketInputQueue = queue.Queue()
    tcpSocketThread = TcpSocketThread(tcpThreadStop, socketInputQueue)
    tcpSocketThread.start()

    sweepThreadStop = threading.Event()
    sweepScanBuffer = Buffer()
    sweepThread = SweepThread(sweepThreadStop, sweepScanBuffer, '/dev/ttyUSB0')
    sweepThread.start()

    try:
        while True:
            wifi_scan_result = []


            # for cell in scan('wlan1'):
            #     wifi_scan_result.append((cell.ssid, cell.signal))
            # socketInputQueue.put(json.dumps(wifi_scan_result))

            scan = sweepScanBuffer.get_value()
            if scan:
                socketInputQueue.put(scan)

            time.sleep(2)
    except KeyboardInterrupt:
        tcpThreadStop.set() # TODO Handle network exceptions?
        sweepThreadStop.set()
