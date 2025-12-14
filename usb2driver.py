__all__ = []


def __dir__():
    return []

### PLACEHOLDER, REAL CLASS EXCLUDED FROM REPO


# from threading import Thread
from multiprocessing import Value
from typing import Optional


class Mouse2Driver:
    def __init__(self, vid: int, pid: int, suppress_exceptions: bool = True, interface: int = -1,
                 mouse_log: bool = False, alternative_parser: bool = False, accumulate_movement: bool = False,
                 mouse_api: str = 'driver'):
        self.mouse_api = mouse_api
        self.VID = vid
        self.PID = pid
        self.interface = interface
        # self.mouse = Mouse()
        # self.mouse.connect()
        self._click = Value('i', 0)
        self.report_len = None
        self.alternative_parser = alternative_parser
        self.mouse_log = mouse_log
        self._endpoint = None
        self._mouse_descriptor = None
        self._started = Value('b', False)
        self._data = None
        self._process = None
        self._suppress_exceptions = suppress_exceptions
        self._x_accumulated = Value('i', 0)
        self._y_accumulated = Value('i', 0)
        self.accumulate_movement = accumulate_movement

    @property
    def click(self):
        return self._click.value

    @property
    def accumulated_move(self):
        moved = (self._x_accumulated.value, self._y_accumulated.value)
        self._x_accumulated.value = 0
        self._y_accumulated.value = 0
        return moved

    def parse_hid_report(self):

        print(f'[Mouse2Driver] [W]: Unsupported HID report byte-length ({self.report_len})')
        return 0, 0, 0, 0

    def start(self, priority: bool = False, manual_parse: bool = False, parse_dict: dict = {}) -> bool:

        print("[Mouse2Driver] [W]: Could not start. EXCLUDED FROM OPEN ENGINE")

        return False

    def stop(self):

        print("[Mouse2Driver] [W]: Could not stop. EXCLUDED FROM OPEN ENGINE")

        return True


def get_devices(backend=None) -> list[Optional[tuple[int, int]]]:

    devices = []

    return devices


def get_report_changes(vid, pid, interface, t_sec):
    changes = [0, 0, 0, 0]
    return changes


def find_xy_offsets(reports):
    xy_offsets = []

    return xy_offsets


def find_btn_offsets(reports):
    btn_offsets = []

    return btn_offsets


def find_scroll_offset(reports, xy_offsets, btn_offsets):

    return False


def xy2b(data, offset):
    return 0, 0


def xy3b(data, offset):

    return 0, 0


def xy4b(data, offset):
    return 0, 0


def scrl1b(data, offset):
    return 0


def scrl2b(data, offset):
    return 0


if __name__ == '__main__':
    VID = 0x09da
    PID = 0x5a22

    mouse = Mouse2Driver(VID, PID)

    mouse.start()
    mouse.stop()

"""

mouse = hidparser.parse(descriptor)

mouse.reports[0].inputs.mouse.pointer[0].value

array.array('B', mouse.serialize(0, hidparser.ReportType.INPUT).bytes)

"""