from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import Laser

MAP_SIZE_PIXELS = 800
MAP_SIZE_METERS = 16
SCAN_SIZE = 360


class SweepLaser(Laser):
    def __init__(self):
        Laser.__init__(self, SCAN_SIZE, 2, SCAN_SIZE, 60000)


def create_slam():
    return RMHC_SLAM(SweepLaser(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
