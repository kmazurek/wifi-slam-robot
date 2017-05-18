from collections import namedtuple


class WifiSample(namedtuple('WifiSample', 'ssid', 'signal_strength')):
    pass


class WifiScan(namedtuple('WifiScan', 'samples')):
    pass
