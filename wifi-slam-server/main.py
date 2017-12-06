import argparse
import asyncio
import websockets
import json

parser = argparse.ArgumentParser(description='Connect to the robot and start receiving data.')
parser.add_argument('hostname')
parser.add_argument('port')
args = parser.parse_args()


def print_json_response(response):
    try:
        response = json.loads(response)
        wifi_scan = response['wifi_scan']
        sweep_scan = response['sweep_scan']

        print(f'{wifi_scan}\n{sweep_scan}\n')
    except ValueError:
        print("Error decoding JSON response")


async def client_loop():
    async with websockets.connect(f"ws://{args.hostname}:{args.port}") as socket:
        async for message in socket:
            print_json_response(message)

asyncio.get_event_loop().run_until_complete(client_loop())
