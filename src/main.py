import network.tcp_socket as tcp
import network.wifi_scanner as scanner
import sys
import threading
import time
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue

if __name__ == '__main__':
    tcpSocketStop = threading.Event()
    socketInputQueue = queue.Queue()
    tcpSocketThread = tcp.TcpSocketThread(tcpSocketStop, socketInputQueue)
    tcpSocketThread.start()

    result = ''
    try:
        while True:
            for cell in scanner.scan('wlan1'):
                result += cell.ssid + " " + str(cell.signal) + "\n"
            socketInputQueue.put(result)
            time.sleep(1)
    except KeyboardInterrupt:
        tcpSocketStop.set() # TODO Handle network exceptions?
