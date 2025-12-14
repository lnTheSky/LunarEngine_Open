__all__ = []


def __dir__():
    return []


from multiprocessing import Process, Value, current_process, parent_process, Queue
from threading import Thread
import pyWinhook as pyhook
import pythoncom
import time
import winsound
import os


def activation_sound(on: bool):
    try:
        if on:
            winsound.PlaySound('button_activate.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
            return True
        winsound.PlaySound('button_deactivate.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
        return True
    except:
        return False


def _key_target_winhook(q, *args):
    def onClickDown(event):
        q.put(event.MessageName)

    def onKeyDown(event):
        q.put(event.Key)

    hm = pyhook.HookManager()
    hm.MouseAllButtonsDown = onClickDown
    hm.KeyDown = onKeyDown
    hm.HookMouse()
    hm.HookKeyboard()
    pythoncom.PumpMessages()


def get_pressed_key(api: str = 'winhook'):
    key = None
    if api == 'winhook':
        queue = Queue()
        process = Process(target=_key_target_winhook, args=(queue,))
        process.start()
        key = queue.get()
        process.terminate()
        process.join()
        process.close()
    else:
        try:
            mouse.__dict__
            keyboard.__dict__
        except Exception as e:
            print(f'[Hook Manager] [W]: Pynput not loaded. Loading...')
            from pynput import keyboard, mouse
        
        def on_click(x, y, btn, pressed):
            nonlocal key
            try:
                key = 'm_' + btn.name
            except:
                key = 'm_unknown'

        def on_press(key_btn):
            nonlocal key
            if key_btn.__class__ is keyboard.Key:
                try:
                    key = 'k_' + key_btn.name.lower()
                except:
                    key = 'k_unknown'
            elif key_btn.__class__ is keyboard.KeyCode:
                if key_btn.char is not None:
                    key = 'k_' + key_btn.char.lower()
                else:
                    key = 'k_unknown'
            else:
                key = 'k_unknown'

        mouse_l = mouse.Listener(on_click=on_click)
        keyboard_l = keyboard.Listener(on_press=on_press)

        mouse_l.start()
        keyboard_l.start()

        while True:
            if not key is None:
                break
            time.sleep(0.1)
        
        mouse_l.stop()
        keyboard_l.stop()
        del mouse_l, keyboard_l

    return key


class HookManager:

    def __init__(self, settings):
        self._trigger_mode_dict = {
            'bbox': 0,
            'color': 1,
            'pixel': 2
        }

        self._started = False
        self._process = None
        self._exit = Value('b', False)
        self._lock_mode = Value('b', False)
        self._lock_toggled = Value('b', False)
        self._lock_hold = Value('b', False)
        self._ragebot = Value('b', False)
        self._trigger_mode = Value('b', False)
        self._interpolation = Value('b', settings.interpolation_filter)
        self._reaction = Value('i', settings.trigger_reaction)
        self._duration = Value('i', settings.trigger_duration)
        self._smoothness = Value('f', settings.smooth)
        self._color_trigger_mode = Value('i', self._trigger_mode_dict[settings.color_trigger_mode])
        self._macro = Value('b', False)
        self._aim_enabled = Value('b', True)
        self._flickbot_enabled = Value('b', False)
        self._dynamic_height = Value('b', settings.dynamic_height)
        self._use_pid = Value('b', settings.use_pid)
        self.mouse_events = settings.mouse_events
        self.keyboard_events = settings.keyboard_events
        self.stop_moving_time = settings.stop_moving_time
        self._is_moving_a = Value('b', False)
        self._is_moving_w = Value('b', False)
        self._is_moving_s = Value('b', False)
        self._is_moving_d = Value('b', False)
        self.is_moving = False
        self._key_pressed = Value('b', False)
        self._press_mult = Value('i', 1)
        self._moving_thread = None
        self._moving_timer = time.perf_counter()
        self._trigger_wait_stop = Value('b', settings.wait_stop_moving)

        print(f'[HookManager] [I]: Bind sounds: {settings.bind_sounds}')

    @property
    def color_trigger_mode(self):
        if self._color_trigger_mode.value == 0:
            return 'bbox'
        elif self._color_trigger_mode.value == 1:
            return 'color'
        elif self._color_trigger_mode.value == 2:
            return 'pixel'

    @property
    def aim_enabled(self):
        return bool(self._aim_enabled.value)
    
    @property
    def key_pressed(self):
        return bool(self._key_pressed.value)

    @property
    def ragebot(self):
        return bool(self._ragebot.value)

    @property
    def dynamic_height(self):
        return bool(self._dynamic_height.value)

    @property
    def flickbot_enabled(self):
        return bool(self._flickbot_enabled.value)

    @property
    def use_pid(self):
        return bool(self._use_pid.value)

    @property
    def lock_mode(self):
        return bool(self._lock_mode.value)

    @property
    def lock_toggled(self):
        return bool(self._lock_toggled.value)

    @property
    def lock_hold(self):
        return bool(self._lock_hold.value)

    @property
    def is_alive(self):
        return self._started

    @property
    def trigger_mode(self):
        return bool(self._trigger_mode.value)

    @property
    def interpolation(self):
        return bool(self._interpolation.value)

    @property
    def reaction(self):
        return self._reaction.value

    @property
    def duration(self):
        return self._duration.value

    @property
    def smoothness(self):
        return self._smoothness.value

    @property
    def macro(self):
        return bool(self._macro.value)
    
    def _moving_target(self):
        press_time = None
        while self._started:
            if (self._is_moving_a.value or self._is_moving_d.value or self._is_moving_w.value or self._is_moving_s.value) and self._trigger_wait_stop.value:
                self.is_moving = True
                self._moving_timer = time.perf_counter()
            elif self.is_moving and ((time.perf_counter() - self._moving_timer) >= self.stop_moving_time / 1000):
                self.is_moving = False
            if self.key_pressed and press_time is None:
                press_time = time.time()
            elif self.key_pressed:
                k = 1
                if time.time() - press_time > 4.5:
                    k = 20
                elif time.time() - press_time > 3.5:
                    k = 15
                elif time.time() - press_time > 2.5:
                    k = 10
                elif time.time() - press_time > 1.5:
                    k = 5
                elif time.time() - press_time > 0.6:
                    k = 2
                self._press_mult.value = k
            else:
                press_time = None
                self._press_mult.value = 1
            
            time.sleep(0.01)

    @staticmethod
    def _target_pynput(mouse_events, keyboard_events, aim, trigger, interpolation, reaction, duration, smoothness, macro,
                aim_switch, flickbot_switch, pid_switch, aim_toggle, aim_hold, bind_sounds, color_trigger_mode,
                dynamic_height, ragebot, is_moving_a, is_moving_d, is_moving_s, is_moving_w, trigger_wait_stop, key_pressed, press_mult, exit_val):
        from pynput import keyboard, mouse
        
        # Функция обработки нажатия и отпускания кнопок мышки
        def on_click(x, y, btn, pressed):

            # Получаем название нажатой кнопки
            try:
                key = 'm_' + btn.name
            except:
                key = 'm_unknown'
            

            # Условие чтобы отделить нажатие и отпускание
            if pressed:
                # Проверяем, что нажатая кнопка в списке забинженных и выполняем соответствующие им действия
                if key in mouse_events:
                    match mouse_events[key]:
                        case 'aim':
                            if bool(aim_switch.value):
                                aim.value = True
                
                if key in keyboard_events:
                    match keyboard_events[key]:
                        case 'trigger':
                            trigger.value = True
                        case 'trigger_toggle':
                            trigger.value = not bool(trigger.value)
                            print('[Hook Manager] [I]: Trigger toggled ', bool(trigger.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(trigger.value))
                        case 'trigger_wait_stop':
                            trigger_wait_stop.value = not bool(trigger_wait_stop.value)
                            print("[Hook Manager] [I]: Trigger don't shoot while running ", bool(trigger_wait_stop.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(trigger_wait_stop.value))
                        case 'aim_toggle':
                            aim_toggle.value = not bool(aim_toggle.value)
                            print('[Hook Manager] [I]: Aim toggled ', bool(aim_toggle.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(aim_toggle.value))
                        case 'aim_hold':
                            aim_hold.value = True
                        case 'interpolation':
                            interpolation.value = not bool(interpolation.value)
                            print('[Hook Manager] [I]: Interpolation ', bool(interpolation.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(interpolation.value))
                        case 'dynamic_height':
                            dynamic_height.value = not bool(dynamic_height.value)
                            print('[Hook Manager] [I]: Dynamic Height ', bool(dynamic_height.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(dynamic_height.value))
                        case 'reaction-':
                            reaction.value -= 1
                            print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                            if bind_sounds:
                                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                        case 'reaction+':
                            reaction.value += 1
                            print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                            if bind_sounds:
                                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                        case 'duration-':
                            duration.value -= 1
                            print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                            if bind_sounds:
                                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                        case 'duration+':
                            duration.value += 1
                            print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                            if bind_sounds:
                                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                        case 'smooth-':
                            smoothness.value -= 0.05
                            print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                            if bind_sounds:
                                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                        case 'smooth+':
                            smoothness.value += 0.05
                            print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                            if bind_sounds:
                                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                        case 'macro':
                            macro.value = not bool(macro.value)
                            print('[Hook Manager] [I]: Macro ', bool(macro.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(macro.value))
                        case 'aim_switch':
                            aim_switch.value = not bool(aim_switch.value)
                            print('[Hook Manager] [I]: Enabled aim ', bool(aim_switch.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(aim_switch.value))
                        case 'flickbot_switch':
                            flickbot_switch.value = not bool(flickbot_switch.value)
                            print('[Hook Manager] [I]: Flickbot ', bool(flickbot_switch.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(flickbot_switch.value))
                        case 'pid_switch':
                            pid_switch.value = not bool(pid_switch.value)
                            print('[Hook Manager] [I]: PID ', bool(pid_switch.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(pid_switch.value))
                        case 'trigger_mode_switch':
                            color_trigger_mode.value = color_trigger_mode.value + 1
                            color_trigger_mode.value = color_trigger_mode.value % 3
                            print('[Hook Manager] [I]: ColorBot Trigger mode: ', color_trigger_mode.value, sep='')
                            if bind_sounds:
                                for i in range(color_trigger_mode.value + 1):
                                    winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                                    time.sleep(0.1)
                        case 'rage_switch':
                            ragebot.value = not bool(ragebot.value)
                            print('[Hook Manager] [I]: RageBot active', bool(ragebot.value), sep='')
                            if bind_sounds:
                                activation_sound(bool(ragebot.value))
                        case 'rage_hold':
                            ragebot.value = True                
            else:
                # Проверяем, что нажатая кнопка в списке забинженных и выполняем соответствующие им действия
                if key in mouse_events:
                    match mouse_events[key]:
                        case 'aim':
                            aim.value = False
                        case 'aim_hold':
                            aim_hold.value = False
                        case 'trigger':
                            trigger.value = False
                        case 'rage_hold':
                            ragebot.value = False

                if key in keyboard_events:
                    match keyboard_events[key]:
                        case 'aim_hold':
                            aim_hold.value = False
                        case 'trigger':
                            trigger.value = False
                        case 'rage_hold':
                            ragebot.value = False

        # Функция обработки нажатия клавиш клавиатуры
        def on_press(key_btn):

            # Получаем название нажатой кнопки
            if key_btn.__class__ is keyboard.Key:
                try:
                    key = 'k_' + key_btn.name.lower()
                except:
                    key = 'k_unknown'
            elif key_btn.__class__ is keyboard.KeyCode:
                if key_btn.char is not None:
                    key = 'k_' + key_btn.char.lower()
                else:
                    key = 'k_unknown'
            else:
                key = 'k_unknown'
            
            # Отслеживание ходьбы
            match key:
                case 'k_w':
                    is_moving_w.value = True
                case 'k_a':
                    is_moving_a.value = True
                case 'k_s':
                    is_moving_s.value = True
                case 'k_d':
                    is_moving_d.value = True
            
            # Отслеживание нажатой кнопки для её ускорения
            key_pressed.value = True

            # Проверка есть ли кнопка в биндах
            if key not in keyboard_events:
                return True
            
            match keyboard_events[key]:
                case 'trigger':
                    trigger.value = True
                case 'trigger_toggle':
                    trigger.value = not bool(trigger.value)
                    print('[Hook Manager] [I]: Trigger toggled ', bool(trigger.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(trigger.value))
                case 'trigger_wait_stop':
                        trigger_wait_stop.value = not bool(trigger_wait_stop.value)
                        print("[Hook Manager] [I]: Trigger don't shoot while running ", bool(trigger_wait_stop.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(trigger_wait_stop.value))
                case 'aim_toggle':
                    aim_toggle.value = not bool(aim_toggle.value)
                    print('[Hook Manager] [I]: Aim toggled ', bool(aim_toggle.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(aim_toggle.value))
                case 'aim_hold':
                    aim_hold.value = True
                case 'interpolation':
                    interpolation.value = not bool(interpolation.value)
                    print('[Hook Manager] [I]: Interpolation ', bool(interpolation.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(interpolation.value))
                case 'dynamic_height':
                    dynamic_height.value = not bool(dynamic_height.value)
                    print('[Hook Manager] [I]: Dynamic Height ', bool(dynamic_height.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(dynamic_height.value))
                case 'reaction-':
                    reaction.value -= 1 * press_mult.value
                    print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'reaction+':
                    reaction.value += 1 * press_mult.value
                    print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'duration-':
                    duration.value -= 1 * press_mult.value
                    print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'duration+':
                    duration.value += 1 * press_mult.value
                    print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'smooth-':
                    smoothness.value -= 0.05 * press_mult.value
                    print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'smooth+':
                    smoothness.value += 0.05 * press_mult.value
                    print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'macro':
                    macro.value = not bool(macro.value)
                    print('[Hook Manager] [I]: Macro ', bool(macro.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(macro.value))
                case 'aim_switch':
                    aim_switch.value = not bool(aim_switch.value)
                    print('[Hook Manager] [I]: Enabled aim ', bool(aim_switch.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(aim_switch.value))
                case 'flickbot_switch':
                    flickbot_switch.value = not bool(flickbot_switch.value)
                    print('[Hook Manager] [I]: Flickbot ', bool(flickbot_switch.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(flickbot_switch.value))
                case 'pid_switch':
                    pid_switch.value = not bool(pid_switch.value)
                    print('[Hook Manager] [I]: PID ', bool(pid_switch.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(pid_switch.value))
                case 'trigger_mode_switch':
                    color_trigger_mode.value = color_trigger_mode.value + 1
                    color_trigger_mode.value = color_trigger_mode.value % 3
                    print('[Hook Manager] [I]: ColorBot Trigger mode: ', color_trigger_mode.value, sep='')
                    if bind_sounds:
                        for i in range(color_trigger_mode.value + 1):
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                            time.sleep(0.1)
                case 'rage_switch':
                    ragebot.value = not bool(ragebot.value)
                    print('[Hook Manager] [I]: RageBot active', bool(ragebot.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(ragebot.value))
                case 'rage_hold':
                    ragebot.value = True
        
        # Функция обработки отпускания клавиш клавиатуры
        def on_release(key_btn):

            # Получаем название нажатой кнопки
            if key_btn.__class__ is keyboard.Key:
                try:
                    key = 'k_' + key_btn.name.lower()
                except:
                    key = 'k_unknown'
            elif key_btn.__class__ is keyboard.KeyCode:
                if key_btn.char is not None:
                    key = 'k_' + key_btn.char.lower()
                else:
                    key = 'k_unknown'
            else:
                key = 'k_unknown'
            
            # Отслеживание ходьбы
            match key:
                case 'k_w':
                    is_moving_w.value = False
                case 'k_a':
                    is_moving_a.value = False
                case 'k_s':
                    is_moving_s.value = False
                case 'k_d':
                    is_moving_d.value = False

            # Отслеживание нажатой кнопки для её ускорения
            key_pressed.value = False
            
            # Проверка кнопки на присутствие в биндах
            if key not in keyboard_events:
                return True

            match keyboard_events[key]:
                case 'aim_hold':
                    aim_hold.value = False
                case 'trigger':
                    trigger.value = False
                case 'rage_hold':
                    ragebot.value = False

        keyboard_l = keyboard.Listener(on_press=on_press, on_release=on_release)
        mouse_l = mouse.Listener(on_click=on_click)

        keyboard_l.start()
        mouse_l.start()

        print('[Hook Manager] [I]: Successfully started! (Pynput)')

        exit_val.value = True

        par_p = parent_process()
        while True:
            time.sleep(5)
            if not par_p.is_alive():
                print('[Hook Manager] [W]: Killed by closed parent')
                break
        os.kill(current_process().pid, 15)

    @staticmethod
    def _target_winhook(mouse_events, keyboard_events, aim, trigger, interpolation, reaction, duration, smoothness, macro,
                aim_switch, flickbot_switch, pid_switch, aim_toggle, aim_hold, bind_sounds, color_trigger_mode,
                dynamic_height, ragebot, is_moving_a, is_moving_d, is_moving_s, is_moving_w, trigger_wait_stop, key_pressed, press_mult, exit_val):

        def onClickDown(event):
            if bool(event.Injected):
                return True

            if event.MessageName in mouse_events:
                match mouse_events[event.MessageName]:
                    case 'aim':
                        if bool(aim_switch.value):
                            aim.value = True

            if event.MessageName in keyboard_events:
                match keyboard_events[event.MessageName]:
                    case 'trigger':
                        trigger.value = True
                    case 'trigger_toggle':
                        trigger.value = not bool(trigger.value)
                        print('[Hook Manager] [I]: Trigger toggled ', bool(trigger.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(trigger.value))
                    case 'trigger_wait_stop':
                        trigger_wait_stop.value = not bool(trigger_wait_stop.value)
                        print("[Hook Manager] [I]: Trigger don't shoot while running ", bool(trigger_wait_stop.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(trigger_wait_stop.value))
                    case 'aim_toggle':
                        aim_toggle.value = not bool(aim_toggle.value)
                        print('[Hook Manager] [I]: Aim toggled ', bool(aim_toggle.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(aim_toggle.value))
                    case 'aim_hold':
                        aim_hold.value = True
                    case 'interpolation':
                        interpolation.value = not bool(interpolation.value)
                        print('[Hook Manager] [I]: Interpolation ', bool(interpolation.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(interpolation.value))
                    case 'dynamic_height':
                        dynamic_height.value = not bool(dynamic_height.value)
                        print('[Hook Manager] [I]: Dynamic Height ', bool(dynamic_height.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(dynamic_height.value))
                    case 'reaction-':
                        reaction.value -= 1
                        print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                        if bind_sounds:
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                    case 'reaction+':
                        reaction.value += 1
                        print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                        if bind_sounds:
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                    case 'duration-':
                        duration.value -= 1
                        print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                        if bind_sounds:
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                    case 'duration+':
                        duration.value += 1
                        print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                        if bind_sounds:
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                    case 'smooth-':
                        smoothness.value -= 0.05
                        print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                        if bind_sounds:
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                    case 'smooth+':
                        smoothness.value += 0.05
                        print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                        if bind_sounds:
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                    case 'macro':
                        macro.value = not bool(macro.value)
                        print('[Hook Manager] [I]: Macro ', bool(macro.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(macro.value))
                    case 'aim_switch':
                        aim_switch.value = not bool(aim_switch.value)
                        print('[Hook Manager] [I]: Enabled aim ', bool(aim_switch.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(aim_switch.value))
                    case 'flickbot_switch':
                        flickbot_switch.value = not bool(flickbot_switch.value)
                        print('[Hook Manager] [I]: Flickbot ', bool(flickbot_switch.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(flickbot_switch.value))
                    case 'pid_switch':
                        pid_switch.value = not bool(pid_switch.value)
                        print('[Hook Manager] [I]: PID ', bool(pid_switch.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(pid_switch.value))
                    case 'trigger_mode_switch':
                        color_trigger_mode.value = color_trigger_mode.value + 1
                        color_trigger_mode.value = color_trigger_mode.value % 3
                        print('[Hook Manager] [I]: ColorBot Trigger mode: ', color_trigger_mode.value, sep='')
                        if bind_sounds:
                            for i in range(color_trigger_mode.value + 1):
                                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                                time.sleep(0.1)
                    case 'rage_switch':
                        ragebot.value = not bool(ragebot.value)
                        print('[Hook Manager] [I]: RageBot active', bool(ragebot.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(ragebot.value))
                    case 'rage_hold':
                        ragebot.value = True

            return True

        def onClickUp(event):
            if bool(event.Injected):
                return True

            if event.MessageName in mouse_events:
                match mouse_events[event.MessageName]:
                    case 'aim':
                        aim.value = False
                    case 'aim_hold':
                        aim_hold.value = False
                    case 'trigger':
                        trigger.value = False
                    case 'rage_hold':
                        ragebot.value = False

            if event.MessageName in keyboard_events:
                match keyboard_events[event.MessageName]:
                    case 'aim_hold':
                        aim_hold.value = False
                    case 'trigger':
                        trigger.value = False
                    case 'rage_hold':
                        ragebot.value = False

            if event.MessageName == 'mouse right up' and 'mouse right down' in keyboard_events:
                aim_hold.value = False
                trigger.value = False
                ragebot.value = False

            return True

        def onKeyDown(event):
            match event.Key:
                case 'W':
                    is_moving_w.value = True
                case 'A':
                    is_moving_a.value = True
                case 'S':
                    is_moving_s.value = True
                case 'D':
                    is_moving_d.value = True

            if bool(event.Injected):
                return True
            
            key_pressed.value = True

            if event.Key not in keyboard_events:
                return True

            match keyboard_events[event.Key]:
                case 'trigger':
                    trigger.value = True
                case 'trigger_toggle':
                    trigger.value = not bool(trigger.value)
                    print('[Hook Manager] [I]: Trigger toggled ', bool(trigger.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(trigger.value))
                case 'trigger_wait_stop':
                        trigger_wait_stop.value = not bool(trigger_wait_stop.value)
                        print("[Hook Manager] [I]: Trigger don't shoot while running ", bool(trigger_wait_stop.value), sep='')
                        if bind_sounds:
                            activation_sound(bool(trigger_wait_stop.value))
                case 'aim_toggle':
                    aim_toggle.value = not bool(aim_toggle.value)
                    print('[Hook Manager] [I]: Aim toggled ', bool(aim_toggle.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(aim_toggle.value))
                case 'aim_hold':
                    aim_hold.value = True
                case 'interpolation':
                    interpolation.value = not bool(interpolation.value)
                    print('[Hook Manager] [I]: Interpolation ', bool(interpolation.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(interpolation.value))
                case 'dynamic_height':
                    dynamic_height.value = not bool(dynamic_height.value)
                    print('[Hook Manager] [I]: Dynamic Height ', bool(dynamic_height.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(dynamic_height.value))
                case 'reaction-':
                    reaction.value -= 1 * press_mult.value
                    print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'reaction+':
                    reaction.value += 1 * press_mult.value
                    print('[Hook Manager] [I]: Reaction ', reaction.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'duration-':
                    duration.value -= 1 * press_mult.value
                    print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'duration+':
                    duration.value += 1 * press_mult.value
                    print('[Hook Manager] [I]: Duration ', duration.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'smooth-':
                    smoothness.value -= 0.05 * press_mult.value
                    print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'smooth+':
                    smoothness.value += 0.05 * press_mult.value
                    print('[Hook Manager] [I]: Smoothness ', smoothness.value, sep='')
                    if bind_sounds:
                        winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                case 'macro':
                    macro.value = not bool(macro.value)
                    print('[Hook Manager] [I]: Macro ', bool(macro.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(macro.value))
                case 'aim_switch':
                    aim_switch.value = not bool(aim_switch.value)
                    print('[Hook Manager] [I]: Enabled aim ', bool(aim_switch.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(aim_switch.value))
                case 'flickbot_switch':
                    flickbot_switch.value = not bool(flickbot_switch.value)
                    print('[Hook Manager] [I]: Flickbot ', bool(flickbot_switch.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(flickbot_switch.value))
                case 'pid_switch':
                    pid_switch.value = not bool(pid_switch.value)
                    print('[Hook Manager] [I]: PID ', bool(pid_switch.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(pid_switch.value))
                case 'trigger_mode_switch':
                    color_trigger_mode.value = color_trigger_mode.value + 1
                    color_trigger_mode.value = color_trigger_mode.value % 3
                    print('[Hook Manager] [I]: ColorBot Trigger mode: ', color_trigger_mode.value, sep='')
                    if bind_sounds:
                        for i in range(color_trigger_mode.value + 1):
                            winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                            time.sleep(0.1)
                case 'rage_switch':
                    ragebot.value = not bool(ragebot.value)
                    print('[Hook Manager] [I]: RageBot active', bool(ragebot.value), sep='')
                    if bind_sounds:
                        activation_sound(bool(ragebot.value))
                case 'rage_hold':
                    ragebot.value = True

            return True

        def onKeyUp(event):
            match event.Key:
                case 'W':
                    is_moving_w.value = False
                case 'A':
                    is_moving_a.value = False
                case 'S':
                    is_moving_s.value = False
                case 'D':
                    is_moving_d.value = False
            
            if bool(event.Injected):
                return True

            key_pressed.value = False
            
            if event.Key not in keyboard_events:
                return True

            match keyboard_events[event.Key]:
                case 'aim_hold':
                    aim_hold.value = False
                case 'trigger':
                    trigger.value = False
                case 'rage_hold':
                    ragebot.value = False

            return True

        def parent_is_alive():
            par_p = parent_process()
            while True:
                time.sleep(5)
                if not par_p.is_alive():
                    break
            os.kill(current_process().pid, 15)

        hm = pyhook.HookManager()
        hm.MouseAllButtonsDown = onClickDown
        hm.MouseAllButtonsUp = onClickUp
        hm.KeyDown = onKeyDown
        hm.KeyUp = onKeyUp
        hm.HookMouse()
        hm.HookKeyboard()

        is_alive = Thread(target=parent_is_alive)
        is_alive.start()

        print('[Hook Manager] [I]: Successfully started! (PyWinHook)')

        exit_val.value = True

        pythoncom.PumpMessages()

    def start(self, mouse_events=None, keyboard_events=None, bind_sounds: bool = True, api: str = 'winhook'):

        if self._started:
            print("[Hook Manager] [W]: The process already started")
            return None

        self._exit.value = False

        if mouse_events:
            self.mouse_events.update(mouse_events)
        if keyboard_events:
            self.keyboard_events.update(keyboard_events)

        if api == 'winhook':
            self._process = Process(
                target=self._target_winhook,
                args=(
                    self.mouse_events, self.keyboard_events, self._lock_mode, self._trigger_mode,
                    self._interpolation, self._reaction, self._duration, self._smoothness,
                    self._macro, self._aim_enabled, self._flickbot_enabled, self._use_pid,
                    self._lock_toggled, self._lock_hold, bind_sounds, self._color_trigger_mode,
                    self._dynamic_height, self._ragebot, self._is_moving_a, self._is_moving_d,
                    self._is_moving_s, self._is_moving_w, self._trigger_wait_stop, self._key_pressed, 
                    self._press_mult, self._exit
                )
            )
        else:
            self._process = Process(
                target=self._target_pynput,
                args=(
                    self.mouse_events, self.keyboard_events, self._lock_mode, self._trigger_mode,
                    self._interpolation, self._reaction, self._duration, self._smoothness,
                    self._macro, self._aim_enabled, self._flickbot_enabled, self._use_pid,
                    self._lock_toggled, self._lock_hold, bind_sounds, self._color_trigger_mode,
                    self._dynamic_height, self._ragebot, self._is_moving_a, self._is_moving_d,
                    self._is_moving_s, self._is_moving_w, self._trigger_wait_stop, self._key_pressed, 
                    self._press_mult, self._exit
                )
            )

        print('[Hook Manager] [I]: Starting...')
        self._process.start()

        while not self._exit.value:
            time.sleep(0.1)

        self._started = True

        self._moving_thread = Thread(target=self._moving_target)
        self._moving_thread.start()

    def terminate(self):

        if not self._started:
            print("[Hook Manager] [W]: Unable to terminate process. The hook isn't running")
            return None

        print('[Hook Manager] [I]: Terminating process...')
        self._process.terminate()
        print('[Hook Manager] [I]: Process terminated')

        # time.sleep(0.1)
        self._process.join()
        # if not self._process.is_alive():
        #     self._process.join(1)

        print('[Hook Manager] [I]: Closing process...')
        # time.sleep(1)
        self._process.close()

        self._started = False
        self._moving_thread.join()
