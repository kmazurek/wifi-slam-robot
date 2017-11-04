from breezyslam.components import Laser

MAP_SIZE_PIXELS = 800
MAP_SIZE_METERS = 32

class SweepLaser(Laser):
    def __init__(self):
        Laser.__init__(self, 355, 3, 355, 60000)