import argparse
import asyncio
import websockets
import json
from server.slam import *

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
    print(f'Received {len(scan)} LIDAR samples, adjusting . . .')
    adjusted = prepare_scan_for_slam(scan)
    print(f'Scan length after adjustment: {len(adjusted)}')
    if len(adjusted) == SCAN_SIZE:
        print('Updating SLAM . . .')
        slam.update(adjusted)


def prepare_scan_for_slam(scan):
    translated = list(map(lambda sample: sample if sample[1] != 1 else [sample[0], 0, sample[2]], scan))
    approximated_angles = list(map(lambda sample: (round(sample[0] / 1000), sample[1], sample[2]), translated))
    angle_dict = {}

    for sample in approximated_angles:
        if sample[0] >= 1:
            stored = angle_dict.get(sample[0])
            if stored is None or (stored is not None and sample[1] != 0):
                angle_dict[sample[0]] = sample

    unique_angles = list(angle_dict.values())

    if abs(len(unique_angles) - SCAN_SIZE) > 10:
        return []

    length_diff = len(unique_angles) - SCAN_SIZE
    if length_diff != 0:
        for i in range(abs(length_diff)):
            unique_angles.append((0, 0, 0))

    return list(map(lambda sample: sample[1] * CM_TO_MM, unique_angles))


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
