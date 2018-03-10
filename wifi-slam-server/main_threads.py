import argparse
import json
from gui import update_gui
from http.server import BaseHTTPRequestHandler, HTTPServer
from slam import SLAMSession
from sys import argv

parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('port')
args = parser.parse_args()

slam_session = SLAMSession()


def process_data(data):
    try:
        data = json.loads(data)
        wifi_scan = data['wifi_scan']
        sweep_scan = data['sweep_scan']

        print(json.dumps(data))
        slam_session.update_slam(sweep_scan)
        update_gui(slam_session.get_map_image())

    except ValueError:
        print("Error decoding JSON response")


class HTTPHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        process_data(post_data)

        self._set_headers()
        self.wfile.write(bytes(json.dumps({'heading':'120'}).encode('utf-8')))  # TODO Replace with actual heading


try:
    server_address = (args.hostname, int(args.port))
    httpd = HTTPServer(server_address, HTTPHandler)
    print(f'Starting server at {server_address[0]} on port {server_address[1]} . . .')
    httpd.serve_forever()
except KeyboardInterrupt:
    slam_session.save_map()
