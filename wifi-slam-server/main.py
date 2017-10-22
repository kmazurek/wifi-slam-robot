import socket
import sys
import json
from breezyslam.components import Laser

MAP_SIZE_PIXELS = 800
MAP_SIZE_METERS = 32


def print_json_response(response):
    global response_index
    try:
        print(json.loads(response))
        print("Received response with index {}".format(response_index))
        response_index += 1
    except ValueError:
        print("Error decoding JSON response")


class SweepLaser(Laser):
    def __init__(self):
        Laser.__init__(self, 355, 3, 355, 60000)

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect(("192.168.0.192", 8889))

response_index = 0
response_buffer = ""

try:
    while True:
        response = tcp_socket.recv(8192)
        print("Response length: {}".format(len(response)))

        if not response:
            continue

        decoded_response = response.decode('utf-8')

        for char in decoded_response:
            if char == '\n':
                print_json_response(response_buffer)
                response_buffer = ""
            else:
                response_buffer += char


except KeyboardInterrupt:
    tcp_socket.close()
    sys.exit(0)
