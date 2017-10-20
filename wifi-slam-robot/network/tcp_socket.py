import socket
import threading


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
