__all__ = []


def __dir__():
    return []


from os import path
from interval_timer import IntervalTimer
from ctypes import windll, c_long, c_ulong, Structure, Union, c_int, POINTER, sizeof, c_ushort, c_byte, CDLL
from threading import Thread
from struct import pack, unpack
import socket
import time



LONG = c_long
DWORD = c_ulong
ULONG_PTR = POINTER(DWORD)


class MOUSEINPUT(Structure):
    _fields_ = (('dx', LONG),
                ('dy', LONG),
                ('mouseData', DWORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))


class _INPUTunion(Union):
    _fields_ = (('mi', MOUSEINPUT), ('mi', MOUSEINPUT))


class INPUT(Structure):
    _fields_ = (('type', DWORD),
                ('union', _INPUTunion))


def SendInput(*inputs):
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = c_int(sizeof(INPUT))
    return windll.user32.SendInput(nInputs, pInputs, cbSize)


def Input(structure):
    return INPUT(0, _INPUTunion(mi=structure))


def MouseInput(flags, x, y, data):
    return MOUSEINPUT(x, y, data, flags, 0, None)


def MouseRep(flags, x=0, y=0, data=0):
    return Input(MouseInput(flags, x, y, data))


def mouse_xy(x, y):
    return SendInput(MouseRep(0x0001, x, y))


def mouse_down(key=1):
    if key == 1:
        return SendInput(MouseRep(0x0002))
    elif key == 2:
        return SendInput(MouseRep(0x0008))


def mouse_up(key=1):
    if key == 1:
        return SendInput(MouseRep(0x0004))
    elif key == 2:
        return SendInput(MouseRep(0x0010))


class Mouse:
    def __init__(self, default_api: str = 'driver', flush_time: float = 0.2):
        """
        Relative flag:  0x04
        Absolute flag:  0x09
        LeftM flag:     0x01
        RightM flag:    0x02
        MiddleM flag:   0x04
        ReleaseM flag:  0x00
        """

        self._movement_mode = {
            'abs': (0x09, 10, c_ushort),
            'rel': (0x04, 7, c_byte)
        }

        self._mouse_button = {
            'left': 0x01,
            'right': 0x02,
            'middle': 0x04,
            'left_up': 0x01,
            'right_up': 0x02,
            'middle_up': 0x04
        }

        self._interception_button = {
            'left': 0x10,
            'right': 0x11,
            'middle': 0x12,
            'left_up': 0x00,
            'right_up': 0x01,
            'middle_up': 0x02
        }

        self.RelMovementApis = {
            'rdriver': self.RDriverMoveR,
            'driver': self.DriverMoveR,
            'stm32': self.STM32MoveR,
            'ghub': self.GHubMoveR,
            'user32': self.User32MoveR,
            'proxy': self.ProxyMoveR,
            'interception': self.InterceptionMoveR
        }

        self.MBtnApis = {
            'rdriver': self.RDriverBtnEvent,
            'driver': self.DriverBtnEvent,
            'stm32': self.STM32BtnEvent,
            'ghub': self.GHubBtnEvent,
            'user32': self.User32BtnEvent,
            'proxy': self.ProxyBtnEvent,
            'interception': self.InterceptionBtnEvent
        }

        self._default_api = default_api

        self._driver = None
        self._driver_opened = False

        self._rdriver = None
        self._rdriver_opened = False
        self._rdriver_keepalive = 30
        self._rdriver_ka_time = 0

        self._ghub = None
        self._ghub_opened = False

        self._proxy = None
        self._proxy_opened = False

        self._interception = None
        self._interception_id = 0
        self._interception_opened = False

        self._stm32 = None
        self._stm32_secret = 0x11111111
        self._stm32_opened = False

        self._user32 = False

        self.connected = False

        self._error_x = 0
        self._error_y = 0
        self._current_btns = 0
        self._move_btns = 0

        self.flush_time = flush_time

        self._flush_thread = None

    @staticmethod
    def _clamp(value, min_value, max_value):
        return max(min(value, max_value), min_value)
    
    @staticmethod
    def _filter_kwargs(kwargs, allowed_keys):
        return {k: v for k, v in kwargs.items() if k in allowed_keys}

    def Flush(self):
        self._error_x = 0
        self._error_y = 0
        return True

    def _flush_target(self):
        while self.connected:
            time.sleep(self.flush_time)
            self.Flush()
    
    def _connect_interception(self, vid, pid):

        if self._interception_opened:
            return True
        
        try:
            import clr
            clr.AddReference(path.abspath('interception_api.dll'))
            import AutoHotInterception
        except:
            print("[Mouse] [F]: An error has occcured while trying to load interception dll's. Maybe they're locked?")
            exit()
        
        self._interception = AutoHotInterception.Manager()
        self._interception_opened = 'OK' == self._interception.OkCheck()
        self._interception_id = self._interception.GetMouseId(vid, pid)
        self._interception_opened = self._interception_opened and self._interception_id != 0

        return self._interception_opened
    
    def _close_interception(self):
        if not self._interception_opened:
            return False

        del self._interception
        self._interception = None
        self._interception_opened = False

        return True

    def _connect_driver(self):
        print(f'[F] [Mouse] Driver api error: EXCLUDED')
        return False

    def _connect_rdriver(self):
        print(f'[F] [Mouse] RDriver api error: EXCLUDED')
        return False
    
    def _close_rdriver(self):
        print(f'[F] [Mouse] RDriver api error: EXCLUDED')
        return False

    def _close_driver(self):
        print(f'[F] [Mouse] Driver api error: EXCLUDED')
        return False

    def _connect_ghub(self):

        if self._ghub_opened:
            return True

        basedir = path.dirname(path.abspath(__file__))
        ghub_dll = path.join(basedir, 'ghub_mouse.dll')

        self._ghub = CDLL(ghub_dll)

        self._ghub_opened = self._ghub.mouse_open()
        return self._ghub_opened

    def _close_ghub(self):

        if not self._ghub_opened:
            return False

        self._ghub.mouse_close()
        self._ghub_opened = False

        return True

    def _connect_proxy(self, c_ip: str, l_ip: str, l_port: int, extra_port: int = 1):

        if self._proxy_opened:
            return True

        self._proxy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._proxy.bind((c_ip, l_port + extra_port))

        self._proxy_addr = (l_ip, l_port)

        self._proxy_opened = True

        return self._proxy_opened

    def _close_proxy(self):

        if not self._proxy_opened:
            return False

        self._proxy.close()
        self._proxy_opened = False

        return True
    
    def _connect_stm32(self, vid=None, pid=None, col=0):
        print(f'[F] [Mouse] STM32 api error: EXCLUDED')
        return False
    
    def _close_stm32(self):
        print(f'[F] [Mouse] STM32 api error: EXCLUDED')
        return False

        

    # def connect(self, api=None, c_ip: str = None, l_ip: str = None, l_port: int = None, extra_port: int = 1):
    def connect(self, *args, api=None, **kwargs):
        if not api:
            api = self._default_api
        match api:
            case 'rdriver':
                self.connected = self._connect_rdriver()
            case 'driver':
                self.connected = self._connect_driver()
            case 'stm32':
                try:
                    self.connected = self._connect_stm32(*args, **self._filter_kwargs(kwargs, ['vid', 'pid', 'col']))
                except:
                    print('[Mouse] [F]: Failed to connect to LunarSTM32')
                    self.connected = False
            case 'proxy':
                # if c_ip and l_ip and l_port:
                #     self.connected = self._connect_proxy(c_ip, l_ip, l_port, extra_port)
                # else:
                #     self.connected = False
                try:
                    self.connected = self._connect_proxy(*args, **self._filter_kwargs(kwargs, ['c_ip', 'l_ip', 'l_port', 'extra_port']))
                except:
                    print('[Mouse] [F]: Failed to connect to proxy')
                    self.connected = False
            case 'interception':
                try:
                    self.connected = self._connect_interception(*args, **kwargs)
                except:
                    print('[Mouse] [F]: Failed to connect to interception')
                    self.connected = False
            case 'ghub':
                self.connected = self._connect_ghub()
            case 'user32':
                self._user32 = True
                self.connected = True
        if self.connected:
            if self._flush_thread is not None:
                if not self._flush_thread.is_alive():
                    self._flush_thread = Thread(target=self._flush_target, args=tuple(self))
                    self._flush_thread.start()
        if not self.connected:
            print(f"[Main] [W]: Used mouse API '{api}' doesn't work!")
        return self.connected

    def close(self):
        user32_opened = self._user32
        self._user32 = False
        self.connected = False

        if self._flush_thread is not None:
            if self._flush_thread.is_alive():
                self._flush_thread.join()

        return self._close_rdriver() or self._close_driver() or self._close_proxy() or self._close_ghub() or self._close_interception() or self._close_stm32() or user32_opened

    def MoveR(self, x, y, api=None, btn_flag=0, scroll_byte=0, optimize: bool = False):
        self._move_btns = btn_flag
        btn_flag ^= self._current_btns
        # print(btn_flag, self._move_btns)
        if api:
            if api not in self.RelMovementApis:
                return self.User32MoveR(x, y, optimize=optimize)
            elif api == 'rdriver':
                return self.RDriverMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
            elif api == 'driver':
                return self.DriverMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
            elif api == 'stm32':
                return self.STM32MoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
            elif api == 'proxy':
                return self.ProxyMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
            elif api == 'interception':
                return self.InterceptionMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
            return self.RelMovementApis[api](x, y)

        if self._rdriver_opened:
            return self.RDriverMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
        elif self._driver_opened:
            return self.DriverMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
        elif self._stm32_opened:
            return self.STM32MoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
        elif self._proxy_opened:
            return self.ProxyMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
        elif self._interception_opened:
            return self.InterceptionMoveR(x, y, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)
        elif self._ghub_opened:
            return self.GHubMoveR(x, y, optimize=optimize)
        elif self._user32:
            return self.User32MoveR(x, y, optimize=optimize)

    def User32MoveR(self, x, y, optimize: bool = False):

        if not self._user32:
            return False

        x1, y1 = x + self._error_x, y + self._error_y

        self._error_x = x1 % -1 if x1 < 0 else x1 % 1
        self._error_y = y1 % -1 if y1 < 0 else y1 % 1

        if optimize and int(x1) == int(y1) == 0:
            return True

        mouse_xy(int(x1), int(y1))
        return True

    def GHubMoveR(self, x, y, optimize: bool = False):

        if not self._ghub_opened:
            return False

        x1, y1 = x + self._error_x, y + self._error_y

        self._error_x = x1 % -1 if x1 < 0 else x1 % 1
        self._error_y = y1 % -1 if y1 < 0 else y1 % 1

        if optimize and int(x1) == int(y1) == 0:
            return True

        self._ghub.moveR(int(x1), int(y1))
        return True
    
    def InterceptionMoveR(self, x, y, btn_flag: int = 0, scroll_byte: int = 0, optimize: bool = False):

        if not self._interception_opened:
            return False
        
        x1, y1 = x + self._error_x, y + self._error_y

        self._error_x = x1 % -1 if x1 < 0 else x1 % 1
        self._error_y = y1 % -1 if y1 < 0 else y1 % 1

        if optimize and int(x1) == int(y1) == 0:
            return True

        self._interception.SendMouseMoveRelative(self._interception_id, int(x1), int(y1))
        return True
    
    def STM32MoveR(self, x, y, btn_flag: int = 0, scroll_byte: int = 0, optimize: bool = False):
        print(f'[F] [Mouse] STM32 api error: EXCLUDED')
        return False
    
    # def ProxyMoveR(self, x, y, btn_flag: int = 0, scroll_byte: int = 0):

    #     if not self._proxy_opened:
    #         return False

    #     x1, y1, scroll1 = x + self._error_x, y + self._error_y, scroll_byte
    #     while abs(x1) > 32767 or abs(y1) > 32767 or abs(scroll1) > 127:
    #         x2 = self._clamp(x1, -32768, 32767)
    #         y2 = self._clamp(y1, -32768, 32767)
    #         scroll2 = self._clamp(scroll1, -128, 127)
    #         self._proxy.sendto(pack('B', btn_flag) + pack('hh', int(x2), int(y2)) + pack('b', scroll2), self._proxy_addr)
    #         x1 -= x2
    #         y1 -= y2
    #         scroll1 -= scroll2

    #     self._error_x = x1 % -1 if x1 < 0 else x1 % 1
    #     self._error_y = y1 % -1 if y1 < 0 else y1 % 1
    #     self._proxy.sendto(pack('B', btn_flag) + pack('hh', int(x1), int(y1)) + pack('b', scroll1), self._proxy_addr)
    #     return True

        # struct.pack('B', 1) + struct.pack('hh', -32768, 32767) + struct.pack('b', 127)
    
    def ProxyMoveR(self, x, y, btn_flag: int = 0, scroll_byte: int = 0, optimize: bool = False):
        # if not self._proxy_opened:
        #     return False
        # dx = int(x)
        # dy = int(y)

        # dx = self._clamp(dx, -127, 127)
        # dy = self._clamp(dy, -127, 127)

        # dx_byte = dx & 0xFF
        # dy_byte = dy & 0xFF

        # command = [0x01, dx_byte, dy_byte] + [0] * 2
        # self._proxy.write(bytes(command))

        # return True
        if not self._proxy_opened:
            return False

        x1, y1, scroll1 = x + self._error_x, y + self._error_y, scroll_byte
        while abs(x1) > 32767 or abs(y1) > 32767 or abs(scroll1) > 127:
            x2 = self._clamp(x1, -32768, 32767)
            y2 = self._clamp(y1, -32768, 32767)
            scroll2 = self._clamp(scroll1, -128, 127)
            self._proxy.sendto(pack('B', btn_flag) + pack('hh', int(x2), int(y2)) + pack('b', scroll2), self._proxy_addr)
            x1 -= x2
            y1 -= y2
            scroll1 -= scroll2

        self._error_x = x1 % -1 if x1 < 0 else x1 % 1
        self._error_y = y1 % -1 if y1 < 0 else y1 % 1

        if optimize and int(x1) == int(y1) == 0:
            return True

        self._proxy.sendto(pack('B', btn_flag) + pack('hh', int(x1), int(y1)) + pack('b', scroll1), self._proxy_addr)
        return True

    def DriverMoveR(self, x, y, btn_flag=0, scroll_byte=0, div_time=0.0002, optimize: bool = False):
        print(f'[F] [Mouse] Driver api error: EXCLUDED')
        return False
    
    def RDriverMoveR(self, x, y, btn_flag=0, scroll_byte=0, div_time=0.0002, optimize: bool = False):
        print(f'[F] [Mouse] RDriver api error: EXCLUDED')
        return False
    
    def DriverMoveRA(self, x, y, width=1920, height=1080, btn_flag=0, scroll_byte=0):
        print(f'[F] [Mouse] Driver api error: EXCLUDED')
        return False
    
    def RDriverMoveRA(self, x, y, width=1920, height=1080, btn_flag=0, scroll_byte=0):
        print(f'[F] [Mouse] RDriver api error: EXCLUDED')
        return False

    def DriverMoveA(self, x, y, width=1920, height=1080, btn_flag=0, scroll_byte=0):
        print(f'[F] [Mouse] Driver api error: EXCLUDED')
        return False
    
    def RDriverMoveA(self, x, y, width=1920, height=1080, btn_flag=0, scroll_byte=0):
        print(f'[F] [Mouse] RDriver api error: EXCLUDED')
        return False

    def MoveRInterpolated(self, rx, ry, duration: float, refresh_rate: int = 1000, api=None, btn_flag=0, scroll_byte=0, optimize: bool = False):

        steps: int = int(duration * refresh_rate)

        if steps == 0:
            return self.MoveR(rx, ry, api=api, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)

        step_time: float = duration / steps

        pps_x: float = rx / steps
        pps_y: float = ry / steps

        for _ in IntervalTimer(step_time, stop=steps):
            self.MoveR(pps_x, pps_y, api=api, btn_flag=btn_flag, scroll_byte=scroll_byte, optimize=optimize)

        return True

    def DriverBtnEvent(self, button='left', btns_pressed=0):
        print(f'[F] [Mouse] Driver api error: EXCLUDED')
        return False
    
    def RDriverBtnEvent(self, button='left', btns_pressed=0):
        print(f'[F] [Mouse] RDriver api error: EXCLUDED')
        return False
    
    def InterceptionBtnEvent(self, button='left', btns_pressed=0):

        if not self._interception_opened:
            return False

        if button not in self._interception_button:
            for i in range(8):
                self._interception.SendMouseButtonEvent(self._interception_id, i, (button >> i) % 2)
            return True

        self._interception.SendMouseButtonEvent(self._interception_id, self._interception_button[button] % 2, self._interception_button[button] >> 1)

        return True
    
    def STM32BtnEvent(self, button='left', btns_pressed=0):
        print(f'[F] [Mouse] STM32 api error: EXCLUDED')
        return False

    def ProxyBtnEvent(self, button='left', btns_pressed=0):

        # if not self._proxy_opened:
        #     return False

        

        # # self._proxy.sendto(pack('B', self._move_btns ^ self._current_btns ^ btns_pressed) + pack('hh', 0, 0) + pack('b', 0), self._proxy_addr)

        # return True
        if not self._proxy_opened:
            return False
        
        if button not in self._mouse_button:
            self._current_btns ^= button
        else:
            self._current_btns ^= self._mouse_button[button]

        # if button not in self._mouse_button:
        #     self._proxy.sendto(pack('B', self._move_btns ^ self._current_btns ^ btns_pressed) + pack('hh', 0, 0) + pack('b', 0), self._proxy_addr)
        #     return True

        self._proxy.sendto(pack('B', self._move_btns ^ self._current_btns ^ btns_pressed) + pack('hh', 0, 0) + pack('b', 0), self._proxy_addr)

        return True

    def BtnEvent(self, button='left', api=None, btns_pressed=0):
        if api:
            if api not in self.MBtnApis:
                return self.User32BtnEvent(button)
            return self.MBtnApis[api](button, btns_pressed=btns_pressed)

        if self._rdriver_opened:
            return self.RDriverBtnEvent(button, btns_pressed=btns_pressed)
        elif self._driver_opened:
            return self.DriverBtnEvent(button, btns_pressed=btns_pressed)
        elif self._stm32_opened:
            return self.STM32BtnEvent(button, btns_pressed=btns_pressed)
        elif self._proxy_opened:
            return self.ProxyBtnEvent(button, btns_pressed=btns_pressed)
        elif self._interception_opened:
            return self.InterceptionBtnEvent(button)
        elif self._ghub_opened:
            return self.GHubBtnEvent(button)
        elif self._user32:
            return self.User32BtnEvent(button)

    def User32BtnEvent(self, button):

        if button not in self._mouse_button:
            return False

        if not self._user32:
            return False

        if button == 'left':
            mouse_down(1)
        elif button == 'right':
            mouse_down(2)
        elif button == 'left_up':
            mouse_up(1)
        elif button == 'right_up':
            mouse_up(2)
        else:
            return False

        return True

    def GHubBtnEvent(self, button):

        if button not in self._mouse_button:
            return False

        if not self._ghub_opened:
            return False

        if button == 'left':
            self._ghub.press(1)
        elif button == 'right':
            self._ghub.press(2)
        elif button == 'left_up':
            self._ghub.release()
        elif button == 'right_up':
            self._ghub.release()
        else:
            return False

        return True
