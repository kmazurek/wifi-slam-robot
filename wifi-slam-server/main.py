import argparse
import asyncio
import websockets
import json
from slam import *

CM_TO_MM = 10

parser = argparse.ArgumentParser(description='Connect to the robot and start receiving data.')
parser.add_argument('hostname')
parser.add_argument('port')
args = parser.parse_args()

slam = create_slam()


def pgm_save(filename, imgbytes, imgsize):
    print('\nSaving image to file %s' % filename)

    output = open(filename, 'wt')

    output.write('P2\n%d %d 255\n' % imgsize)

    wid, hgt = imgsize

    for y in range(hgt):
        for x in range(wid):
            output.write('%d ' % imgbytes[y * wid + x])
        output.write('\n')

    output.close()


def update_slam(scan):
    # filtered = list(filter(lambda sample: sample[1] != 1, scan))
    translated = list(map(lambda sample: sample if sample[1] != 1 else [sample[0], 0, sample[2]], scan))
    mapped = list(map(lambda sample: sample[1] * CM_TO_MM, translated))

    print(f'Received {len(mapped)} LIDAR samples . . .')
    if len(mapped) == SCAN_SIZE:
        print('Updating SLAM . . .')
        slam.update(mapped)


def adjust_scan(scan):
    scan_length = len(scan)
    scan_diff = SCAN_SIZE - scan_length
    if scan_diff == 0 or abs(scan_diff) > 5:
        return scan
    else:
        for i in range(1, abs(scan_diff)):
            if scan_diff > 0:
                scan.append(0)
            else:
                scan.pop()


def process_packet(response):
    try:
        response = json.loads(response)
        wifi_scan = response['wifi_scan']
        sweep_scan = response['sweep_scan']

        print(json.dumps(response))
        update_slam(sweep_scan)

    except ValueError:
        print("Error decoding JSON response")


async def client_loop():
    async with websockets.connect(f"ws://{args.hostname}:{args.port}") as socket:
        async for message in socket:
            process_packet(message)

try:
    asyncio.get_event_loop().run_until_complete(client_loop())
except KeyboardInterrupt:
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    slam.getmap(mapbytes)
    pgm_save('slam_map.pgm', mapbytes, (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
