__all__ = []


def __dir__():
    return []


import flet
from flet import (
    Container,
    Column,
    MainAxisAlignment,
    CrossAxisAlignment,
    ElevatedButton,
    OutlinedButton,
    IconButton,
    icons,
    ButtonStyle,
    MaterialState,
    CircleBorder,
    ScrollMode,
    Text,
    TextAlign,
    Row,
    ResponsiveRow,
    Dropdown,
    dropdown,
    border_radius,
    TextField,
    Switch,
    colors,
    Slider,
    Divider,
    LineChart,
    LineChartData,
    LineChartDataPoint,
    Border,
    BorderSide,
    ChartAxis,
    margin,
    FilePickerResultEvent,
    FilePicker,
    Markdown,
    MarkdownExtensionSet
)
from flet_contrib.color_picker import ColorPicker
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import current_process
from core_utils import CoreState, Settings, SETTINGS_LIST, check_settings
from hook_manager import get_pressed_key
from win32api import GetSystemMetrics
from usb2driver import get_devices, get_report_changes
from psutil import pid_exists, HIGH_PRIORITY_CLASS, ABOVE_NORMAL_PRIORITY_CLASS, NORMAL_PRIORITY_CLASS, \
    BELOW_NORMAL_PRIORITY_CLASS, IDLE_PRIORITY_CLASS
from threading import Thread
from GPUtil import getGPUs
from locales import TextLocales
import subprocess
import winsound
import ctypes
import random
import pickle
import socket
import struct
import json
import time
import math
import os


UUID_OFFSET = 366
UUID_LEN = 32

# def getGPUs():
#     return []


class SettingsContent:

    def __init__(self, date, page: flet.Page, license_type: int):
        self.border_radius = 18
        self.bgcolor_theme = colors.BLACK26
        self.date = date
        self.lic_type = license_type

        if page.client_storage.contains_key('locale'):
            self.textLocaled = TextLocales(page.client_storage.get('locale'))
        else:
            self.textLocaled = TextLocales()
        # self.textLocaled = TextLocales('en-US')

        self.lic_tiers = {
            254: 'X',
            0: 'I User-Mode',
            1: 'II Kernel-Mode',
            2: 'III Kernel-Proxy',
            3: 'IV FaceIT-UD'
        }

        self.file_picker = FilePicker(on_result=self.load_config)
        self.file_saver = FilePicker(on_result=self.save_config)
        self.low_aim_color_picker = ColorPicker(color="#68526b", width=300)
        self.high_aim_color_picker = ColorPicker(color="#ff00f7", width=300)
        self.low_trigger_color_picker = ColorPicker(color="#68526b", width=300)
        self.high_trigger_color_picker = ColorPicker(color="#ff00f7", width=300)

        self.page = page
        self.page.overlay.append(self.file_picker)
        self.page.overlay.append(self.file_saver)
        # self.page.on_keyboard_event = self.on_keyboard

        self.config_names = []
        self.update_config_names()

        self.settings = Settings()

        self._alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
        self.core_memory_name = ''.join(random.choices(self._alphabet, k=random.randint(6, 12)))

        self.core_memory = SharedMemory(self.core_memory_name, create=True, size=2**20)
        self.core_state = CoreState()
        self.core_state.parent_pid = current_process().pid
        self.core_state_listener_ran = False
        self.core_state_refresh_rate = 10
        self.core_state_listener = Thread(target=self.core_state_listener_target)

        self.settings.bind_sounds = True
        self.settings.core_priority = NORMAL_PRIORITY_CLASS

        self.settings.rtx_gpu = False
        self.settings.screen_width = GetSystemMetrics(0)
        self.settings.screen_height = GetSystemMetrics(1)
        self.settings.neural_input_area_size = 320

        self.settings.interpolation_filter = False
        self.settings.interpolation_filter_refresh_rate = 1000
        self.settings.mouse_driver = 'user32'
        self.settings.driver_priority = False
        self.settings.accumulate_mouse_movement = False
        self.settings.compensate_mouse_movement = False
        self.settings.mouse_c_ip = '10.55.0.5'
        self.settings.mouse_l_ip = '10.55.0.1'
        self.settings.mouse_l_port = 13371
        self.settings.mouse_proxy_manual = False
        self.settings.mouse2driver_translate = False
        # self.settings.mouse_device = None
        self.settings.mouse_report_log = False
        self.settings.alternative_parser = False

        self.settings.mouse_manual_parse = False
        self.settings.mouse_parse_dict = {"move_xy_offset": 1, "move_xy_size": 4, "scroll_offset": 4, "scroll_size": 1, "buttons_offset": 0, "buttons_count": 8}
        self.settings.mouse_interface = -1

        self.settings.iou_thres = 0.65
        self.settings.conf_thres = 0.25
        self.settings.topk = 100
        self.settings.detection_classes = [0, 2]
        self.settings.screen_handler_queue_size = 1
        self.settings.screen_handler_queue_mode = False
        self.settings.frame_synchronization = False
        self.settings.use_dxcam = False

        self.settings.smooth = 5
        self.settings.static_height_offset = 3
        self.settings.detect_distance_x = 55
        self.settings.detect_distance_y = 55
        self.settings.dynamic_height = False
        self.settings.predict_x = False
        self.settings.predict_y = False
        self.settings.prediction_x = 1.9
        self.settings.prediction_y = 1
        self.settings.damping_x = 0.4
        self.settings.damping_y = 0.4
        self.settings.damping_power_x = 1.5
        self.settings.damping_power_y = 1
        self.settings.nonlinear_aim = False
        self.settings.nonlinear_k = 3.5
        self.settings.nonlinear_b = 1.3
        self.settings.nonlinear_i = 1.5

        self.settings.trigger_reaction = -10
        self.settings.trigger_duration = 20
        self.settings.trigger_reaction_dispersion = 1.7
        self.settings.trigger_duration_dispersion = 5.4
        self.settings.trigger_burst_mode = False
        self.settings.trigger_burst_count = 4
        self.settings.trigger_cooldown = 200
        self.settings.trigger_cooldown_dispersion = 20
        self.settings.low_trigger_color = '#68526b'
        self.settings.high_trigger_color = '#ff00f7'
        self.settings.color_trigger_mode = 'color'
        self.settings.min_ratio_trigger = 0.33
        self.settings.max_ratio_trigger = 0.93
        self.settings.morph_iterations_trigger = 2
        self.settings.dilate_iterations_trigger = 6
        self.settings.morph_kernel_trigger = (3, 3)
        self.settings.dilate_kernel_trigger = (17, 3)
        self.settings.changed_pixels = 1
        self.settings.trigger_zone = (8, 8)
        self.settings.trigger_pixel_thresh = 25
        self.settings.stop_moving_time = 125
        self.settings.wait_stop_moving = False
        self.settings.trigger_hit_chance = 100

        self.settings.use_pid = True
        self.settings.flick_aim = False
        self.settings.pid_interpolate = False
        self.settings.pidx_k = 0.315
        self.settings.pidx_i = 0.17
        self.settings.pidx_d = 0.0033
        self.settings.pidy_k = 0.24
        self.settings.pidy_i = 0.1
        self.settings.pidy_d = 0.0

        self.settings.low_aim_color = '#68526b'
        self.settings.high_aim_color = '#ff00f7'
        self.settings.min_ratio = 0.33
        self.settings.max_ratio = 0.93
        self.settings.morph_iterations = 2
        self.settings.dilate_iterations = 6
        self.settings.morph_kernel = (3, 3)
        self.settings.dilate_kernel = (17, 3)
        self.settings.use_centroids = True
        self.settings.centroids_thresh = 0.7

        self.settings.ragebot_max_flick = 127
        self.settings.ragebot_flick_time = 40
        self.settings.ragebot_retract_time = 10
        self.settings.ragebot_cooldown_time = 110

        self.settings.screen_handler_fps = None

        self.settings.hookmanager_api = 'winhook'
        self.settings.mouse_events = {
            'mouse left down': 'aim',
            'mouse left up': 'aim'
        }

        self.settings.keyboard_events = {
            'Lmenu': 'trigger',
            'Rcontrol': 'interpolation',
            'F1': 'smooth-',
            'F2': 'smooth+',
            'Rmenu': 'macro',
            'V': 'trigger_toggle',
            'Z': 'aim_toggle',
            'Left': 'reaction-',
            'Right': 'reaction+',
            'Up': 'duration+',
            'Down': 'duration-',
            'F3': 'aim_switch',
            'F4': 'rage_switch',
            'mouse right down': 'rage_hold'
        }

        self.actions = self.textLocaled('actions')

        self.lunarbox_actions = {
            'shutdown': 1,
            'reboot': 2
        }

        self.bindings_rows = []

        self.settings.aim_model_name = 'yolov8s-pose'
        self.settings.trigger_model_name = 'yolov8s'
        self.settings.macro_divide = 6
        self.settings.target_height = 0.68

        # n
        self.game_select = Dropdown(
            label=self.textLocaled('game_select_label'),
            width=160,
            hint_text=self.textLocaled('game_select_hint'),
            options=[
                dropdown.Option(text='FragPunk', key='fragpunk'),
                dropdown.Option(text='CS2', key='cs'),
                dropdown.Option(text='Valorant', key='val'),
                dropdown.Option(text='Apex Legends', key='apex'),
                dropdown.Option(text=self.textLocaled('game_select_othergame'), key='other')
            ],
            border_radius=border_radius.all(self.border_radius),
            on_change=self.game_selected,
        )

        self.sensitivity = TextField(
            label=self.textLocaled('sensitivity_label'),
            hint_text=f'{self.textLocaled("example")}: 1.5',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            col={'sm': 5, 'md': 4, 'lg': 3}
        )

        self.full_rotate = TextField(
            label=self.textLocaled('full_rotate_label'),
            hint_text=f'{self.textLocaled("example")}: 15000',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            col={'sm': 5, 'md': 4, 'lg': 3}
        )

        self.fov = TextField(
            label=self.textLocaled('fov_label'),
            hint_text=f'{self.textLocaled("example")}: 90',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            col={'sm': 5, 'md': 4, 'lg': 3}
        )

        self.screen_width = TextField(
            label=self.textLocaled('screen_width_label'),
            hint_text=f'{self.textLocaled("example")}: 1920',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=self.settings.screen_width
        )

        self.screen_height = TextField(
            label=self.textLocaled('screen_height_label'),
            hint_text=f'{self.textLocaled("example")}: 1080',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=self.settings.screen_height
        )

        # n
        self.screen_handler_fps_check = Switch(
            label=self.textLocaled('screen_handler_fps_check_label'),
            value=True,
            on_change=self.change_fps
        )

        self.screen_handler_fps = TextField(
            label=self.textLocaled('screen_handler_fps_label'),
            hint_text=f'{self.textLocaled("example")}: 60',
            disabled=True,
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
        )

        self.neural_input_area_size = TextField(
            label=self.textLocaled('neural_input_area_size_label'),
            hint_text=f'{self.textLocaled("example")}: 320',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.neural_input_area_size)
        )

        # n
        self.gpu_select = Dropdown(
            label=self.textLocaled('gpu_select_label'),
            hint_text=self.textLocaled('gpu_select_hint'),
            options=[dropdown.Option(text=gpu.name, key=f'cuda:{gpu.id}') for gpu in getGPUs()] +
                    [dropdown.Option(text='CPU', key='cpu')],
            border_radius=border_radius.all(self.border_radius),
            on_change=self.gpu_selected
        )

        # n
        self.cudart_select = Dropdown(
            label=self.textLocaled('cudart_select_label'),
            hint_text=self.textLocaled('cudart_select_hint'),
            options=[
                dropdown.Option(text='TensorRT', key='trt', disabled=True),
                dropdown.Option(text='Torch', key='torch'),
                dropdown.Option(text='ONNX', key='onnx'),
                dropdown.Option(text='TorchScript', key='torchscript', disabled=True)
            ],
            border_radius=border_radius.all(self.border_radius),
            on_change=self.cudart_selected,
        )

        self.iou_thres = Slider(
            value=int(self.settings.iou_thres * 100),
            min=0,
            max=95,
            divisions=19,
            width=300,
            label="0.{value}",
            on_change=self.set_thres
        )

        self.conf_thres = Slider(
            value=int(self.settings.conf_thres * 100),
            min=0,
            max=95,
            divisions=19,
            width=300,
            label="0.{value}",
            on_change=self.set_thres
        )

        self.topk = Slider(
            value=self.settings.topk,
            min=1,
            max=200,
            divisions=199,
            width=300,
            label="{value}",
            on_change=self.text_field_change_int
        )

        # noinspection PyTypeChecker
        # n
        self.screen_handler_queue_mode = Dropdown(
            label=self.textLocaled('screen_handler_queue_mode_label'),
            hint_text=self.textLocaled('screen_handler_queue_mode_hint'),
            options=[
                dropdown.Option(
                    text=self.textLocaled('screen_handler_queue_mode_option_1'),
                    key=False
                ),
                dropdown.Option(
                    text=self.textLocaled('screen_handler_queue_mode_option_2'),
                    key=True
                )
            ],
            border_radius=border_radius.all(self.border_radius),
            on_change=self.get_queue_mode,
            value=self.settings.screen_handler_queue_mode
        )

        self.screen_handler_queue_size = TextField(
            label=self.textLocaled('screen_handler_queue_size_label'),
            hint_text=f'{self.textLocaled("example")}: 1',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.screen_handler_queue_size),
            disabled=not self.settings.screen_handler_queue_mode
        )

        # n
        self.frame_synchronization = Switch(
            label=self.textLocaled('frame_synchronization_label'),
            value=self.settings.frame_synchronization,
            on_change=lambda e: setattr(self.settings, 'frame_synchronization', e.control.value)
        )

        self.use_dxcam = Switch(
            label=self.textLocaled('use_dxcam_label'),
            value=self.settings.use_dxcam,
            on_change=lambda e: setattr(self.settings, 'use_dxcam', e.control.value)
        )

        self.detect_distance_x = TextField(
            label=self.textLocaled('detect_distance_x_label'),
            hint_text=f'{self.textLocaled("example")}: 180',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.detect_distance_x)
        )

        self.detect_distance_y = TextField(
            label=self.textLocaled('detect_distance_y_label'),
            hint_text=f'{self.textLocaled("example")}: 180',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.detect_distance_y)
        )

        # n
        self.interpolation_filter = Switch(
            label=self.textLocaled('interpolation_filter_label'),
            value=self.settings.interpolation_filter,
            on_change=self.switch_interpolation_filter
            # disabled=not self.settings.interpolation_filter
        )

        # n
        self.mouse_driver = Dropdown(
            label=self.textLocaled('mouse_driver_label'),
            hint_text=self.textLocaled('mouse_driver_hint'),
            options=[
                dropdown.Option(
                    text='LunarBox Proxy',
                    key='proxy',
                    disabled=True if self.lic_type != 3 else False
                ),
                dropdown.Option(
                    text='LunarSTM32',
                    key='stm32',
                    disabled=True if self.lic_type != 3 else False
                ),
                dropdown.Option(
                    text='Interception',
                    key='interception',
                    disabled=True if self.lic_type != 3 else False
                ),
                dropdown.Option(
                    text='Remote Driver',
                    key='rdriver',
                    disabled=True if self.lic_type == 254 or self.lic_type == 0 else False
                ),
                dropdown.Option(
                    text='Virtual Driver',
                    key='driver',
                    disabled=True if self.lic_type == 254 or self.lic_type == 0 else False
                ),
                dropdown.Option(
                    text='GHub',
                    key='ghub',
                    disabled=True if self.lic_type == 254 else False
                ),
                dropdown.Option(
                    text='Win32API',
                    key='user32',
                    disabled=True if self.lic_type == 254 else False
                )
            ],
            border_radius=border_radius.all(self.border_radius),
            on_change=self.mouse_driver_change,
            value=self.settings.mouse_driver
        )

        self.interpolation_filter_refresh_rate = TextField(
            label=self.textLocaled('interpolation_filter_refresh_rate_label'),
            hint_text=f'{self.textLocaled("example")}: 1000',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.interpolation_filter_refresh_rate)
        )

        self.smooth = TextField(
            label=self.textLocaled('smooth_label'),
            hint_text=f'{self.textLocaled("example")}: 3.1',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            col={'md': 6, 'lg': 5, 'xl': 4},
            value=str(self.settings.smooth)
        )

        # n
        self.nonlinear_aim = Switch(
            label=self.textLocaled('nonlinear_aim_label'),
            value=self.settings.nonlinear_aim,
            on_change=self.switch_nonlinear_aim
        )

        self.nonlinear_k = TextField(
            label=self.textLocaled('nonlinear_k_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.nonlinear_k}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.aim_chart_change_float,
            value=str(self.settings.nonlinear_k),
            disabled=not self.settings.nonlinear_aim
        )

        self.nonlinear_i = TextField(
            label=self.textLocaled('nonlinear_i_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.nonlinear_i}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.aim_chart_change_float,
            value=str(self.settings.nonlinear_i),
            disabled=not self.settings.nonlinear_aim
        )

        self.nonlinear_b = TextField(
            label=self.textLocaled('nonlinear_b_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.nonlinear_b}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.aim_chart_change_float,
            value=str(self.settings.nonlinear_b),
            disabled=not self.settings.nonlinear_aim
        )

        self.core_ran_text = Text(self.textLocaled('core_ran_text_stopped'), size=34, color='#bf2c4c')

        self.nonlinear_aim_chart = LineChart(
            data_series=[
                self.aim_chart_data(1, 0, -1, 40,
                                    colors.CYAN)],
            left_axis=ChartAxis(
                labels_size=50,
                title=Text(self.textLocaled('nonlinear_aim_chart_axis_y'))
            ),
            bottom_axis=ChartAxis(
                labels_size=50,
                title=Text(self.textLocaled('nonlinear_aim_chart_axis_x'))
            ),
            border=Border(
                bottom=BorderSide(4, colors.with_opacity(0.5, colors.ON_SURFACE)),
                left=BorderSide(4, colors.with_opacity(0.5, colors.ON_SURFACE)),
            ),
            tooltip_bgcolor=colors.with_opacity(0.2, colors.CYAN_ACCENT),
            min_x=0,
            min_y=0,
            max_x=1,
            max_y=1,
            # expand=1,
            # animate=flet.animation.Animation(0.5, flet.AnimationCurve.EASE_IN_OUT_CUBIC)
        )

        self.trigger_reaction = TextField(
            label=self.textLocaled('trigger_reaction_label'),
            hint_text=f'{self.textLocaled("example")}: 17',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.normal_change_int,
            value=str(self.settings.trigger_reaction)
        )

        self.trigger_duration = TextField(
            label=self.textLocaled('trigger_duration_label'),
            hint_text=f'{self.textLocaled("example")}: 20',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.normal_change_int,
            value=str(self.settings.trigger_duration)
        )

        self.trigger_reaction_dispersion = TextField(
            label=self.textLocaled('trigger_reaction_dispersion_label'),
            hint_text=self.textLocaled('trigger_reaction_dispersion_hint'),
            border_radius=border_radius.all(self.border_radius),
            on_change=self.normal_chart_change_float,
            value=str(self.settings.trigger_reaction_dispersion)
        )

        self.trigger_duration_dispersion = TextField(
            label=self.textLocaled('trigger_duration_dispersion_label'),
            hint_text=self.textLocaled('trigger_duration_dispersion_hint'),
            border_radius=border_radius.all(self.border_radius),
            on_change=self.normal_chart_change_float,
            value=str(self.settings.trigger_duration_dispersion)
        )

        # n
        self.normal_chart = LineChart(
            data_series=[self.normal_chart_data(self.settings.trigger_reaction,
                                                self.settings.trigger_reaction_dispersion, 40, colors.CYAN),
                         self.normal_chart_data(self.settings.trigger_duration,
                                                self.settings.trigger_duration_dispersion, 40, colors.ORANGE)
                         ],
            left_axis=ChartAxis(
                labels_size=50,
                title=Text(self.textLocaled('normal_chart_axis_y'))
            ),
            bottom_axis=ChartAxis(
                labels_size=50,
                title=Text(self.textLocaled('normal_chart_axis_x'))
            ),
            border=Border(
                bottom=BorderSide(4, colors.with_opacity(0.5, colors.ON_SURFACE)),
                left=BorderSide(4, colors.with_opacity(0.5, colors.ON_SURFACE)),
            ),
            tooltip_bgcolor=colors.with_opacity(0.2, colors.CYAN_ACCENT),
            min_x=-40,
            min_y=0,
            max_x=40,
            max_y=0.3,
            expand=1
        )

        self.config_menu = Dropdown(
            label=self.textLocaled('config_menu_label'),
            width=160,
            hint_text=self.textLocaled('config_menu_hint'),
            options=[dropdown.Option(text=config) for config in self.config_names],
            border_radius=border_radius.all(self.border_radius),
            on_change=self.on_change_config_menu
        )
        self.config_menu.options.append(dropdown.Option(text=self.textLocaled('config_menu_button'), key='newconfig_save'))

        self.update_core_state_field()
        self.core_state_field = Markdown(
            self.core_state_text,
            selectable=False,
            extension_set=MarkdownExtensionSet.GITHUB_WEB,
            expand=True,
            opacity=0.8
        )

        self.aim_model_name = Dropdown(
            label=self.textLocaled('aim_model_name_label'),
            width=160,
            hint_text=self.textLocaled('model_name_hint'),
            options=[
                dropdown.Option(text='ColorBot', key='color'),
                dropdown.Option(text='NanoV10', key='yolov10n'),
                dropdown.Option(text='SmallV10', key='yolov10s'),
                dropdown.Option(text='MediumV10', key='yolov10m'),
                dropdown.Option(text='NanoV9', key='yolo11n'),
                dropdown.Option(text='SmallV9', key='yolo11s'),
                dropdown.Option(text='MediumV9', key='yolov9m'),
                dropdown.Option(text='NanoV8', key='yolov8n'),
                dropdown.Option(text='Nano-PoseV8', key='yolov8n-pose'),
                dropdown.Option(text='SmallV8', key='yolov8s'),
                dropdown.Option(text='Small-PoseV8', key='yolov8s-pose'),
                dropdown.Option(text='MediumV8', key='yolov8m'),
                dropdown.Option(text='Medium-PoseV8', key='yolov8m-pose'),
                dropdown.Option(text='Best', key='best')
            ],
            value=self.settings.aim_model_name,
            border_radius=border_radius.all(self.border_radius),
            on_change=lambda e: setattr(self.settings, 'aim_model_name', e.control.value),
            col={'md': 6, 'lg': 5, 'xl': 4}
        )

        self.trigger_model_name = Dropdown(
            label=self.textLocaled('trigger_model_name_label'),
            width=160,
            hint_text=self.textLocaled('model_name_hint'),
            options=[
                dropdown.Option(text='ColorBot', key='color'),
                dropdown.Option(text='NanoV10', key='yolo11n'),
                dropdown.Option(text='SmallV10', key='yolo11s'),
                dropdown.Option(text='MediumV10', key='yolov10m'),
                dropdown.Option(text='NanoV9', key='yolov9t'),
                dropdown.Option(text='SmallV9', key='yolov9s'),
                dropdown.Option(text='MediumV9', key='yolov9m'),
                dropdown.Option(text='NanoV8', key='yolov8n'),
                dropdown.Option(text='SmallV8', key='yolov8s'),
                dropdown.Option(text='MediumV8', key='yolov8m'),
                dropdown.Option(text='Best', key='best')
            ],
            value=self.settings.trigger_model_name,
            border_radius=border_radius.all(self.border_radius),
            on_change=lambda e: setattr(self.settings, 'trigger_model_name', e.control.value),
            col={'md': 6, 'lg': 5, 'xl': 4}
        )

        self.target_height = Slider(
            width=300,
            label='{value}%',
            min=0,
            max=100,
            divisions=100,
            value=int(self.settings.target_height * 100),
            on_change=lambda e: setattr(self.settings, 'target_height', e.control.value/100)
        )

        self.fov_width = TextField(
            label=self.textLocaled('fov_width_label'),
            hint_text=f'{self.textLocaled("example")}: 16',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            col={'sm': 5, 'md': 4, 'lg': 3}
        )

        self.fov_height = TextField(
            label=self.textLocaled('fov_height_label'),
            hint_text=f'{self.textLocaled("example")}: 9',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            col={'sm': 5, 'md': 4, 'lg': 3}
        )

        self.mouse2driver_translate = Switch(
            label=self.textLocaled('mouse2driver_translate_label'),
            value=self.settings.mouse2driver_translate,
            on_change=self.mouse2driver_change,
            disabled=False if 2 <= self.lic_type <= 3 else True
        )

        self.use_pid = Switch(
            label=self.textLocaled('use_pid_label'),
            value=self.settings.use_pid,
            on_change=self.use_pid_change
        )

        self.pidx_k = TextField(
            label=self.textLocaled('pidx_k_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.pidx_k}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.pidx_k),
            disabled=not self.settings.use_pid
        )

        self.pidy_k = TextField(
            label=self.textLocaled('pidy_k_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.pidy_k}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.pidy_k),
            disabled=not self.settings.use_pid
        )

        self.pidx_i = TextField(
            label=self.textLocaled('pidx_i_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.pidx_i}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.pidx_i),
            disabled=not self.settings.use_pid
        )

        self.pidy_i = TextField(
            label=self.textLocaled('pidy_i_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.pidy_i}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.pidy_i),
            disabled=not self.settings.use_pid
        )

        self.pidx_d = TextField(
            label=self.textLocaled('pidx_d_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.pidx_d}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.pidx_d),
            disabled=not self.settings.use_pid
        )

        self.pidy_d = TextField(
            label=self.textLocaled('pidy_d_label'),
            hint_text=f'{self.textLocaled("example")}: {self.settings.pidy_d}',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.pidy_d),
            disabled=not self.settings.use_pid
        )

        self.mouse_device = Dropdown(
            label=self.textLocaled('mouse_device_label'),
            hint_text=self.textLocaled('mouse_device_hint'),
            options=[
                dropdown.Option(
                    text=f'{hex(device[0])[2:].upper()}:{hex(device[1])[2:].upper()}',
                    key=str(device[0]) + ' ' + str(device[1])
                ) for device in get_devices()
            ],
            border_radius=border_radius.all(self.border_radius),
            on_change=self.mouse_device_change,
            disabled=not self.settings.mouse2driver_translate,
            # width=240
        )

        self.pid_interpolate = Switch(
            label=self.textLocaled('pid_interpolate_label'),
            value=self.settings.pid_interpolate,
            on_change=self.pid_interpolate_change
        )

        self.low_hsv_aim_btn = ElevatedButton(
            self.textLocaled('lower_bounbary'),
            bgcolor=self.settings.low_aim_color,
            color=colors.WHITE,
            height=60,
            width=145,
            on_click=self.open_color_picker,
            key='low_aim'
        )

        self.low_hsv_aim_dialog = flet.AlertDialog(
            content=self.low_aim_color_picker,
            actions=[
                flet.TextButton(self.textLocaled('okay'), key='low_aim', on_click=self.change_color),
                flet.TextButton(self.textLocaled('cancel'), key='low_aim', on_click=self.close_dialog)
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=self.close_dialog
        )
        self.low_hsv_aim_dialog.key = 'low_aim'

        self.high_hsv_aim_btn = ElevatedButton(
            self.textLocaled('upper_bounbary'),
            bgcolor=self.settings.high_aim_color,
            color=colors.BLACK,
            height=60,
            width=145,
            on_click=self.open_color_picker,
            key='high_aim'
        )

        self.high_hsv_aim_dialog = flet.AlertDialog(
            content=self.high_aim_color_picker,
            actions=[
                flet.TextButton(self.textLocaled('okay'), key='high_aim', on_click=self.change_color),
                flet.TextButton(self.textLocaled('cancel'), key='high_aim', on_click=self.close_dialog)
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=self.close_dialog
        )
        self.high_hsv_aim_dialog.key = 'high_aim'

        self.mouse_report_log = Switch(
            label=self.textLocaled('mouse_report_log_label'),
            value=self.settings.mouse_report_log,
            on_change=lambda e: setattr(self.settings, 'mouse_report_log', e.control.value),
            disabled=not self.settings.mouse_report_log
        )

        self.min_ratio = TextField(
            label=self.textLocaled('min_ratio_label'),
            hint_text=f'{self.textLocaled("example")}: 0.33',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.min_ratio)
        )

        self.max_ratio = TextField(
            label=self.textLocaled('max_ratio_label'),
            hint_text=f'{self.textLocaled("example")}: 0.93',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.max_ratio)
        )

        self.morph_iterations = TextField(
            label=self.textLocaled('morph_iterations_label'),
            hint_text=f'{self.textLocaled("example")}: 2',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.morph_iterations)
        )

        self.dilate_iterations = TextField(
            label=self.textLocaled('dilate_iterations_label'),
            hint_text=f'{self.textLocaled("example")}: 6',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.dilate_iterations)
        )

        self.morph_kernel = TextField(
            label=self.textLocaled('morph_kernel_label'),
            hint_text=f'{self.textLocaled("example")}: 3 3',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.kernel_change,
            value=' '.join(list(map(lambda x: str(x), self.settings.morph_kernel))),
            width=140
        )

        self.dilate_kernel = TextField(
            label=self.textLocaled('dilate_kernel_label'),
            hint_text=f'{self.textLocaled("example")}: 17 3',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.kernel_change,
            value=' '.join(list(map(lambda x: str(x), self.settings.dilate_kernel))),
            width=140
        )

        self.alternative_parser = Switch(
            label=self.textLocaled('alternative_parser_label'),
            value=self.settings.alternative_parser,
            on_change=lambda e: setattr(self.settings, 'alternative_parser', e.control.value)
        )

        self.color_trigger_mode = Dropdown(
            label=self.textLocaled('color_trigger_mode_label'),
            hint_text=self.textLocaled('color_trigger_mode_hint'),
            border_radius=border_radius.all(self.border_radius),
            options=[
                dropdown.Option(
                    text=self.textLocaled('color_trigger_mode_bbox'),
                    key='bbox'
                ),
                dropdown.Option(
                    text=self.textLocaled('color_trigger_mode_color'),
                    key='color'
                ),
                dropdown.Option(
                    text=self.textLocaled('color_trigger_mode_pixel'),
                    key='pixel'
                )
            ],
            value=self.settings.color_trigger_mode,
            width=300,
            on_change=self.color_trigger_mode_change
            # on_change=lambda e: setattr(self.settings, 'color_trigger_mode', e.control.value)
        )

        self.low_hsv_trigger_btn = ElevatedButton(
            self.textLocaled('lower_bounbary'),
            bgcolor=self.settings.low_trigger_color,
            color=colors.WHITE,
            height=60,
            width=145,
            on_click=self.open_color_picker,
            key='low_trigger'
        )

        self.low_hsv_trigger_dialog = flet.AlertDialog(
            content=self.low_trigger_color_picker,
            actions=[
                flet.TextButton(self.textLocaled('okay'), key='low_trigger', on_click=self.change_color),
                flet.TextButton(self.textLocaled('cancel'), key='low_trigger', on_click=self.close_dialog)
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=self.close_dialog
        )
        self.low_hsv_trigger_dialog.key = 'low_trigger'

        self.high_hsv_trigger_btn = ElevatedButton(
            self.textLocaled('upper_bounbary'),
            bgcolor=self.settings.high_trigger_color,
            color=colors.BLACK,
            height=60,
            width=145,
            on_click=self.open_color_picker,
            key='high_trigger'
        )

        self.high_hsv_trigger_dialog = flet.AlertDialog(
            content=self.high_trigger_color_picker,
            actions=[
                flet.TextButton(self.textLocaled('okay'), key='high_trigger', on_click=self.change_color),
                flet.TextButton(self.textLocaled('cancel'), key='high_trigger', on_click=self.close_dialog)
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=self.close_dialog
        )
        self.high_hsv_trigger_dialog.key = 'high_trigger'

        self.min_ratio_trigger = TextField(
            label=self.textLocaled('min_ratio_label'),
            hint_text=f'{self.textLocaled("example")}: 0.33',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.min_ratio_trigger)
        )

        self.max_ratio_trigger = TextField(
            label=self.textLocaled('max_ratio_label'),
            hint_text=f'{self.textLocaled("example")}: 0.93',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.max_ratio_trigger)
        )

        self.morph_iterations_trigger = TextField(
            label=self.textLocaled('morph_iterations_label'),
            hint_text=f'{self.textLocaled("example")}: 1',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.morph_iterations_trigger)
        )

        self.dilate_iterations_trigger = TextField(
            label=self.textLocaled('dilate_iterations_label'),
            hint_text=f'{self.textLocaled("example")}: 2',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.dilate_iterations_trigger)
        )

        self.morph_kernel_trigger = TextField(
            label=self.textLocaled('morph_kernel_label'),
            hint_text=f'{self.textLocaled("example")} (y x): 2 2',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.kernel_change,
            value=' '.join(list(map(lambda x: str(x), self.settings.morph_kernel_trigger)))
        )

        self.dilate_kernel_trigger = TextField(
            label=self.textLocaled('dilate_kernel_label'),
            hint_text=f'{self.textLocaled("example")} (y x): 2 2',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.kernel_change,
            value=' '.join(list(map(lambda x: str(x), self.settings.dilate_kernel_trigger)))
        )

        self.changed_pixels = TextField(
            label=self.textLocaled('changed_pixels_label'),
            hint_text=f'{self.textLocaled("example")}: 3',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.changed_pixels),
            col={'md': 6, 'lg': 5, 'xl': 4}
        )

        self.trigger_zone = TextField(
            label=self.textLocaled('trigger_zone_label'),
            hint_text=f'{self.textLocaled("example")} (x y): 6 4',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.kernel_change,
            value=' '.join(list(map(lambda x: str(x), self.settings.trigger_zone))),
            col={'md': 6, 'lg': 5, 'xl': 4}
        )

        self.trigger_burst_mode = Switch(
            label=self.textLocaled('trigger_burst_mode_label'),
            value=self.settings.trigger_burst_mode,
            on_change=self.trigger_burst_change
        )

        self.trigger_burst_count = TextField(
            label=self.textLocaled('trigger_burst_count_label'),
            hint_text=f'{self.textLocaled("example")}: 4',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.trigger_burst_count),
            disabled=not self.settings.trigger_burst_mode
        )

        self.trigger_pixel_thresh = TextField(
            label=self.textLocaled('trigger_pixel_thresh_label'),
            hint_text=f'{self.textLocaled("example")}: 25',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.trigger_pixel_thresh),
        )

        self.trigger_cooldown = TextField(
            label=self.textLocaled('trigger_cooldown_label'),
            hint_text=f'{self.textLocaled("example_ms")}: 200',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.trigger_cooldown),
        )

        self.trigger_cooldown_dispersion = TextField(
            label=self.textLocaled('trigger_cooldown_dispersion_label'),
            hint_text=f'{self.textLocaled("example")}: 20',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.trigger_cooldown_dispersion),
        )

        self.color_menu_aim = Dropdown(
            label=self.textLocaled('color_menu_label'),
            hint_text=self.textLocaled('color_menu_hint'),
            border_radius=border_radius.all(self.border_radius),
            options=[
                dropdown.Option(
                    text=self.textLocaled('color_menu_purple'),
                    key='purple_aim'
                ),
                dropdown.Option(
                    text=self.textLocaled('color_menu_green'),
                    key='green_aim'
                ),
                dropdown.Option(
                    text=self.textLocaled('color_menu_yellow'),
                    key='yellow_aim'
                )
            ],
            value=None,
            width=300,
            on_change=self.color_menu_change
        )

        self.color_menu_trigger = Dropdown(
            label=self.textLocaled('color_menu_label'),
            hint_text=self.textLocaled('color_menu_hint'),
            border_radius=border_radius.all(self.border_radius),
            options=[
                dropdown.Option(
                    text=self.textLocaled('color_menu_purple'),
                    key='purple_trigger'
                ),
                dropdown.Option(
                    text=self.textLocaled('color_menu_green'),
                    key='green_trigger'
                ),
                dropdown.Option(
                    text=self.textLocaled('color_menu_yellow'),
                    key='yellow_trigger'
                )
            ],
            value=None,
            width=300,
            on_change=self.color_menu_change
        )

        self.flick_aim = Switch(
            label=self.textLocaled('flick_aim_label'),
            value=self.settings.flick_aim,
            on_change=lambda e: setattr(self.settings, 'flick_aim', e.control.value)
        )

        self.static_height_offset = TextField(
            label=self.textLocaled('static_height_offset_label'),
            hint_text=f'{self.textLocaled("example")}: -3',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.normal_change_int,
            value=str(self.settings.static_height_offset),
        )

        self.predict_x = Switch(
            label=f'{self.textLocaled("predict_label")} X',
            value=self.settings.predict_x,
            on_change=lambda e: setattr(self.settings, 'predict_x', e.control.value)
        )

        self.predict_y = Switch(
            label=f'{self.textLocaled("predict_label")} Y',
            value=self.settings.predict_y,
            on_change=lambda e: setattr(self.settings, 'predict_y', e.control.value)
        )

        self.prediction_x = TextField(
            label=f'{self.textLocaled("prediction_label")} X',
            hint_text=f'{self.textLocaled("example_degrees")}: 4',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.prediction_x),
        )

        self.prediction_y = TextField(
            label=f'{self.textLocaled("prediction_label")} Y',
            hint_text=f'{self.textLocaled("example_degrees")}: 2',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.prediction_y),
        )

        self.damping_y = TextField(
            label=f'{self.textLocaled("damping_label")} Y',
            hint_text=f'{self.textLocaled("example_degrees")}: 0.25',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.damping_y),
        )

        self.damping_x = TextField(
            label=f'{self.textLocaled("damping_label")} X',
            hint_text=f'{self.textLocaled("example_degrees")}: 0.4',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.damping_x),
        )

        self.damping_power_x = TextField(
            label=f'{self.textLocaled("damping_power_label")} X',
            hint_text=f'{self.textLocaled("example")}: 1',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.damping_power_x),
        )

        self.damping_power_y = TextField(
            label=f'{self.textLocaled("damping_power_label")} Y',
            hint_text=f'{self.textLocaled("example")}: 1',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_float,
            value=str(self.settings.damping_power_y),
        )

        self.dynamic_height = Switch(
            label=self.textLocaled('dynamic_height_label'),
            value=self.settings.trigger_burst_mode,
            on_change=lambda e: setattr(self.settings, 'dynamic_height', e.control.value)
        )

        self.driver_priority = Switch(
            label=self.textLocaled('driver_priority_label'),
            value=self.settings.driver_priority,
            on_change=lambda e: setattr(self.settings, 'driver_priority', e.control.value),
            disabled=not self.settings.driver_priority
        )

        self.mouse_c_ip = TextField(
            label=self.textLocaled('mouse_c_ip_label'),
            hint_text=f'{self.textLocaled("example")}: 10.55.0.5',
            border_radius=border_radius.all(self.border_radius),
            on_change=lambda e: setattr(self.settings, 'mouse_c_ip', e.control.value),
            value=self.settings.mouse_c_ip,
            disabled=not self.settings.mouse_proxy_manual
        )

        self.mouse_l_ip = TextField(
            label=self.textLocaled('mouse_l_ip_label'),
            hint_text=f'{self.textLocaled("example")}: 10.55.0.1',
            border_radius=border_radius.all(self.border_radius),
            on_change=lambda e: setattr(self.settings, 'mouse_l_ip', e.control.value),
            value=self.settings.mouse_l_ip,
            disabled=not self.settings.mouse_proxy_manual
        )

        self.mouse_l_port = TextField(
            label=self.textLocaled('mouse_l_port_label'),
            hint_text=f'{self.textLocaled("example")}: 13371',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.mouse_l_port),
            disabled=not self.settings.mouse_proxy_manual
        )

        self.mouse_proxy_manual = Switch(
            label=self.textLocaled('mouse_proxy_manual_label'),
            value=self.settings.mouse_proxy_manual,
            on_change=self.mouse_proxy_manual_change
        )

        self.core_priority = Dropdown(
            label=self.textLocaled('core_priority_label'),
            hint_text=self.textLocaled('core_priority_hint'),
            border_radius=border_radius.all(self.border_radius),
            options=[
                dropdown.Option(
                    text=self.textLocaled('high_priority'),
                    key=HIGH_PRIORITY_CLASS
                ),
                dropdown.Option(
                    text=self.textLocaled('above_normal_priority'),
                    key=ABOVE_NORMAL_PRIORITY_CLASS
                ),
                dropdown.Option(
                    text=self.textLocaled('normal_priority'),
                    key=NORMAL_PRIORITY_CLASS
                ),
                dropdown.Option(
                    text=self.textLocaled('below_normal_priority'),
                    key=BELOW_NORMAL_PRIORITY_CLASS,
                ),
                dropdown.Option(
                    text=self.textLocaled('idle_priority'),
                    key=IDLE_PRIORITY_CLASS,
                )
            ],
            value=self.settings.core_priority,
            width=300,
            on_change=lambda e: setattr(self.settings, 'core_priority', int(e.control.value))
        )

        self.accumulate_mouse_movement = Switch(
            label=self.textLocaled('accumulate_mouse_movement_label'),
            value=self.settings.accumulate_mouse_movement,
            on_change=lambda e: setattr(self.settings, 'accumulate_mouse_movement', e.control.value),
            disabled=not self.settings.mouse2driver_translate
        )

        self.ragebot_max_flick = TextField(
            label=self.textLocaled('ragebot_max_flick_label'),
            hint_text=f'{self.textLocaled("example")}: 127',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.ragebot_max_flick)
        )

        self.ragebot_flick_time = TextField(
            label=self.textLocaled('ragebot_flick_time_label'),
            hint_text=f'{self.textLocaled("example_ms")}: 40',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.ragebot_flick_time)
        )

        self.ragebot_retract_time = TextField(
            label=self.textLocaled('ragebot_retract_time_label'),
            hint_text=f'{self.textLocaled("example_ms")}: 10',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.ragebot_retract_time)
        )

        self.ragebot_cooldown_time = TextField(
            label=self.textLocaled('ragebot_cooldown_time_label'),
            hint_text=f'{self.textLocaled("example_ms")}: 110',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.ragebot_cooldown_time)
        )

        self.use_centroids = Switch(
            label=self.textLocaled('use_centroids_label'),
            value=self.settings.use_centroids,
            on_change=self.use_centroids_change
        )

        self.centroids_thresh = Slider(
            width=300,
            label='{value}%',
            min=0,
            max=100,
            divisions=100,
            value=int(self.settings.centroids_thresh * 100),
            on_change=lambda e: setattr(self.settings, 'centroids_thresh', e.control.value/100)
        )

        self.wait_stop_moving = Switch(
            label=self.textLocaled('wait_stop_moving_label'),
            value=self.settings.wait_stop_moving,
            on_change=self.wait_stop_moving_change
        )

        self.stop_moving_time = TextField(
            label=self.textLocaled('stop_moving_time_label'),
            hint_text=f'{self.textLocaled("example_ms")}: 150',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.text_field_change_int,
            value=str(self.settings.stop_moving_time),
            disabled=not self.settings.wait_stop_moving
        )

        self.trigger_hit_chance = Slider(
            width=300,
            label='{value}%',
            min=0,
            max=100,
            divisions=100,
            value=self.settings.trigger_hit_chance,
            on_change=lambda e: setattr(self.settings, 'trigger_hit_chance', e.control.value)
        )

        self.mouse_report_changes_text = Text('0   0   0   0   0   0', text_align=TextAlign.CENTER, size=24)
        
        self.mouse_interface = TextField(
            label=self.textLocaled('mouse_interface_label'),
            hint_text=f'{self.textLocaled("mouse_interface_example")}: -1',
            border_radius=border_radius.all(self.border_radius),
            on_change=self.normal_change_int,
            value='-1',
            width=100
        )

        self.mouse_report_changes_btn = ElevatedButton(
            self.textLocaled('mouse_report_changes_btn_text'),
            on_click=self.get_mouse_report_changes
        )

        self.mouse_manual_parse = Switch(
            label=self.textLocaled('mouse_manual_parse_label'),
            value=self.settings.mouse_manual_parse,
            on_change=self.mouse_manual_parse_change
        )

        self.mouse_manual_parse_textfield = TextField(
            label=self.textLocaled('mouse_manual_parse_textfield_label'),
            hint_text=self.textLocaled('mouse_manual_parse_textfield_hint'),
            border_radius=border_radius.all(self.border_radius),
            on_change=self.mouse_manual_parse_textfield_change,
            multiline=True,
            min_lines=1,
            max_lines=3,
            disabled=not self.settings.mouse_manual_parse,
            value="""{\n    "move_xy_offset": 1,\n    "move_xy_size": 4,\n    "scroll_offset": 4,\n    "scroll_size": 1,\n    "buttons_offset": 5,\n    "buttons_count": 8\n}"""
        )

        self.mouse_device_config_dlg = flet.AlertDialog(
            modal=False,
            title=Text(self.textLocaled('mouse_device_config_dlg_title')),
            content=Column(
                controls=[
                    Text(self.textLocaled('mouse_report_changes_label')),
                    self.mouse_report_changes_text,
                    Row(
                        controls=[
                            self.mouse_interface,
                            self.mouse_report_changes_btn
                        ],
                        spacing=60,
                        alignment=MainAxisAlignment.CENTER,
                        width=280
                    ),
                    Row(
                        controls=[
                            self.mouse_manual_parse,
                            flet.IconButton(
                                icons.RESTART_ALT_ROUNDED, 
                                on_click=self.reset_mouse_manual_parse_textfield
                            ),
                            flet.IconButton(
                                icons.SETTINGS_ROUNDED, 
                                on_click=self.configure_libusb
                            )
                        ],
                        spacing=30,
                        alignment=MainAxisAlignment.CENTER
                    ),
                    # self.mouse_manual_parse,
                    self.mouse_manual_parse_textfield
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=20,
                height=300
            ),
            on_dismiss=lambda e: self.page.close(self.mouse_device_config_dlg)
        )

        self.hookmanager_api = Dropdown(
            label=self.textLocaled('hookmanager_api_label'),
            hint_text=self.textLocaled('hookmanager_api_hint'),
            border_radius=border_radius.all(self.border_radius),
            options=[
                dropdown.Option(
                    text='PyWinHook',
                    key='winhook'
                ),
                dropdown.Option(
                    text='Pynput',
                    key='pynput'
                )
            ],
            value=self.settings.hookmanager_api,
            width=300,
            on_change=self.hookmanager_api_change
        )

        self.hookmanager_api_dlg = flet.AlertDialog(
            modal=False,
            title=Text(self.textLocaled('hookmanager_api_dlg_title'), text_align=TextAlign.CENTER, color="#ba2c4c"),
            content=Text(self.textLocaled('hookmanager_api_dlg_content')),
            on_dismiss=lambda e: self.page.close(self.hookmanager_api_dlg)
        )

        self.spoof_btn = ElevatedButton(
            text=self.textLocaled('spoof_btn_text'),
            on_click=self.spoof_signatures
        )

        self.spoof_btn_dlg = flet.AlertDialog(
            modal=False,
            title=Text(self.textLocaled('spoof_btn_dlg_title'), text_align=TextAlign.CENTER, color="#ba2c4c"),
            content=Text(self.textLocaled('spoof_btn_dlg_content')),
            on_dismiss=lambda e: self.page.close(self.spoof_btn_dlg)
        )

        self.detection_cls_1 = flet.Checkbox(
            value=0 in self.settings.detection_classes,
            label='T1_B',
            on_change=self.detection_cls_change
        )

        self.detection_cls_2 = flet.Checkbox(
            value=1 in self.settings.detection_classes,
            label='T1_H',
            on_change=self.detection_cls_change
        )

        self.detection_cls_3 = flet.Checkbox(
            value=2 in self.settings.detection_classes,
            label='T2_B',
            on_change=self.detection_cls_change
        )

        self.detection_cls_4 = flet.Checkbox(
            value=3 in self.settings.detection_classes,
            label='T2_H',
            on_change=self.detection_cls_change
        )

        self.detection_cls_map = {
            'T1_B': 0,
            'T1_H': 1,
            'T2_B': 2,
            'T2_H': 3
        }

        try:
            core_sign = self.get_signature('core.pyc')
        except:
            core_sign = 'ERROR'
        try:
            app_sign = self.get_signature('app.pyc')
        except:
            app_sign = 'ERROR'

        self.core_launcher_signature_text = Text(f'Core: {core_sign}', size=20)
        self.app_launcher_signature_text = Text(f'App: {app_sign}', size=20)

        self.high_hsv_trigger_btn.disabled = False
        self.low_hsv_trigger_btn.disabled = False
        self.morph_kernel_trigger.disabled = True
        self.dilate_kernel_trigger.disabled = True
        self.morph_iterations_trigger.disabled = True
        self.dilate_iterations_trigger.disabled = True
        self.min_ratio_trigger.disabled = True
        self.max_ratio_trigger.disabled = True
        self.trigger_zone.disabled = False
        self.changed_pixels.disabled = False
        self.trigger_pixel_thresh.disabled = True

        # ==============================================================================================================
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # ==============================================================================================================

        self.main_content = Column(
            expand=1,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                Row(
                    [
                        Text(self.textLocaled('activated_until_main'), size=26, text_align=TextAlign.CENTER),
                        Text(date, size=26, text_align=TextAlign.CENTER, color='#2aae4f')
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    wrap=True
                ),
                Row(
                    [
                        Text(self.textLocaled('driver_supported_main'), size=26, text_align=TextAlign.CENTER),
                        Text(self.lic_tiers[self.lic_type], size=26, text_align=TextAlign.CENTER, color='#bf2c4c')
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    wrap=True
                ),
                Row(
                    [
                        Row(
                            [
                                # Text('Конфиг:', size=20, text_align=TextAlign.CENTER),
                                flet.IconButton(icons.RESTART_ALT_ROUNDED, on_click=self.update_config_dropdown),
                                self.config_menu,
                                ElevatedButton(self.textLocaled('save_btn_main'), on_click=self.save_config),
                                ElevatedButton(self.textLocaled('load_btn_main'), on_click=self.load_config),
                            ],
                            wrap=True
                        ),
                        self.game_select
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    wrap=True,
                    spacing=140
                ),
                ResponsiveRow(
                    [
                        self.sensitivity,
                        self.full_rotate,
                        self.fov
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND
                ),
                ResponsiveRow(
                    [
                        self.fov_width,
                        self.fov_height
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND
                ),
                Divider(thickness=3),
                Text(self.textLocaled('control_panel_main'), size=26, text_align=TextAlign.CENTER),
                Row(
                    [
                        Container(
                            Row(
                                [
                                    Column(
                                        [
                                            ElevatedButton(content=Text(self.textLocaled('start_btn_main'), size=16, text_align=TextAlign.CENTER, width=67,
                                                                        font_family='Multiround'), on_click=self.start_core,
                                                           bgcolor='#2aae4f', color='#ffffff'),
                                            Container(height=20),
                                            ElevatedButton(content=Text(self.textLocaled('stop_btn_main'), size=16, text_align=TextAlign.CENTER, width=67,
                                                                        font_family='Multiround'), on_click=self.stop_core,
                                                           bgcolor='#ba2c4c', color='#ffffff'),
                                            Container(height=20),
                                            ElevatedButton(
                                                content=Text(self.textLocaled('restart_btn_main'), size=14, text_align=TextAlign.CENTER, width=67,
                                                             font_family='Multiround'), on_click=self.restart_core,
                                                bgcolor='#2a97ae', color='#ffffff')
                                        ],
                                        horizontal_alignment=CrossAxisAlignment.CENTER,
                                        alignment=MainAxisAlignment.SPACE_AROUND,
                                        # expand=True,
                                        spacing=40
                                    ),
                                    self.core_ran_text
                                ],
                                alignment=MainAxisAlignment.SPACE_AROUND
                            ),
                            padding=0,
                            expand=True
                        ),
                        Container(
                            self.core_state_field,
                            border_radius=15,
                            width=250,
                            bgcolor='#000000'
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    # spacing=80
                )
            ]
        )

        self.neural_content = Column(
            expand=1,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                Text(self.textLocaled('basic_settings_neural'), size=26, text_align=TextAlign.CENTER),
                ResponsiveRow(
                    [
                        Column(
                            controls=[
                                Row(
                                    controls=[
                                        Column(
                                            controls=[
                                                self.screen_width,
                                                self.screen_height,
                                            ],
                                            alignment=MainAxisAlignment.CENTER,
                                            expand=True
                                        ),
                                        flet.IconButton(
                                            icons.RESTART_ALT_ROUNDED, 
                                            on_click=self.update_screen_metrics
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.CENTER,
                                    vertical_alignment=CrossAxisAlignment.CENTER,
                                    expand=True
                                    # spacing=15
                                ),
                                self.screen_handler_fps,
                                self.screen_handler_fps_check,
                            ],
                            expand=1,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            alignment=MainAxisAlignment.CENTER
                        ),
                        Column(
                            controls=[
                                self.neural_input_area_size,
                                self.gpu_select,
                                self.cudart_select,
                            ],
                            expand=1,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            alignment=MainAxisAlignment.CENTER
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                ResponsiveRow(
                    [
                        self.aim_model_name,
                        self.trigger_model_name
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                Divider(height=3, thickness=3),
                Text(self.textLocaled('advanced_settings_neural'), size=26, text_align=TextAlign.CENTER),
                ResponsiveRow(
                    [
                        Column(
                            controls=[
                                Text('iou_thres', text_align=TextAlign.CENTER),
                                self.iou_thres,
                                Text('conf_thres', text_align=TextAlign.CENTER),
                                self.conf_thres,
                                Text('topk', text_align=TextAlign.CENTER),
                                self.topk,
                            ],
                            expand=1,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            alignment=MainAxisAlignment.CENTER,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            spacing=5
                        ),
                        Column(
                            controls=[
                                Text(self.textLocaled('advanced_settings_classes'), text_align=TextAlign.CENTER, size=16),
                                Row(
                                    controls=[
                                        self.detection_cls_1,
                                        self.detection_cls_2,
                                        self.detection_cls_3,
                                        self.detection_cls_4
                                    ],
                                    alignment=MainAxisAlignment.CENTER,
                                    vertical_alignment=CrossAxisAlignment.CENTER,
                                    spacing=10
                                ),
                                self.core_priority,
                                self.use_dxcam
                            ],
                            expand=1,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            alignment=MainAxisAlignment.CENTER,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            spacing=15
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                )
            ]
        )

        self.mouse_content = Column(
            expand=1,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                Text(self.textLocaled('mouse_settings_mouse'), size=26, text_align=TextAlign.CENTER),
                Divider(
                    thickness=3,
                    height=3
                ),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.START,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.mouse2driver_translate,
                                self.driver_priority,
                                self.accumulate_mouse_movement,
                                # self.alternative_parser,
                                self.mouse_report_log
                            ]
                        ),
                        # Column(
                        #     expand=1,
                        #     horizontal_alignment=CrossAxisAlignment.CENTER,
                        #     alignment=MainAxisAlignment.CENTER,
                        #     col={'md': 6, 'lg': 5, 'xl': 4},
                        #     controls=[
                        #         self.mouse_driver,
                        #         Row(
                        #             [
                        #                 self.mouse_device,
                        #                 flet.IconButton(icons.RESTART_ALT_ROUNDED, on_click=self.update_mouse_devices),
                        #                 flet.IconButton(icons.SETTINGS_ROUNDED, on_click=self.configure_libusb)
                        #             ],
                        #             alignment=MainAxisAlignment.CENTER,
                        #             # spacing=10,
                        #             expand=True
                        #         ),
                        #         self.interpolation_filter_refresh_rate
                        #     ]
                        # ),
                        Column(
                            expand=True,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.mouse_driver,
                                Row(
                                    controls=[
                                        Column(
                                            controls=[
                                                self.mouse_device
                                            ],
                                            alignment=MainAxisAlignment.CENTER,
                                            horizontal_alignment=CrossAxisAlignment.CENTER,
                                            expand=True
                                        ),
                                        flet.IconButton(
                                            icons.RESTART_ALT_ROUNDED, 
                                            on_click=self.update_mouse_devices
                                        ),
                                        flet.IconButton(
                                            icons.SETTINGS_ROUNDED, 
                                            # on_click=self.configure_libusb
                                            on_click=lambda e: self.page.open(self.mouse_device_config_dlg)
                                        )
                                    ],
                                    alignment=MainAxisAlignment.CENTER,
                                    expand=True
                                ),
                                self.interpolation_filter_refresh_rate
                            ],
                            spacing=20,  # добавляем вертикальный отступ между элементами колонки,
                            # expand=True
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                Row(
                                    [
                                        ElevatedButton(content=Text(self.textLocaled('power_off_btn_mouse'), size=12, text_align=TextAlign.CENTER,
                                                                    width=90, font_family='Multiround'),
                                                       on_click=self.lunarbox_action, key='shutdown', bgcolor='#ba2c4c',
                                                       color='#ffffff'),
                                        ElevatedButton(content=Text(self.textLocaled('restart_btn_mouse'), size=13, text_align=TextAlign.CENTER,
                                                                    width=90, font_family='Multiround'),
                                                       on_click=self.lunarbox_action, key='reboot', bgcolor='#ba2c4c',
                                                       color='#ffffff')
                                    ],
                                    alignment=MainAxisAlignment.SPACE_AROUND
                                ),
                                Divider(thickness=1, height=3),
                                self.mouse_c_ip,
                                # self.mouse_l_ip,
                                # self.mouse_l_port,
                                self.mouse_proxy_manual,
                            ]
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                )
            ]
        )

        self.aim_content = Column(
            expand=1,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                Text(self.textLocaled('curve_aim'), size=26, text_align=TextAlign.CENTER),
                Container(
                    padding=0,
                    margin=margin.only(20, 20, 80, 10),
                    content=self.nonlinear_aim_chart
                ),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.detect_distance_x,
                                self.smooth,
                                self.nonlinear_aim,
                                self.nonlinear_k,
                                self.nonlinear_b,
                                self.nonlinear_i
                            ]
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.detect_distance_y,
                                Column(
                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                    alignment=MainAxisAlignment.CENTER,
                                    col={'md': 6, 'lg': 5, 'xl': 4},
                                    controls=[
                                        Text(self.textLocaled('target_height_text_aim')),
                                        self.target_height
                                    ],
                                    spacing=0
                                ),
                                self.static_height_offset,
                                Column(
                                    horizontal_alignment=CrossAxisAlignment.START,
                                    alignment=MainAxisAlignment.CENTER,
                                    col={'md': 6, 'lg': 5, 'xl': 4},
                                    controls=[
                                        self.dynamic_height,
                                        self.flick_aim,
                                        self.use_pid
                                    ]
                                )
                            ]
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.pidx_k,
                                self.pidx_i,
                                self.pidx_d
                            ]
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.pidy_k,
                                self.pidy_i,
                                self.pidy_d
                            ]
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.predict_x,
                                self.prediction_x,
                                self.damping_x,
                                self.damping_power_x
                            ]
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.predict_y,
                                self.prediction_y,
                                self.damping_y,
                                self.damping_power_y
                            ]
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                Divider(thickness=3, height=3),
                Text(self.textLocaled('colorbot_aim'), size=26, text_align=TextAlign.CENTER),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.color_menu_aim,
                                Row(
                                    [
                                        Container(
                                            padding=15,
                                            margin=margin.only(20, 20, 20, 0),
                                            bgcolor='#1f1f1f',
                                            border_radius=border_radius.all(30),
                                            content=Column(
                                                controls=[
                                                    Text('  ' + self.textLocaled('color_range_text')),
                                                    self.high_hsv_aim_btn,
                                                    self.low_hsv_aim_btn
                                                ],
                                                alignment=MainAxisAlignment.CENTER
                                            )
                                        ),
                                        Column(
                                            controls=[
                                                self.morph_kernel,
                                                self.dilate_kernel,
                                                self.use_centroids
                                            ],
                                            alignment=MainAxisAlignment.CENTER
                                        )
                                    ],
                                    spacing=0,
                                    alignment=MainAxisAlignment.SPACE_AROUND,
                                    vertical_alignment=CrossAxisAlignment.CENTER
                                )
                            ]
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.morph_iterations,
                                self.dilate_iterations,
                                Column(
                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                    alignment=MainAxisAlignment.CENTER,
                                    col={'md': 6, 'lg': 5, 'xl': 4},
                                    controls=[
                                        Text(self.textLocaled('centroids_text_aim')),
                                        self.centroids_thresh
                                    ],
                                    spacing=0
                                ),
                                self.min_ratio,
                                self.max_ratio
                            ],
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                Divider(thickness=3, height=3),
                Text(self.textLocaled('ragebot_text_aim'), size=30, text_align=TextAlign.CENTER),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.ragebot_max_flick,
                                self.ragebot_cooldown_time
                            ]
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.ragebot_flick_time,
                                self.ragebot_retract_time
                            ]
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                )
            ]
        )

        self.trigger_content = Column(
            expand=1,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                Text(self.textLocaled('prob_distr_trigger'), size=26, text_align=TextAlign.CENTER),
                Container(
                    padding=0,
                    margin=margin.only(20, 20, 80, 10),
                    content=self.normal_chart,
                ),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.trigger_reaction,
                                self.trigger_duration,
                                self.trigger_cooldown,
                                Column(
                                    horizontal_alignment=CrossAxisAlignment.START,
                                    alignment=MainAxisAlignment.CENTER,
                                    col={'md': 6, 'lg': 5, 'xl': 4},
                                    controls=[
                                        self.trigger_burst_mode,
                                        self.wait_stop_moving
                                    ]
                                ),
                                Column(
                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                    alignment=MainAxisAlignment.CENTER,
                                    col={'md': 6, 'lg': 5, 'xl': 4},
                                    controls=[
                                        Text(self.textLocaled('hit_chance_text_trigger')),
                                        self.trigger_hit_chance
                                    ],
                                    spacing=0
                                )
                            ]
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.trigger_reaction_dispersion,
                                self.trigger_duration_dispersion,
                                self.trigger_cooldown_dispersion,
                                self.trigger_burst_count,
                                self.stop_moving_time
                            ]
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                Divider(thickness=3, height=3),
                Text(self.textLocaled('colorbot_trigger'), size=26, text_align=TextAlign.CENTER),
                Row(
                    [
                        Container(
                            padding=15,
                            margin=margin.only(20, 20, 20, 0),
                            bgcolor='#1f1f1f',
                            border_radius=border_radius.all(30),
                            content=Column(
                                controls=[
                                    Text('  ' + self.textLocaled('color_range_text')),
                                    self.high_hsv_trigger_btn,
                                    self.low_hsv_trigger_btn
                                ],
                                alignment=MainAxisAlignment.CENTER
                            )
                        ),
                        Column(
                            [
                                self.color_trigger_mode,
                                self.color_menu_trigger
                            ],
                            alignment=MainAxisAlignment.CENTER
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                Divider(thickness=1, height=3),
                Text(self.textLocaled('bbox_trigger'), size=24, text_align=TextAlign.CENTER),
                ResponsiveRow(
                    [
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.morph_kernel_trigger,
                                self.dilate_kernel_trigger,
                                self.morph_iterations_trigger,
                                self.dilate_iterations_trigger
                            ]
                        ),
                        Column(
                            expand=1,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            col={'md': 6, 'lg': 5, 'xl': 4},
                            controls=[
                                self.min_ratio_trigger,
                                self.max_ratio_trigger
                            ]
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                Divider(thickness=1, height=3),
                Text(self.textLocaled('color_px_change_trigger'), size=24, text_align=TextAlign.CENTER),
                ResponsiveRow(
                    [
                        self.changed_pixels,
                        self.trigger_zone
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                Row(
                    [
                        self.trigger_pixel_thresh
                    ],
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.CENTER
                )
            ]
        )

        self.bindings_rows_update()

        self.bindings_content = Column(
            expand=1,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                Text(self.textLocaled('bindings_settings_text'), size=26, text_align=TextAlign.CENTER),
                Divider(height=3, thickness=3),
                self.hookmanager_api,
                ElevatedButton(
                    text=self.textLocaled('add_btn_bindings'),
                    width=170,
                    on_click=self.add_binding_row
                ),
                *self.bindings_rows
            ]
        )

        self.spoofer_content = Column(
            expand=1,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                self.app_launcher_signature_text,
                self.core_launcher_signature_text,
                Divider(height=3, thickness=3),
                self.spoof_btn
                # Text(self.textLocaled('bindings_settings_text'), size=26, text_align=TextAlign.CENTER),
                # Divider(height=3, thickness=3),
                # self.hookmanager_api,
                # ElevatedButton(
                #     text=self.textLocaled('add_btn_bindings'),
                #     width=170,
                #     on_click=self.add_binding_row
                # ),
                # *self.bindings_rows
            ]
        )

        # ==============================================================================================================
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # ==============================================================================================================

    # @staticmethod
    # def on_keyboard(e: flet.KeyboardEvent):
    #     print(f'Keyboard key pressed: {e.key} {e.alt} {e.ctrl} {e.shift} {e.meta}')

    # def bindings_action_change(self, e):
    #     key = e.control.key_name
    #     self.settings.keyboard_events[key] = e.control.value

    @staticmethod
    def get_signature(pyc_filename: str) -> str:
        with open(pyc_filename, 'rb') as file:
            data = file.read()

        return data[UUID_OFFSET:UUID_OFFSET+UUID_LEN].decode()
    
    @staticmethod
    def change_signature(pyc_filename: str) -> str:
        try:
            uuid.uuid4()
        except NameError:
            import uuid
        
        sign = uuid.uuid4().hex
        
        with open(pyc_filename, 'rb') as file:
            data = file.read()
        
        new_data = data[:UUID_OFFSET]
        new_data += sign.encode()
        new_data += data[UUID_OFFSET+UUID_LEN:]

        with open(pyc_filename, 'wb') as file:
            file.write(new_data)
        
        del new_data, data
        return sign

    def spoof_signatures(self, e):
        app_changed = self.change_signature('app.pyc')
        core_changed = self.change_signature('core.pyc')

        try:
            core_sign = self.get_signature('core.pyc')
        except:
            core_sign = 'ERROR'
        try:
            app_sign = self.get_signature('app.pyc')
        except:
            app_sign = 'ERROR'
        
        if app_changed != app_sign:
            print(f'[F] [App]: Spoof App ERROR ({app_changed}) ({app_sign})')
        if core_changed != core_sign:
            print(f'[F] [App]: Spoof Core ERROR ({core_changed}) ({core_sign})')

        self.core_launcher_signature_text.value = f'Core: {core_sign}'
        self.app_launcher_signature_text.value = f'App: {app_sign}'
        self.core_launcher_signature_text.update()
        self.app_launcher_signature_text.update()

        self.page.open(self.spoof_btn_dlg)

    def update_screen_metrics(self, e):
        self.settings.screen_width = GetSystemMetrics(0)
        self.settings.screen_height = GetSystemMetrics(1)
        self.screen_width.value = str(self.settings.screen_width)
        self.screen_height.value = str(self.settings.screen_height)
        self.screen_width.update()
        self.screen_height.update()

    def reset_mouse_manual_parse_textfield(self, e):
        self.mouse_manual_parse_textfield.value = """{\n    "move_xy_offset": 1,\n    "move_xy_size": 4,\n    "scroll_offset": 4,\n    "scroll_size": 1,\n    "buttons_offset": 5,\n    "buttons_count": 8\n}"""
        self.mouse_manual_parse_textfield.update()
        self.mouse_manual_parse_textfield_change(e)

    def mouse_manual_parse_textfield_change(self, e):
        control = self.mouse_manual_parse_textfield
        keys = ["move_xy_offset", "move_xy_size", "scroll_offset", "scroll_size", "buttons_offset", "buttons_count"]

        try:
            result = json.loads(control.value)
            if control.error_text is not None:
                control.error_text = None
                control.update()
        except:
            control.error_text = self.textLocaled('wrong_input')
            control.update()
            return

        for key in keys:
            if key not in result:
                control.error_text = self.textLocaled('wrong_input')
                control.update()
                return
            elif type(result[key]) != int:
                control.error_text = self.textLocaled('wrong_input')
                control.update()
                return
            elif result[key] < 0:
                control.error_text = self.textLocaled('wrong_input')
                control.update()
                return
        
        if result[keys[1]] not in range(2, 5):
            control.error_text = self.textLocaled('wrong_input')
            control.update()
            return
        if result[keys[3]] not in range(1, 3):
            control.error_text = self.textLocaled('wrong_input')
            control.update()
            return
        self.settings.mouse_parse_dict = result

    def mouse_manual_parse_change(self, e):
        self.settings.mouse_manual_parse = e.control.value
        self.mouse_manual_parse_textfield.disabled = not e.control.value
        self.mouse_manual_parse_textfield.update()

    def get_mouse_report_changes(self, e):
        try:
            mouse_info = list(map(int, self.settings.mouse_device.split()))
            vid, pid = mouse_info[0], mouse_info[1]
        except Exception as e:
            print(f'[App] [W]: No mouse_device in Settings ({e})')
            return
        changes = get_report_changes(vid, pid, self.settings.mouse_interface, 1.5)
        self.mouse_report_changes_text.value = '   '.join(map(str, changes))
        self.mouse_report_changes_text.update()

    def configure_libusb(self, e):
        try:
            subprocess.Popen(['python', '../bin/filter_configure.py'])
        except OSError:
            print('[App] [I]: Operation canceled by user')
    
    def hookmanager_api_change(self, e):
        self.settings.hookmanager_api = e.control.value
        if e.control.value == 'winhook':
            self.settings.mouse_events = {
                'mouse left down': 'aim',
                'mouse left up': 'aim'
            }
        else:
            self.settings.mouse_events = {
                'm_left': 'aim'
            }
        self.page.open(self.hookmanager_api_dlg)

    def bindings_content_update(self):
        self.bindings_rows_update()

        self.bindings_content.controls = [
            Text(self.textLocaled('bindings_settings_text'), size=26, text_align=TextAlign.CENTER),
            self.hookmanager_api,
            ElevatedButton(
                text=self.textLocaled('add_btn_bindings'),
                width=170,
                on_click=self.add_binding_row
            ),
            Divider(height=3, thickness=3),
            *self.bindings_rows
        ]

        try:
            self.bindings_content.update()
        except:
            pass

    def remove_binding_row(self, e):

        self.settings.keyboard_events.pop(e.control.key_name)

        # for row in self.bindings_rows:
        #     if row.controls[0].key_name == e.control.key_name:
        #         self.bindings_rows.remove(row)

        self.bindings_content_update()

    def reassign_binding(self, e):
        prev_key = e.control.key_name
        e.control.text = self.textLocaled('press_text_bindings')
        e.control.update()
        new_key = get_pressed_key(api=self.settings.hookmanager_api)
        e.control.text = new_key
        try:
            e.control.update()
        except:
            pass

        pos = list(self.settings.keyboard_events.keys()).index(prev_key)
        value = self.settings.keyboard_events.pop(prev_key)
        items = list(self.settings.keyboard_events.items())
        items.insert(pos, (new_key, value))
        self.settings.keyboard_events = dict(items)

        self.bindings_content_update()

    def add_binding_row(self, e):
        items = list(self.settings.keyboard_events.items())
        items.insert(0, ('not_set', 'not_set'))
        self.settings.keyboard_events = dict(items)

        self.bindings_content_update()

    def bindings_rows_update(self):
        self.bindings_rows = []

        for key in self.settings.keyboard_events:
            key_button = OutlinedButton(
                text=key,
                width=190,
                on_click=self.reassign_binding
            )
            action_menu = Dropdown(
                label=self.textLocaled('action_label_bindings'),
                hint_text=self.textLocaled('action_hint_bindings'),
                options=[
                    dropdown.Option(
                        text=self.actions[j],
                        key=j
                    ) for j in self.actions
                ],
                border_radius=border_radius.all(self.border_radius),
                value=self.settings.keyboard_events[key],
                on_change=lambda e: self.settings.keyboard_events.update({e.control.key_name: e.control.value})
            )
            remove_btn = IconButton(
                icon=icons.CLOSE_ROUNDED,
                data=0,
                style=ButtonStyle(
                    bgcolor={
                        MaterialState.HOVERED: colors.RED
                    },
                    shape={
                        MaterialState.HOVERED: CircleBorder()
                    }
                ),
                on_click=self.remove_binding_row
            )
            key_button.key_name = key
            action_menu.key_name = key
            remove_btn.key_name = key
            self.bindings_rows.append(Row(
                [
                    key_button,
                    Row([
                        action_menu,
                        remove_btn
                    ])
                ],
                alignment=MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=CrossAxisAlignment.CENTER
            ))


    @staticmethod
    def normal_chart_data(center, sigma, n, color):
        return LineChartData(
            stroke_width=5,
            color=color,
            curved=True,
            stroke_cap_round=True,
            data_points=[LineChartDataPoint((x / n - 0.5) * 2 * n, (1 / (sigma * (2 * math.pi) ** 0.5)) * math.e ** (
                    -0.5 * (((x / n - 0.5) * 2 * n - center) / sigma) ** 2)) for x in
                         range(0, n + 1)]
        )

    @staticmethod
    def aim_chart_data(k, b, i, n, color):
        return LineChartData(
            stroke_width=5,
            color=color,
            curved=True,
            stroke_cap_round=True,
            data_points=[LineChartDataPoint((x / n), max(-0.2, min(1.2, ((x / n) * k + abs(b)) ** -i))) for x in
                         range(0, n + 1)]
        )
    
    def detection_cls_change(self, e: flet.ControlEvent):
        control_idx = self.detection_cls_map[e.control.label]
        if e.control.value:
            if control_idx not in self.settings.detection_classes:
                self.settings.detection_classes.append(control_idx)
        elif control_idx in self.settings.detection_classes:
            self.settings.detection_classes.remove(control_idx)
    
    def mouse_driver_change(self, e):
        self.settings.mouse_driver = e.control.value
        if e.control.value == 'interception':
            self.mouse_device.disabled = False
        elif self.settings.mouse2driver_translate:
            self.mouse_device.disabled = False
        else:
            self.mouse_device.disabled = True
        self.mouse_device.update()

    def wait_stop_moving_change(self, e):
        self.stop_moving_time.disabled = not e.control.value
        self.settings.wait_stop_moving = e.control.value
        self.stop_moving_time.update()
    
    def use_centroids_change(self, e):
        self.centroids_thresh.disabled = not e.control.value
        self.settings.use_centroids = e.control.value
        self.centroids_thresh.update()

    def lunarbox_action(self, e):
        try:
            mouse_c_ip = self.settings.mouse_c_ip
            if self.settings.mouse_proxy_manual:
                print('[Main] [I]: Trying auto-connect to LunarBox')
                mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                mouse_socket.connect((self.settings.mouse_l_ip, self.settings.mouse_l_port))
                mouse_c_ip = mouse_socket.getsockname()[0]
                mouse_socket.close()

            _proxy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _proxy.bind((mouse_c_ip, self.settings.mouse_l_port + 1))

            _proxy_addr = (self.settings.mouse_l_ip, self.settings.mouse_l_port)

            _proxy.sendto(struct.pack('=H', self.lunarbox_actions[e.control.key]), _proxy_addr)
            _proxy.close()
            if self.settings.bind_sounds:
                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
        except Exception as e:
            print(f'[App] [F]: Exception handled while sending LunarBox actions ({e})')

    def color_menu_change(self, e):
        if e.control.value == 'green_aim':
            self.low_hsv_aim_btn.bgcolor = '#4b4a41'
            self.low_aim_color_picker.color = '#4b4a41'
            self.high_hsv_aim_btn.bgcolor = '#a9ff00'
            self.high_aim_color_picker.color = '#a9ff00'
            self.settings.low_aim_color = '#4b4a41'
            self.settings.high_aim_color = '#a9ff00'
            self.low_hsv_aim_btn.update()
            self.high_hsv_aim_btn.update()
        elif e.control.value == 'yellow_aim':
            self.low_hsv_aim_btn.bgcolor = '#9b964d'
            self.low_aim_color_picker.color = '#9b964d'
            self.high_hsv_aim_btn.bgcolor = '#fbff00'
            self.high_aim_color_picker.color = '#fbff00'
            self.settings.low_aim_color = '#9b964d'
            self.settings.high_aim_color = '#fbff00'
            self.low_hsv_aim_btn.update()
            self.high_hsv_aim_btn.update()
        elif e.control.value == 'purple_aim':
            self.low_hsv_aim_btn.bgcolor = '#68526b'
            self.low_aim_color_picker.color = '#68526b'
            self.high_hsv_aim_btn.bgcolor = '#ff00f7'
            self.high_aim_color_picker.color = '#ff00f7'
            self.settings.low_aim_color = '#68526b'
            self.settings.high_aim_color = '#ff00f7'
            self.low_hsv_aim_btn.update()
            self.high_hsv_aim_btn.update()
        elif e.control.value == 'green_trigger':
            self.low_hsv_trigger_btn.bgcolor = '#4b4a41'
            self.low_trigger_color_picker.color = '#4b4a41'
            self.high_hsv_trigger_btn.bgcolor = '#a9ff00'
            self.high_trigger_color_picker.color = '#a9ff00'
            self.settings.low_trigger_color = '#4b4a41'
            self.settings.high_trigger_color = '#a9ff00'
            self.low_hsv_trigger_btn.update()
            self.high_hsv_trigger_btn.update()
        elif e.control.value == 'yellow_trigger':
            self.low_hsv_trigger_btn.bgcolor = '#9b964d'
            self.low_trigger_color_picker.color = '#9b964d'
            self.high_hsv_trigger_btn.bgcolor = '#fbff00'
            self.high_trigger_color_picker.color = '#fbff00'
            self.settings.low_trigger_color = '#9b964d'
            self.settings.high_trigger_color = '#fbff00'
            self.low_hsv_trigger_btn.update()
            self.high_hsv_trigger_btn.update()
        elif e.control.value == 'purple_trigger':
            self.low_hsv_trigger_btn.bgcolor = '#68526b'
            self.low_trigger_color_picker.color = '#68526b'
            self.high_hsv_trigger_btn.bgcolor = '#ff00f7'
            self.high_trigger_color_picker.color = '#ff00f7'
            self.settings.low_trigger_color = '#68526b'
            self.settings.high_trigger_color = '#ff00f7'
            self.low_hsv_trigger_btn.update()
            self.high_hsv_trigger_btn.update()

    def open_color_picker(self, e):
        # print('Choosing dialog')
        # self.page.dialog = None
        # self.page.update()
        if e.control.key == 'low_aim':
            self.page.open(self.low_hsv_aim_dialog)
            # self.low_hsv_aim_dialog.update()
        elif e.control.key == 'high_aim':
            self.page.open(self.high_hsv_aim_dialog)
            # self.high_hsv_aim_dialog.open = True
            # self.high_hsv_aim_dialog.update()
        elif e.control.key == 'low_trigger':
            self.page.open(self.low_hsv_trigger_dialog)
            # self.low_hsv_trigger_dialog.open = True
            # self.low_hsv_trigger_dialog.update()
        elif e.control.key == 'high_trigger':
            self.page.open(self.high_hsv_trigger_dialog)
            # self.high_hsv_trigger_dialog.open = True
            # self.high_hsv_trigger_dialog.update()
        # print('Dialog activated')
        # await self.page.update_async()
        # self.page.update()
        # print('Page updated')

    def close_dialog(self, e):
        if e.control.key == 'low_aim':
            self.page.close(self.low_hsv_aim_dialog)
            # self.low_hsv_aim_dialog.open = False
            # self.low_hsv_aim_dialog.update()
            # self.page.dialog = None
        elif e.control.key == 'high_aim':
            self.page.close(self.high_hsv_aim_dialog)
            # self.high_hsv_aim_dialog.open = False
            # self.high_hsv_aim_dialog.update()
            # self.page.dialog = None
        elif e.control.key == 'low_trigger':
            self.page.close(self.low_hsv_trigger_dialog)
            # self.low_hsv_trigger_dialog.open = False
            # self.low_hsv_trigger_dialog.update()
            # self.page.dialog = None
        elif e.control.key == 'high_trigger':
            self.page.close(self.high_hsv_trigger_dialog)
            # self.high_hsv_trigger_dialog.open = False
            # self.high_hsv_trigger_dialog.update()
            # self.page.dialog = None
        # self.page.dialog = None
        # self.page.update()

    def change_color(self, e):
        if e.control.key == 'low_aim':
            self.low_hsv_aim_btn.bgcolor = self.low_aim_color_picker.color
            self.settings.low_aim_color = self.low_aim_color_picker.color
            self.close_dialog(e)
            self.low_hsv_aim_btn.update()
            # self.low_hsv_aim_dialog.open = False
            # self.low_hsv_aim_dialog.update()
        elif e.control.key == 'high_aim':
            self.high_hsv_aim_btn.bgcolor = self.high_aim_color_picker.color
            self.settings.high_aim_color = self.high_aim_color_picker.color
            self.close_dialog(e)
            self.high_hsv_aim_btn.update()
            # self.high_hsv_aim_dialog.open = False
            # self.high_hsv_aim_dialog.update()
        elif e.control.key == 'low_trigger':
            self.low_hsv_trigger_btn.bgcolor = self.low_trigger_color_picker.color
            self.settings.low_trigger_color = self.low_trigger_color_picker.color
            self.close_dialog(e)
            self.low_hsv_trigger_btn.update()
            # self.low_hsv_trigger_dialog.open = False
            # self.low_hsv_trigger_dialog.update()
        elif e.control.key == 'high_trigger':
            self.high_hsv_trigger_btn.bgcolor = self.high_trigger_color_picker.color
            self.settings.high_trigger_color = self.high_trigger_color_picker.color
            self.close_dialog(e)
            self.high_hsv_trigger_btn.update()
            # self.high_hsv_trigger_dialog.open = False
            # self.high_hsv_trigger_dialog.update()
        # self.page.dialog = None
        # self.page.update()

    def normal_chart_change_float(self, e):
        control = e.control
        try:
            for attr_name in filter(lambda aname: not aname.startswith('_'), dir(self)):
                if getattr(self, attr_name) == control:
                    break
            setattr(self.settings, attr_name, abs(float(e.control.value)))
            control.error_text = None
        except ValueError:
            control.error_text = self.textLocaled('wrong_input')
        control.update()
        data = [self.normal_chart_data(self.settings.trigger_reaction, self.settings.trigger_reaction_dispersion,
                                       40, colors.CYAN),
                self.normal_chart_data(self.settings.trigger_duration, self.settings.trigger_duration_dispersion,
                                       40, colors.ORANGE)
                ],
        self.normal_chart.data_series = data[0]
        self.normal_chart.update()

    def aim_chart_change_float(self, e):
        control = e.control
        try:
            for attr_name in filter(lambda aname: not aname.startswith('_'), dir(self)):
                if getattr(self, attr_name) == control:
                    break
            setattr(self.settings, attr_name, float(e.control.value))
            control.error_text = None
        except ValueError:
            control.error_text = self.textLocaled('wrong_input')
        control.update()
        self.nonlinear_aim_chart.data_series = [
            self.aim_chart_data(self.settings.nonlinear_k, self.settings.nonlinear_b, self.settings.nonlinear_i, 40,
                                colors.CYAN)]
        self.nonlinear_aim_chart.update()

    def mouse_proxy_manual_change(self, e):
        self.settings.mouse_proxy_manual = e.control.value
        self.mouse_c_ip.disabled = not e.control.value
        # self.mouse_l_ip.disabled = not e.control.value
        # self.mouse_l_port.disabled = not e.control.value
        self.mouse_c_ip.update()
        # self.mouse_l_ip.update()
        # self.mouse_l_port.update()

    def switch_nonlinear_aim(self, e):
        self.settings.nonlinear_aim = e.control.value
        # self.nonlinear_chart.disabled = not e.control.value
        self.nonlinear_k.disabled = not e.control.value
        self.nonlinear_i.disabled = not e.control.value
        self.nonlinear_b.disabled = not e.control.value
        self.nonlinear_k.update()
        self.nonlinear_i.update()
        self.nonlinear_b.update()
        self.nonlinear_aim_chart.data_series = [
            self.aim_chart_data(self.settings.nonlinear_k, self.settings.nonlinear_b, self.settings.nonlinear_i, 40,
                                colors.CYAN)] if e.control.value else \
            [self.aim_chart_data(1, 0, -1, 40, colors.ORANGE)]
        self.nonlinear_aim_chart.update()

    def switch_interpolation_filter(self, e):
        self.settings.interpolation_filter = e.control.value
        if not self.settings.pid_interpolate and not self.settings.interpolation_filter:
            self.interpolation_filter_refresh_rate.disabled = True
        elif e.control.value:
            self.interpolation_filter_refresh_rate.disabled = False
        self.interpolation_filter_refresh_rate.update()

    def mouse_device_change(self, e):
        self.settings.mouse_device = e.control.value
    
    def update_mouse_devices(self, e):
        self.mouse_device.options = [
            dropdown.Option(
                text=f'{hex(device[0])[2:].upper()}:{hex(device[1])[2:].upper()}',
                key=str(device[0]) + ' ' + str(device[1])
            ) for device in get_devices()
        ]
        self.mouse_device.update()

    def get_queue_mode(self, e):
        self.settings.screen_handler_queue_mode = True if e.control.value == 'true' else False
        self.screen_handler_queue_size.disabled = True if e.control.value == 'false' else False
        self.screen_handler_queue_size.update()

    def mouse2driver_change(self, e):
        self.settings.mouse2driver_translate = e.control.value
        # if self.settings.mouse2driver_translate:
        #     self.mouse_driver.value = 'driver'
        #     self.settings.mouse_driver = 'driver'
        self.mouse_device.disabled = not self.settings.mouse2driver_translate
        self.mouse_report_log.disabled = not self.settings.mouse2driver_translate
        self.driver_priority.disabled = not self.settings.mouse2driver_translate
        # self.mouse_driver.disabled = self.settings.mouse2driver_translate
        self.accumulate_mouse_movement.disabled = not self.settings.mouse2driver_translate
        self.mouse_driver.update()
        self.mouse_device.update()
        self.mouse_report_log.update()
        self.driver_priority.update()
        self.accumulate_mouse_movement.update()

    def trigger_burst_change(self, e):
        self.settings.trigger_burst_mode = e.control.value
        self.trigger_burst_count.disabled = not e.control.value
        self.trigger_burst_count.update()

    def color_trigger_mode_change(self, e):
        self.settings.color_trigger_mode = e.control.value
        if e.control.value == 'bbox':
            self.high_hsv_trigger_btn.disabled = False
            self.low_hsv_trigger_btn.disabled = False
            self.morph_kernel_trigger.disabled = False
            self.dilate_kernel_trigger.disabled = False
            self.morph_iterations_trigger.disabled = False
            self.dilate_iterations_trigger.disabled = False
            self.min_ratio_trigger.disabled = False
            self.max_ratio_trigger.disabled = False
            self.trigger_zone.disabled = True
            self.changed_pixels.disabled = True
            self.trigger_pixel_thresh.disabled = True
        elif e.control.value == 'color':
            self.high_hsv_trigger_btn.disabled = False
            self.low_hsv_trigger_btn.disabled = False
            self.morph_kernel_trigger.disabled = True
            self.dilate_kernel_trigger.disabled = True
            self.morph_iterations_trigger.disabled = True
            self.dilate_iterations_trigger.disabled = True
            self.min_ratio_trigger.disabled = True
            self.max_ratio_trigger.disabled = True
            self.trigger_zone.disabled = False
            self.changed_pixels.disabled = False
            self.trigger_pixel_thresh.disabled = True
        else:
            self.high_hsv_trigger_btn.disabled = True
            self.low_hsv_trigger_btn.disabled = True
            self.morph_kernel_trigger.disabled = True
            self.dilate_kernel_trigger.disabled = True
            self.morph_iterations_trigger.disabled = True
            self.dilate_iterations_trigger.disabled = True
            self.min_ratio_trigger.disabled = True
            self.max_ratio_trigger.disabled = True
            self.trigger_zone.disabled = False
            self.changed_pixels.disabled = False
            self.trigger_pixel_thresh.disabled = False
        self.trigger_content.update()

    def pid_interpolate_change(self, e):
        self.settings.pid_interpolate = e.control.value
        if not self.settings.pid_interpolate and not self.settings.interpolation_filter:
            self.interpolation_filter_refresh_rate.disabled = True
        elif e.control.value:
            self.interpolation_filter_refresh_rate.disabled = False
        self.interpolation_filter_refresh_rate.update()

    def use_pid_change(self, e):
        self.settings.use_pid = e.control.value

        self.pidx_k.disabled = not e.control.value
        self.pidx_i.disabled = not e.control.value
        self.pidx_d.disabled = not e.control.value
        self.pidy_k.disabled = not e.control.value
        self.pidy_i.disabled = not e.control.value
        self.pidy_d.disabled = not e.control.value

        self.pidx_k.update()
        self.pidx_i.update()
        self.pidx_d.update()
        self.pidy_k.update()
        self.pidy_i.update()
        self.pidy_d.update()


    def start_core(self, e):
        # Some code that starts subprocess
        # ...
        if self.core_state_listener_ran:
            return 0

        for control in SETTINGS_LIST:
            if control == 'cuda_runtime':
                control = self.cudart_select
            elif control == 'device':
                control = self.gpu_select
            elif control in ['keyboard_events', 'macro_divide', 'mouse_events', 'rtx_gpu']:
                control = self.game_select
            elif control in ['low_aim_color', 'high_aim_color']:
                control = self.low_hsv_aim_btn
            elif control == "detection_classes":
                control = self.detection_cls_1
            else:
                control = getattr(self, control)
            control.error_text = None
            try:
                self.main_content.update()
            except:
                pass

        correct, control = check_settings(self.settings)
        if not correct:
            if control == 'cuda_runtime':
                control = self.cudart_select
            elif control == 'device':
                control = self.gpu_select
            elif control in ['keyboard_events', 'macro_divide', 'mouse_events', 'rtx_gpu']:
                control = self.game_select
            elif control == 'mouse2driver_translate':
                setattr(self.settings, control, False)
                control = getattr(self, control)
            elif control in ['low_aim_color', 'high_aim_color']:
                control = self.low_hsv_aim_btn
            else:
                control = getattr(self, control)
            # control.disabled = False
            control.error_text = self.textLocaled('not_set')
            self.core_ran_text.value = self.textLocaled('config_error_core')
            try:
                self.main_content.update()
            except:
                pass
            return 0

        self.core_ran_text.value = self.textLocaled('starting_text_core')
        self.core_ran_text.color = colors.YELLOW_ACCENT
        try:
            self.core_ran_text.update()
        except:
            pass

        self.core_state_listener_ran = True

        settings_bytes = pickle.dumps(self.settings)
        self.core_memory.buf[:len(settings_bytes)] = settings_bytes

        # run subprocess
        self.core_process = subprocess.Popen(['python', '-c', f'import main; main.main("{self.core_memory_name}")'],
                                             stdin=subprocess.PIPE)

        # self.core_process = subprocess.Popen(['python', 'core.pyc', self.core_memory_name],
        #                                      stdin=subprocess.PIPE)

        # self.core_process = subprocess.Popen(['core.exe', self.core_memory_name], stdin=subprocess.PIPE)

        while self.core_memory.buf[0] == 128:
            time.sleep(0.5)
            if not pid_exists(self.core_process.pid):
                self.core_ran_text.value = self.textLocaled('stopped_text_core')
                self.core_ran_text.color = '#bf2c4c'
                try:
                    self.core_ran_text.update()
                except:
                    pass
                self.core_state_listener_ran = False
                return None
        time.sleep(0.5)

        self.core_ran_text.value = self.textLocaled('sync_text_core')
        try:
            self.core_ran_text.update()
        except:
            pass

        corestate_bytes = pickle.dumps(self.core_state)
        self.core_memory.buf[:len(corestate_bytes)] = corestate_bytes
        self.core_memory.buf[-1] = b'\x23'[0]

        while self.core_memory.buf[-1] == 35:
            time.sleep(0.5)
            if not pid_exists(self.core_process.pid):
                self.core_ran_text.value = self.textLocaled('stopped_text_core')
                self.core_ran_text.color = '#bf2c4c'
                try:
                    self.core_ran_text.update()
                except:
                    pass
                self.core_state_listener_ran = False
                return None
        time.sleep(0.5)

        self.core_ran_text.value = self.textLocaled('load_models_text_core')
        try:
            self.core_ran_text.update()
        except:
            pass

        self.core_state = pickle.loads(self.core_memory.buf)
        while not self.core_state.ready:
            time.sleep(0.5)
            self.core_state = pickle.loads(self.core_memory.buf)

        if self.core_state.ready == 'exit':
            self.core_ran_text.value = self.textLocaled('stopped_text_core')
            self.core_ran_text.color = '#bf2c4c'
            try:
                self.core_ran_text.update()
            except:
                pass
            try:
                self.core_process.communicate(b'stopped\r\n', 30)
            except subprocess.TimeoutExpired:
                self.core_process.terminate()
            except ValueError:
                return 0
            self.core_state_listener_ran = False
            return None

        self.core_state_listener = Thread(target=self.core_state_listener_target)
        self.core_state_listener.start()

        self.core_ran_text.value = self.textLocaled('runned_text_core')
        self.core_ran_text.color = '#2aae4f'
        try:
            self.core_ran_text.update()
        except:
            pass

    def stop_core(self, e):
        # Some code to stop subprocess
        # ...
        if not self.core_state_listener.is_alive():
            return 0

        self.core_ran_text.value = self.textLocaled('stopping_text_core')
        self.core_ran_text.color = colors.YELLOW_ACCENT
        try:
            self.core_ran_text.update()
        except:
            pass

        try:
            self.core_process.communicate(b'stopped\r\n', 30)
        except subprocess.TimeoutExpired:
            self.core_process.terminate()
        except ValueError:
            print('[App] [F]: Core inaccessable')
            return 0

        self.core_state_listener_ran = False
        try:
            self.core_state_listener.join()
        except Exception as e:
            print(f'[App] [W]: Core unexpectedly stopped ({e})')

        self.core_ran_text.value = self.textLocaled('stopped_text_core')
        self.core_ran_text.color = '#bf2c4c'
        try:
            self.core_ran_text.update()
        except:
            pass

    def restart_core(self, e):
        self.stop_core(e)
        self.start_core(e)

    def core_state_listener_target(self):
        # print('Main loop started')
        while self.core_state_listener_ran:
            time.sleep(1/self.core_state_refresh_rate)
            try:
                self.core_state = pickle.loads(self.core_memory.buf)
            except Exception as e:
                print('[App] [F]: Core memory error')
            self.update_core_state_field()
            self.core_state_field.value = self.core_state_text
            if not self.core_state.ready:
                self.stop_core(1)
            try:
                self.core_state_field.update()
            except AssertionError:
                pass
        # print('Main loop stopped')

    # noinspection PyTypeChecker
    def set_thres(self, e):
        for attr_name in filter(lambda aname: not aname.startswith('_'), dir(self)):
            if getattr(self, attr_name) == e.control:
                break
        setattr(self.settings, attr_name, e.control.value / 100)

    def cudart_selected(self, e):
        self.settings.cuda_runtime = e.control.value

    def gpu_selected(self, e):
        if e.control.value == 'cpu':
            self.settings.device = e.control.value
            self.settings.rtx_gpu = False
            self.cudart_select.options[0].disabled = True
            if self.cudart_select.value == 'trt':
                self.cudart_select.value = 'torch'
            if self.cudart_select.disabled:
                self.cudart_select.disabled = False
            self.cudart_select.update()
            return

        gpu_id = int(e.control.value[-1:])
        self.settings.device = e.control.value
        for gpu in getGPUs():
            if gpu.id == gpu_id:
                self.settings.rtx_gpu = 'RTX' in gpu.name.upper()
                break
        self.cudart_select.options[0].disabled = not self.settings.rtx_gpu
        if self.cudart_select.disabled:
            self.cudart_select.disabled = False
        self.cudart_select.update()

    def change_fps(self, e):
        self.screen_handler_fps.disabled = not self.screen_handler_fps.disabled
        if self.screen_handler_fps.disabled:
            self.settings.screen_handler_fps = None
        elif self.screen_handler_fps.value != '':
            try:
                self.settings.screen_handler_fps = int(self.screen_handler_fps.value)
            except ValueError:
                print('Incorrect fps value!')
        self.screen_handler_fps.update()

    def text_field_change_int(self, e):
        # control = self.controls[e.control.mykey]
        control = e.control
        try:
            for attr_name in filter(lambda aname: not aname.startswith('_'), dir(self)):
                if getattr(self, attr_name) == control:
                    break
            setattr(self.settings, attr_name, abs(int(e.control.value)))
            control.error_text = None
        except ValueError:
            control.error_text = self.textLocaled('wrong_input')
        control.update()

    def kernel_change(self, e):
        try:
            for attr_name in filter(lambda aname: not aname.startswith('_'), dir(self)):
                if getattr(self, attr_name) == e.control:
                    break
            setattr(self.settings, attr_name, tuple(map(lambda x: abs(int(x)), e.control.value.split())))
            e.control.error_text = None
        except ValueError:
            e.control.error_text = self.textLocaled('wrong_input')
        e.control.update()

    def normal_change_int(self, e):
        # control = self.controls[e.control.mykey]
        control = e.control
        try:
            for attr_name in filter(lambda aname: not aname.startswith('_'), dir(self)):
                if getattr(self, attr_name) == control:
                    break
            setattr(self.settings, attr_name, int(e.control.value))
            control.error_text = None
        except ValueError:
            control.error_text = self.textLocaled('wrong_input')
        control.update()
        data = [self.normal_chart_data(self.settings.trigger_reaction, self.settings.trigger_reaction_dispersion,
                                       40, colors.CYAN),
                self.normal_chart_data(self.settings.trigger_duration, self.settings.trigger_duration_dispersion,
                                       40, colors.ORANGE)
                ],
        self.normal_chart.data_series = data[0]
        try:
            self.normal_chart.update()
        except:
            pass

    def text_field_change_float(self, e):
        # control = self.controls[e.control.mykey]
        control = e.control
        try:
            for attr_name in filter(lambda aname: not aname.startswith('_'), dir(self)):
                if getattr(self, attr_name) == control:
                    break
            setattr(self.settings, attr_name, abs(float(control.value)))
            control.error_text = None
        except ValueError:
            control.error_text = self.textLocaled('wrong_input')
        except Exception as e:
            print(f"[App] [W]: Handled unknown exception {e} in text_field_change_float")
        control.update()

    def game_selected(self, e):
        match self.game_select.value:
            case 'cs':
                self.fov.value = '90'
                self.full_rotate.value = '16364'
                self.fov_width.value = '4'
                self.fov_height.value = '3'

                self.settings.fov = float(self.fov.value)
                self.settings.full_rotate = int(self.full_rotate.value)
                self.settings.fov_width = float(self.fov_width.value)
                self.settings.fov_height = float(self.fov_height.value)

                self.fov.error_text = None
                self.full_rotate.error_text = None
                self.fov_width.error_text = None
                self.fov_height.error_text = None

                self.fov.update()
                self.full_rotate.update()
                self.fov_width.update()
                self.fov_height.update()
            case 'apex':
                self.fov.value = '90'
                self.full_rotate.value = '16364'
                self.fov_width.value = '4'
                self.fov_height.value = '3'

                self.settings.fov = float(self.fov.value)
                self.settings.full_rotate = int(self.full_rotate.value)
                self.settings.fov_width = float(self.fov_width.value)
                self.settings.fov_height = float(self.fov_height.value)

                self.fov.error_text = None
                self.full_rotate.error_text = None
                self.fov_width.error_text = None
                self.fov_height.error_text = None

                self.fov.update()
                self.full_rotate.update()
                self.fov_width.update()
                self.fov_height.update()
            case 'val':
                self.fov.value = '103'
                self.full_rotate.value = '5144'
                self.fov_width.value = '16'
                self.fov_height.value = '9'

                self.settings.fov = float(self.fov.value)
                self.settings.full_rotate = int(self.full_rotate.value)
                self.settings.fov_width = float(self.fov_width.value)
                self.settings.fov_height = float(self.fov_height.value)

                self.fov.error_text = None
                self.full_rotate.error_text = None
                self.fov_width.error_text = None
                self.fov_height.error_text = None

                self.fov.update()
                self.full_rotate.update()
                self.fov_width.update()
                self.fov_height.update()
            case 'fragpunk':
                self.fov.value = '105'
                self.full_rotate.value = '6172'
                self.fov_width.value = '16'
                self.fov_height.value = '9'

                self.settings.fov = float(self.fov.value)
                self.settings.full_rotate = int(self.full_rotate.value)
                self.settings.fov_width = float(self.fov_width.value)
                self.settings.fov_height = float(self.fov_height.value)

                self.fov.error_text = None
                self.full_rotate.error_text = None
                self.fov_width.error_text = None
                self.fov_height.error_text = None

                self.fov.update()
                self.full_rotate.update()
                self.fov_width.update()
                self.fov_height.update()
            case 'other':
                self.fov.value = '90'
                self.fov_width.value = '16'
                self.fov_height.value = '9'

                self.settings.fov = float(self.fov.value)
                self.settings.fov_width = float(self.fov_width.value)
                self.settings.fov_height = float(self.fov_height.value)

                self.fov.error_text = None
                self.fov_width.error_text = None
                self.fov_height.error_text = None

                self.fov.update()
                self.fov_width.update()
                self.fov_height.update()
        self.settings.game_select = e.control.value

    def on_change_config_menu(self, e):
        # print('Menu choice was made')
        if e.control.value == 'newconfig_save':
            # print('Create config button choiced')
            self.file_saver.save_file(dialog_title=self.textLocaled('save_cfg_dialogue'), initial_directory='configs',
                                      allowed_extensions=['config'], file_name='new.config')
        else:
            self.load_config('change_event')
        self.update_config_dropdown(e)

    def save_config(self, e):
        # print('Save config event')
        if type(e) == FilePickerResultEvent:
            # print('Picker result event')
            if self.file_saver.result.path is not None:
                # print(f'Picker path is here {self.filesaver.result.path}')
                self.save_func(self.file_saver.result.path)
                self.update_config_names()
                self.config_menu.options = [dropdown.Option(text=config) for config in self.config_names]
                self.config_menu.options.append(dropdown.Option(text=self.textLocaled('create_cfg_dialogue'), key='newconfig_save'))
                self.config_menu.value = os.path.basename(self.file_saver.result.path).replace('.config', '')
                self.main_content.update()
            # else:
            #     print('Empty result')
        else:
            value = self.config_menu.value
            if value is None:
                self.file_saver.save_file(dialog_title=self.textLocaled('save_cfg_dialogue'), initial_directory='configs',
                                          allowed_extensions=['config'], file_name='new.config')
            else:
                self.save_func(os.path.abspath('configs\\' + value + '.config'))

    def load_config(self, e):
        if type(e) == FilePickerResultEvent:
            if e.files is not None:
                self.update_config_dropdown(e)
                self.load_func(e.files[0].path)
        else:
            value = self.config_menu.value
            if value is None or type(e) != str:
                self.file_picker.pick_files(dialog_title=self.textLocaled('choose_cfg_dialogue'), initial_directory='configs',
                                            allowed_extensions=['config'], allow_multiple=False)
            else:
                self.load_func(os.path.abspath('configs\\' + value + '.config'))

    def save_func(self, path):
        if path[-7:] != '.config':
            path += '.config'
        with open(path, 'wb') as file:
            pickle.dump(self.settings, file)

    def load_func(self, path):
        name = os.path.basename(path).replace('.config', '')

        with open(path, 'rb') as file:
            settings: Settings = pickle.load(file)

        for attr in self.settings.__dict__:
            if attr not in settings.__dict__:
                settings.__setattr__(attr, self.settings.__getattribute__(attr))

        self.settings = settings

        for key, value in self.settings.__dict__.items():
            try:
                control = getattr(self, key)

                if key in ['iou_thres', 'conf_thres', 'target_height', 'centroids_thresh']:
                    value = int(value*100)

                elif key == 'screen_handler_fps':
                    if value is None:
                        self.screen_handler_fps_check.value = True
                        self.screen_handler_fps.value = ''
                    else:
                        self.screen_handler_fps_check.value = False
                        self.screen_handler_fps.value = value

                elif key == 'mouse2driver_translate':
                    self.mouse_device.disabled = not value

                elif key == 'mouse_device':
                    if not self.settings.mouse2driver_translate:
                        value = None

                elif 'kernel' in key:
                    value = ' '.join(list(map(lambda x: str(x), value)))

                elif key == 'trigger_zone':
                    value = ' '.join(list(map(lambda x: str(x), value)))

                control.value = value

            except AttributeError:
                if key == 'low_aim_color':
                    self.low_hsv_aim_btn.bgcolor = self.settings.low_aim_color
                    self.low_aim_color_picker.color = self.settings.low_aim_color
                elif key == 'high_aim_color':
                    self.high_hsv_aim_btn.bgcolor = self.settings.high_aim_color
                    self.high_aim_color_picker.color = self.settings.high_aim_color
                elif key == 'low_trigger_color':
                    self.low_hsv_trigger_btn.bgcolor = self.settings.low_trigger_color
                    self.low_trigger_color_picker.color = self.settings.low_trigger_color
                elif key == 'high_trigger_color':
                    self.high_hsv_trigger_btn.bgcolor = self.settings.high_trigger_color
                    self.high_trigger_color_picker.color = self.settings.high_trigger_color
                elif key == 'detection_classes':
                    self.detection_cls_1.value = self.detection_cls_map[self.detection_cls_1.label] in value
                    self.detection_cls_2.value = self.detection_cls_map[self.detection_cls_2.label] in value
                    self.detection_cls_3.value = self.detection_cls_map[self.detection_cls_3.label] in value
                    self.detection_cls_4.value = self.detection_cls_map[self.detection_cls_4.label] in value
                else:
                    print(f'[App] [I]: key {key} has no UI control')

        data = [
            self.normal_chart_data(self.settings.trigger_reaction, self.settings.trigger_reaction_dispersion,
                                   40, colors.CYAN),
            self.normal_chart_data(self.settings.trigger_duration, self.settings.trigger_duration_dispersion,
                                   40, colors.ORANGE)
        ],
        self.normal_chart.data_series = data[0]
        self.nonlinear_aim_chart.data_series = [
            self.aim_chart_data(self.settings.nonlinear_k, self.settings.nonlinear_b, self.settings.nonlinear_i, 40,
                                colors.CYAN)] if \
            self.nonlinear_aim.value else [self.aim_chart_data(1, 0, -1, 40, colors.ORANGE)]

        self.screen_handler_fps.disabled = self.screen_handler_fps_check.value

        self.screen_handler_queue_size.disabled = not self.settings.screen_handler_queue_mode

        # self.interpolation_filter_refresh_rate.disabled = not self.settings.interpolation_filter
        self.nonlinear_i.disabled = not self.settings.nonlinear_aim
        self.nonlinear_b.disabled = not self.settings.nonlinear_aim
        self.nonlinear_k.disabled = not self.settings.nonlinear_aim

        self.mouse_c_ip.disabled = not self.settings.mouse_proxy_manual
        # self.mouse_l_ip.disabled = not self.settings.mouse_proxy_manual
        # self.mouse_l_port.disabled = not self.settings.mouse_proxy_manual

        if self.settings.color_trigger_mode == 'bbox':
            self.high_hsv_trigger_btn.disabled = False
            self.low_hsv_trigger_btn.disabled = False
            self.morph_kernel_trigger.disabled = False
            self.dilate_kernel_trigger.disabled = False
            self.morph_iterations_trigger.disabled = False
            self.dilate_iterations_trigger.disabled = False
            self.min_ratio_trigger.disabled = False
            self.max_ratio_trigger.disabled = False
            self.trigger_zone.disabled = True
            self.changed_pixels.disabled = True
            self.trigger_pixel_thresh.disabled = True
        elif self.settings.color_trigger_mode == 'color':
            self.high_hsv_trigger_btn.disabled = False
            self.low_hsv_trigger_btn.disabled = False
            self.morph_kernel_trigger.disabled = True
            self.dilate_kernel_trigger.disabled = True
            self.morph_iterations_trigger.disabled = True
            self.dilate_iterations_trigger.disabled = True
            self.min_ratio_trigger.disabled = True
            self.max_ratio_trigger.disabled = True
            self.trigger_zone.disabled = False
            self.changed_pixels.disabled = False
            self.trigger_pixel_thresh.disabled = True
        else:
            self.high_hsv_trigger_btn.disabled = True
            self.low_hsv_trigger_btn.disabled = True
            self.morph_kernel_trigger.disabled = True
            self.dilate_kernel_trigger.disabled = True
            self.morph_iterations_trigger.disabled = True
            self.dilate_iterations_trigger.disabled = True
            self.min_ratio_trigger.disabled = True
            self.max_ratio_trigger.disabled = True
            self.trigger_zone.disabled = False
            self.changed_pixels.disabled = False
            self.trigger_pixel_thresh.disabled = False

        self.pidx_k.disabled = not self.settings.use_pid
        self.pidx_i.disabled = not self.settings.use_pid
        self.pidx_d.disabled = not self.settings.use_pid
        self.pidy_k.disabled = not self.settings.use_pid
        self.pidy_i.disabled = not self.settings.use_pid
        self.pidy_d.disabled = not self.settings.use_pid

        self.accumulate_mouse_movement.disabled = not self.settings.mouse2driver_translate
        self.mouse_report_log.disabled = not self.settings.mouse2driver_translate
        self.driver_priority.disabled = not self.settings.mouse2driver_translate
        self.stop_moving_time.disabled = not self.settings.wait_stop_moving
        self.mouse_manual_parse_textfield.disabled = not self.settings.mouse_manual_parse

        # self.trigger_content.update()

        self.gpu_select.options = [dropdown.Option(text=gpu.name, key=f'cuda:{gpu.id}') for gpu in getGPUs()] + \
                                  [dropdown.Option(text='CPU', key='cpu')]
        try:
            self.gpu_select.value = self.settings.device
        except AttributeError:
            print("[App] [W]: There's no specified device in the config")
        self.cudart_select.value = self.settings.cuda_runtime

        self.config_menu.value = name
        self.update_config_dropdown(1)
        self.config_menu.options.insert(0, dropdown.Option(text=name))
        self.config_menu.update()

        self.centroids_thresh.disabled = not self.settings.use_centroids
        self.main_content.update()

    def update_config_names(self):
        self.config_names = []
        try:
            config_names = os.listdir('configs')
        except FileNotFoundError:
            os.system('mkdir configs')
            config_names = []

        for config_name in config_names:
            if config_name[-7:] != '.config':
                continue
            self.config_names.append(config_name.replace('.config', ''))
    
    def update_config_dropdown(self, e):
        self.update_config_names()
        self.config_menu.options = [dropdown.Option(text=config) for config in self.config_names]
        self.config_menu.options.append(dropdown.Option(text=self.textLocaled('create_cfg_dialogue'), key='newconfig_save'))
        self.config_menu.update()


    def update_core_state_field(self):
        self.core_state_text = self.textLocaled.getCoreStateText(self.core_state)

    def get_container(self, key):
        # return Container(
        #     content=Column(
        #         [
        #             Container(
        #                 expand=1,
        #                 padding=15,
        #                 margin=20,
        #                 bgcolor=self.bgcolor_theme,
        #                 border_radius=border_radius.all(25),
        #                 content=getattr(self, key),
        #             ),
        #             Text('Версия: 1.0.0    Канал: tg.me/lunaraim', size=26, color=colors.ORANGE_ACCENT)
        #         ],
        #         # expand=1,
        #         spacing=0,
        #         horizontal_alignment=CrossAxisAlignment.CENTER,
        #         alignment=MainAxisAlignment.START
        #     ),
        #     expand=1,
        #     padding=0,
        #     margin=0
        # )
        return Container(
            expand=1,
            padding=15,
            margin=margin.only(20, 20, 20, 0),
            bgcolor=self.bgcolor_theme,
            border_radius=border_radius.all(25),
            content=getattr(self, key),
        )
