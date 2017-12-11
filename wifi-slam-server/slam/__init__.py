from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import Laser

MAP_SIZE_PIXELS = 800
MAP_SIZE_METERS = 16
SCAN_SIZE = 355


class SweepLaser(Laser):
    def __init__(self):
        Laser.__init__(self, 355, 3, 355, 60000)


def create_slam():
    return RMHC_SLAM(SweepLaser(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
