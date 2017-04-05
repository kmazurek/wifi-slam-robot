import ctypes
import collections

libsweep = ctypes.cdll.LoadLibrary('libsweep.so')

libsweep.sweep_get_version.restype = ctypes.c_int32
libsweep.sweep_get_version.argtypes = None

libsweep.sweep_is_abi_compatible.restype = ctypes.c_bool
libsweep.sweep_is_abi_compatible.argtypes = None

libsweep.sweep_error_message.restype = ctypes.c_char_p
libsweep.sweep_error_message.argtypes = [ctypes.c_void_p]

libsweep.sweep_error_destruct.restype = None
libsweep.sweep_error_destruct.argtypes = [ctypes.c_void_p]

libsweep.sweep_device_construct_simple.restype = ctypes.c_void_p
libsweep.sweep_device_construct_simple.argtypes = [ctypes.c_void_p]

libsweep.sweep_device_construct.restype = ctypes.c_void_p
libsweep.sweep_device_construct.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_void_p]

libsweep.sweep_device_destruct.restype = None
libsweep.sweep_device_destruct.argtypes = [ctypes.c_void_p]

libsweep.sweep_device_start_scanning.restype = None
libsweep.sweep_device_start_scanning.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

libsweep.sweep_device_stop_scanning.restype = None
libsweep.sweep_device_stop_scanning.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

libsweep.sweep_device_get_scan.restype = ctypes.c_void_p
libsweep.sweep_device_get_scan.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

libsweep.sweep_scan_destruct.restype = None
libsweep.sweep_scan_destruct.argtypes = [ctypes.c_void_p]

libsweep.sweep_scan_get_number_of_samples.restype = ctypes.c_int32
libsweep.sweep_scan_get_number_of_samples.argtypes = [ctypes.c_void_p]

libsweep.sweep_scan_get_angle.restype = ctypes.c_int32
libsweep.sweep_scan_get_angle.argtypes = [ctypes.c_void_p, ctypes.c_int32]

libsweep.sweep_scan_get_distance.restype = ctypes.c_int32
libsweep.sweep_scan_get_distance.argtypes = [ctypes.c_void_p, ctypes.c_int32]

libsweep.sweep_scan_get_signal_strength.restype = ctypes.c_int32
libsweep.sweep_scan_get_signal_strength.argtypes = [ctypes.c_void_p, ctypes.c_int32]

libsweep.sweep_device_get_motor_speed.restype = ctypes.c_int32
libsweep.sweep_device_get_motor_speed.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

libsweep.sweep_device_set_motor_speed.restype = None
libsweep.sweep_device_set_motor_speed.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_void_p]

libsweep.sweep_device_reset.restype = None
libsweep.sweep_device_reset.argtypes = [ctypes.c_void_p, ctypes.c_void_p]


def _error_to_exception(error):
    assert error
    what = libsweep.sweep_error_message(error)
    libsweep.sweep_error_destruct(error)
    return RuntimeError(what)


class Scan(collections.namedtuple('Scan', 'samples')):
    pass


class Sample(collections.namedtuple('Sample', 'angle distance signal_strength')):
    pass


class Sweep:
    def __init__(self, port = None, bitrate = None):
        self.scoped = False
        self.args = [port, bitrate]

    def __enter__(self):
        self.scoped = True
        self.device = None

        assert libsweep.sweep_is_abi_compatible(), 'Your installed libsweep is not ABI compatible with these bindings'

        error = ctypes.c_void_p();

        simple = not any(self.args)
        config = all(self.args)

        assert simple or config, 'No arguments for auto-detection or port, bitrate, required'

        if simple:
            device = libsweep.sweep_device_construct_simple(ctypes.byref(error))

        if config:
            port = ctypes.string_at(self.args[0])
            bitrate = ctypes.c_int32(self.args[1])
            device = libsweep.sweep_device_construct(port, bitrate, ctypes.byref(error))

        if error:
            raise _error_to_exception(error)

        self.device = device

        return self

    def __exit__(self, *args):
        self.scoped = False

        if self.device:
            libsweep.sweep_device_destruct(self.device)

    def _assert_scoped(self):
        assert self.scoped, 'Use the `with` statement to guarantee for deterministic resource management'

    def start_scanning(self):
        self._assert_scoped()

        error = ctypes.c_void_p();
        libsweep.sweep_device_start_scanning(self.device, ctypes.byref(error))

        if error:
            raise _error_to_exception(error)

    def stop_scanning(self):
        self._assert_scoped();

        error = ctypes.c_void_p();
        libsweep.sweep_device_stop_scanning(self.device, ctypes.byref(error))

        if error:
            raise _error_to_exception(error)

    def get_motor_speed(self):
        self._assert_scoped()

        error = ctypes.c_void_p()
        speed = libsweep.sweep_device_get_motor_speed(self.device, ctypes.byref(error))

        if error:
            raise _error_to_exception(error)

        return speed

    def set_motor_speed(self, speed):
        self._assert_scoped()

        error = ctypes.c_void_p()
        libsweep.sweep_device_set_motor_speed(self.device, speed, ctypes.byref(error))

        if error:
            raise _error_to_exception(error)

    def get_scans(self):
        self._assert_scoped()

        error = ctypes.c_void_p()

        while True:
            scan = libsweep.sweep_device_get_scan(self.device, ctypes.byref(error))

            if error:
                raise _error_to_exception(error)

            num_samples = libsweep.sweep_scan_get_number_of_samples(scan)

            samples = [Sample(angle=libsweep.sweep_scan_get_angle(scan, n),
                              distance=libsweep.sweep_scan_get_distance(scan, n),
                              signal_strength=libsweep.sweep_scan_get_signal_strength(scan, n))
                       for n in range(num_samples)]

            libsweep.sweep_scan_destruct(scan)

            yield Scan(samples=samples)

    def reset(self):
        self._assert_scoped();

        error = ctypes.c_void_p();
        libsweep.sweep_device_reset(self.device, ctypes.byref(error))

        if error:
            raise _error_to_exception(error)
