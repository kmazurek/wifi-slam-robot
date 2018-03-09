from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import Laser
from PIL import Image

CM_TO_MM = 10
MAP_SIZE_PIXELS = 800
MAP_SIZE_METERS = 16
SCAN_SIZE = 360


class SweepLaser(Laser):
    def __init__(self):
        Laser.__init__(self, SCAN_SIZE, 2, SCAN_SIZE, 60000)


class SLAMSession:
    # TODO Store robot coordinates (trajectory)
    def __init__(self):
        self.slam = RMHC_SLAM(SweepLaser(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
        self.map_image_bytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

    def get_map(self):
        self.slam.getmap(self.map_image_bytes)
        return self.map_image_bytes

    def save_map(self, file_path='slam_map.png'):
        self.slam.getmap(self.map_image_bytes)
        image = Image.frombuffer('L', (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), self.map_image_bytes, 'raw', 'L', 0, 1)
        print(f'Saving map image to {file_path}')
        image.save(file_path)

    def update_slam(self, scan):
        processed_scan = self.__process_scan__(scan)
        if len(processed_scan) == SCAN_SIZE:
            print('Updating SLAM . . .')
            self.slam.update(processed_scan)

    def __process_scan__(self, scan):
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
