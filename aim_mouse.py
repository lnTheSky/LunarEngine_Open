__all__ = []


def __dir__():
    return []


from multiprocessing import Process, Value, shared_memory, Condition, Queue
from interval_timer import IntervalTimer
from hook_manager import HookManager
from hid_utils import num2buttons
from core_utils import Settings
from _winapi import Overlapped
from threading import Thread
from simple_pid import PID
from mouse import Mouse
from aim import aim
import numpy as np
import random
import pickle
import socket
import time


class FilteredPID(PID):
    def __init__(self, *args, filter_coeff=0.9, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_derivative = 0
        self.filter_coeff = filter_coeff

    def compute(self, input_value):
        # Стандартный расчет
        control_signal = super().compute(input_value)

        # Фильтрация дифференциальной составляющей
        derivative = self._last_output - self.previous_derivative
        derivative = self.filter_coeff * derivative + (1 - self.filter_coeff) * self.previous_derivative
        self.previous_derivative = derivative

        return control_signal


class AimMouse:
    def __init__(self, settings: Settings, hook_manager: HookManager, m2v=None, aim_hz: int = 1000):
        self._started = False
        self._process = None

        self.aim_hz = aim_hz

        self.settings = settings
        self._queue = Queue()
        self._m2v_click = m2v
        self._m2v_x_acc = m2v
        self._m2v_y_acc = m2v
        if m2v:
            self._m2v_click = m2v._click
            self._m2v_x_acc = m2v._x_accumulated
            self._m2v_y_acc = m2v._y_accumulated
        self._aim_enabled = hook_manager._aim_enabled
        self._lock_mode = hook_manager._lock_mode
        self._lock_hold = hook_manager._lock_hold
        self._lock_toggled = hook_manager._lock_toggled
        self._macro = hook_manager._macro
        self._smoothness = hook_manager._smoothness
        self._dynamic_height = hook_manager._dynamic_height
        self._use_pid = hook_manager._use_pid
        # self._lock = Lock()

        self._exit = Value('b', False)

    @staticmethod
    # def _target(s, targets_mname, cond, m2v_click, aim_enabled, lock_mode, lock_hold, lock_toggled, rcs, smoothness,
    #             dynamic_height, use_pid, exit_val, aim_hz, m2v_x, m2v_y):
    def _target(s, targets_queue, m2v_click, aim_enabled, lock_mode, lock_hold, lock_toggled, rcs, smoothness,
                dynamic_height, use_pid, exit_val, aim_hz, m2v_x, m2v_y):
        # targets_mem = shared_memory.SharedMemory(name=targets_mname)

        aims = []
        thread_started = True
        al_x, al_y = 0, 0
        m_x, m_y = 0, 0

        pidx = FilteredPID(s.pidx_k, s.pidx_i, s.pidx_d)
        pidy = FilteredPID(s.pidy_k, s.pidy_i, s.pidy_d)

        pidx.output_limits = (-16364, 16364)
        pidy.output_limits = (-16364, 16364)

        flick_triggered = not s.flick_aim

        macro_time = 0
        hold_time = 0
        start_time = 0
        reset_start_time = None

        # =========================MACRO PARSE===========================
        time_ms = 0
        relative_x = 0
        relative_y = 0
        macro = [[0, 0, 0]]

        max_retraction_time = 0
        max_hold_time = 0.5

        with open('ak47.txt', 'r') as file:
            for line in file:
                line = line.split()

                if len(line) == 0:
                    continue

                match line[0]:
                    case 'Delay':
                        time_ms += int(line[1])
                    case 'MoveR':
                        relative_x -= int(line[1])
                        relative_y -= int(line[2])
                        macro.append([time_ms, relative_x, relative_y])
                    case 'Sensitivity':
                        s.macro_divide = float(line[1])
                    case 'RetractionTime':
                        max_retraction_time = float(line[1])
                    case 'RetractionStart':
                        max_hold_time = float(line[1])

        macro = np.array(macro)

        del time_ms, relative_x, relative_y

        # ===============================================================

        mouse = Mouse()

        if s.mouse_driver == 'proxy' and s.mouse_proxy_manual:
            print('[Aim] [I]: Trying auto-connect to LunarBox')
            mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            mouse_socket.connect((s.mouse_l_ip, s.mouse_l_port))
            s.mouse_c_ip = mouse_socket.getsockname()[0]
            mouse_socket.close()

        if s.mouse_driver == 'interception':
            mouse_info = list(map(int, s.mouse_device.split()))
            vid, pid = mouse_info[0], mouse_info[1]
            if not mouse.connect(vid, pid, api=s.mouse_driver):
                print(f"[Main] [W]: Used mouse API '{s.mouse_driver}' doesn't work!")
        
        ##########################################################################################################
        
        # elif not mouse.connect(api='stm32', vid=0x09da, pid=0x5a24, col=1):
        elif not mouse.connect(api=s.mouse_driver, c_ip=s.mouse_c_ip, l_ip=s.mouse_l_ip, l_port=s.mouse_l_port, extra_port=2):
            print(f"[Aim] [W]: Used mouse API '{s.mouse_driver}' doesn't work!")
        ##########################################################################################################

        def get_aims_target():
            nonlocal aims, al_x, al_y
            while thread_started:
                try:
                    aims = targets_queue.get(timeout=0.2).copy()

                    
                    if type(aims) == Overlapped:
                        aims = []
                        print('[Aim Mouse] [W]: Handled _winapi.Overlapped object')
                    for target in aims:
                        if type(target) != list:
                            aims = []
                            print('[Aim Mouse] [W]: Handled _winapi.Overlapped or smth object')
                            break
                    # cond.wait()
                    # data = bytes(targets_mem.buf[:targets_mem.size])
                    # aims = pickle.loads(data)

                    al_x, al_y = 0, 0
                    # print(aims)
                except Exception as e:
                    # print(type(boxes))
                    aims = []
                # with cond:
                #     try:
                #         # aims = targets_queue.get(timeout=0.2).copy()

                        
                #         # if type(aims) == Overlapped:
                #         #     aims = []
                #         #     print('[Aim Mouse] [W]: Handled _winapi.Overlapped object')
                #         # for target in aims:
                #         #     if type(target) != list:
                #         #         aims = []
                #         #         print('[Aim Mouse] [W]: Handled _winapi.Overlapped or smth object')
                #         #         break
                #         cond.wait()
                #         data = bytes(targets_mem.buf[:targets_mem.size])
                #         aims = pickle.loads(data)

                #         al_x, al_y = 0, 0
                #         # print(aims)
                #     except Exception as e:
                #         # print(type(boxes))
                #         aims = []

        aims_thread = Thread(target=get_aims_target)
        aims_thread.start()

        print("[Aim] [I]: Successfully started")

        exit_val.value = True
        while exit_val.value:
            time.sleep(0.1)

        for _ in IntervalTimer(1/aim_hz):
            if bool(exit_val.value):
                break

            x_acc, y_acc = 0, 0

            if s.mouse2driver_translate:
                # print(m2v_click.value)
                locked = m2v_click.value & 1 and bool(aim_enabled.value)
            else:
                # print(s.mouse2driver_translate)
                locked = bool(lock_mode.value)

            if locked or bool(lock_toggled.value) or bool(lock_hold.value):
                # print('Locked')
                try:
                    if len(aims) == 0:
                        m_x, m_y = 0, 0
                        pidx.reset()
                        pidy.reset()
                        flick_triggered = not s.flick_aim
                        continue
                except TypeError:
                    print('[Aim Mouse] [W]: TypeError handled. May be _winapi.Overlapped')
                    m_x, m_y = 0, 0
                    pidx.reset()
                    pidy.reset()
                    flick_triggered = not s.flick_aim
                    continue
                except Exception as e:
                    print(f'[Aim Mouse] [F]: Unknown exception handled. {e}')
                    m_x, m_y = 0, 0
                    pidx.reset()
                    pidy.reset()
                    flick_triggered = not s.flick_aim
                    continue

                if rcs.value:
                    if not locked:
                        if reset_start_time is None:
                            reset_start_time = time.time()
                            reset_duration = (hold_time / max_hold_time) * max_retraction_time
                        elapsed_reset_time = time.time() - reset_start_time
                        if elapsed_reset_time < reset_duration:
                            macro_time = max(0, hold_time * (1 - elapsed_reset_time / reset_duration))
                        else:
                            macro_time = 0
                    else:
                        if macro_time == 0:
                            start_time = time.time()
                        if reset_start_time:
                            start_time = time.time() - macro_time
                        macro_time = max(time.time() - start_time, 0.0001)
                        hold_time = min(macro_time, max_hold_time)
                        reset_start_time = None

                    macro_ms = macro_time * 1000
                    difference = abs(macro[:, 0] - macro_ms)
                    macro_x, macro_y = macro[difference == difference.min()][0, 1:] / s.macro_divide
                else:
                    macro_x, macro_y = 0, 0

                if s.mouse2driver_translate and s.accumulate_mouse_movement:
                    x_acc = m2v_x.value
                    y_acc = m2v_y.value

                try:
                    m_x, m_y, move, a_x, a_y = aim(aims, al_x=al_x, al_y=al_y, smooth=smoothness.value, settings=s,
                                                   macro_x=macro_x, macro_y=macro_y, flick=not flick_triggered,
                                                   d_height=bool(dynamic_height.value), acc_x=x_acc, acc_y=y_acc)
                except TypeError:
                    print('[Aim Mouse] [W]: TypeError handled. May be _winapi.Overlapped')
                    m_x, m_y = 0, 0
                    pidx.reset()
                    pidy.reset()
                    flick_triggered = not s.flick_aim
                    continue
                except Exception as e:
                    print(f'[Aim Mouse] [F]: Unknown exception handled. {e}')
                    m_x, m_y = 0, 0
                    pidx.reset()
                    pidy.reset()
                    flick_triggered = not s.flick_aim
                    continue
                if s.mouse2driver_translate and s.accumulate_mouse_movement:
                    m2v_x.value = 0
                    m2v_y.value = 0
                # print('Angles get')

                if move:
                    if use_pid.value and flick_triggered:
                        nm_x = -pidx(m_x)
                        nm_y = -pidy(m_y)
                    else:
                        nm_x, nm_y = m_x, m_y
                    
                    ################################################################
                    # if -1 < nm_x < 1 and -1 < nm_y < 1:
                    #     if not flick_triggered:
                    #         flick_triggered = True
                    #     continue
                    ################################################################

                    if s.mouse2driver_translate:
                        mouse.MoveR(nm_x, nm_y, api=s.mouse_driver, btn_flag=m2v_click.value, optimize=True)
                    else:
                        mouse.MoveR(nm_x, nm_y, api=s.mouse_driver, optimize=True)

                    try:
                        al_x += a_x * nm_x / m_x
                        al_y += a_y * nm_y / m_y
                    except ZeroDivisionError:
                        pass
                        # print('[Main] [W]: ZeroDivisionError handled at degrees movement compensation')
                    if not flick_triggered:
                        flick_triggered = True
                else:
                    m_x, m_y = 0, 0
                    pidx.reset()
                    pidy.reset()
                    flick_triggered = not s.flick_aim
            else:
                if reset_start_time is None:
                    reset_start_time = time.time()
                    reset_duration = (hold_time / max_hold_time) * max_retraction_time
                elapsed_reset_time = time.time() - reset_start_time
                if elapsed_reset_time < reset_duration:
                    macro_time = max(0, hold_time * (1 - elapsed_reset_time / reset_duration))
                else:
                    macro_time = 0
                m_x, m_y = 0, 0
                pidx.reset()
                pidy.reset()
                flick_triggered = not s.flick_aim
                # time.sleep(0.0091)

        mouse.close()
        thread_started = False
        aims_thread.join()
        exit_val.value = False

    def send_targets(self, aims):
        # data = pickle.dumps(aims)
        # self._targets_mem.buf[:] = b'\x00' * len(self._targets_mem.buf)
        # self._targets_mem.buf[:len(data)] = data
        # with self._cond:
        #     self._cond.notify()

        self._queue.put(aims)

    def flush(self):
        # while not self._queue.empty():
        #     self._queue.get()
        pass

    def start(self):
        if self._started:
            print('[AimMouse] [W]: Already started')

        self._exit.value = False

        # _alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
        # self._targets_mname = ''.join(random.choices(_alphabet, k=random.randint(13, 15)))

        # self._targets_mem = shared_memory.SharedMemory(create=True, size=2**10, name=self._targets_mname)
        # self._cond = Condition()

        # self._process = Process(
        #     target=self._target,
        #     args=(
        #         self.settings, self._targets_mname, self._cond, self._m2v_click, self._aim_enabled, self._lock_mode, self._lock_hold,
        #         self._lock_toggled, self._macro, self._smoothness, self._dynamic_height, self._use_pid, self._exit,
        #         self.aim_hz, self._m2v_x_acc, self._m2v_y_acc
        #     )
        # )

        self._process = Process(
            target=self._target,
            args=(
                self.settings, self._queue, self._m2v_click, self._aim_enabled, self._lock_mode, self._lock_hold,
                self._lock_toggled, self._macro, self._smoothness, self._dynamic_height, self._use_pid, self._exit,
                self.aim_hz, self._m2v_x_acc, self._m2v_y_acc
            )
        )

        self._process.start()

        while not self._exit.value:
            time.sleep(0.1)
        self._exit.value = False
        time.sleep(0.2)

        self._started = True

        print('[AimMouse] [I]: Started')

    def terminate(self):
        if not self._started:
            print('[AimMouse] [W]: Not started')

        self._exit.value = True
        time.sleep(0.1)
        # self.send_targets([0])
        while self._exit.value:
            time.sleep(0.1)

        self._process.terminate()

        # self._targets_mem.close()
        # self._targets_mem.unlink()

        self._started = False

        print('[AimMouse] [I] Terminated')
