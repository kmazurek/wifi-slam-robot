#!/usr/bin/python3
import sys
import time
import socket
import threading
from .sweep.sweep import SweepThread
from .sweep.sweep import Buffer

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
            self.connection.send(str(data).encode('utf8'))      # TODO serialize to JSON


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


if __name__ == '__main__':
    tcpThreadStop = threading.Event()
    socketInputQueue = queue.Queue()
    tcpSocketThread = TcpSocketThread(tcpThreadStop, socketInputQueue)
    tcpSocketThread.start()

    sweepThreadStop = threading.Event()
    sweepScanBuffer = Buffer()
    sweepThread = SweepThread(sweepThreadStop, sweepScanBuffer, '/dev/ttyUSB0')
    sweepThread.start()

    scan_index = 0

    try:
        while True:
            wifi_scan_result = ''
            scan_index += 1

            for cell in scan('wlan1'):
                wifi_scan_result += cell.ssid + " " + str(cell.signal) + "\n"
            socketInputQueue.put("--- SCAN {} ---\n{}\n{}\n".format(scan_index, wifi_scan_result, str(sweepScanBuffer.get_value())))
            time.sleep(1)
    except KeyboardInterrupt:
        tcpThreadStop.set() # TODO Handle network exceptions?
        sweepThreadStop.set()
