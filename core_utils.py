import time


__all__ = []


def __dir__():
    return []


SETTINGS_LIST = [
        'core_priority',
        'aim_model_name',
        'conf_thres',
        'detection_classes',
        'cuda_runtime',  # Not in SettingsContent
        'detect_distance_x',
        'detect_distance_y',
        'device',  # Not in SettingsContent
        'fov',
        'fov_width',
        'fov_height',
        'frame_synchronization',
        'use_dxcam',
        'full_rotate',
        'game_select',
        'interpolation_filter',
        'interpolation_filter_refresh_rate',
        'iou_thres',
        'keyboard_events',
        'low_aim_color',
        'high_aim_color',
        'morph_iterations',
        'dilate_iterations',
        'morph_kernel',
        'dilate_kernel',
        'use_centroids',
        'centroids_thresh',
        'min_ratio',
        'max_ratio',
        'morph_iterations_trigger',
        'dilate_iterations_trigger',
        'morph_kernel_trigger',
        'dilate_kernel_trigger',
        'min_ratio_trigger',
        'max_ratio_trigger',
        'changed_pixels',
        'trigger_zone',
        'stop_moving_time',
        'wait_stop_moving',
        'trigger_hit_chance',
        'macro_divide',  # Not in SettingsContent
        'mouse2driver_translate',
        'accumulate_mouse_movement',
        'mouse_report_log',
        'alternative_parser',
        'mouse_device',
        'mouse_driver',
        'mouse_c_ip',
        'mouse_l_ip',
        'mouse_l_port',
        'mouse_proxy_manual',
        'driver_priority',
        'mouse_events',  # Not in SettingsContent
        'static_height_offset',
        'dynamic_height',
        'neural_input_area_size',
        'nonlinear_aim',
        'nonlinear_b',
        'nonlinear_i',
        'nonlinear_k',
        'predict_x',
        'predict_y',
        'prediction_x',
        'prediction_y',
        'damping_x',
        'damping_y',
        'damping_power_x',
        'damping_power_y',
        'rtx_gpu',  # Not in SettingsContent
        'ragebot_max_flick',
        'ragebot_flick_time',
        'ragebot_retract_time',
        'ragebot_cooldown_time',
        'screen_handler_fps',
        'screen_handler_queue_mode',
        'screen_handler_queue_size',
        'screen_height',
        'screen_width',
        'sensitivity',
        'smooth',
        'target_height',
        'topk',
        'trigger_duration',
        'trigger_duration_dispersion',
        'trigger_model_name',
        'trigger_reaction',
        'trigger_reaction_dispersion',
        'trigger_burst_mode',
        'trigger_burst_count',
        'trigger_cooldown',
        'trigger_pixel_thresh',
        'trigger_cooldown_dispersion',
        'color_trigger_mode',
        'use_pid',
        'pidx_k',
        'pidx_i',
        'pidx_d',
        'pidy_k',
        'pidy_i',
        'pidy_d'
    ]


class CoreState:
    parent_pid = -1
    ready = False
    inference_latency = 0
    frame_latency = 0
    smoothness = 0
    reaction = 0
    duration = 0
    interpolation = False
    aim = False
    aim_enabled = False
    trigger = False
    macro = False
    flickbot_enabled = False
    use_pid = False


class Settings:
    pass


def check_settings(settings: Settings):
    for setting in SETTINGS_LIST:
        if setting not in settings.__dict__:
            if setting == 'mouse_device' and not settings.mouse2driver_translate:
                continue
            return False, setting

    return True, None


# def latency_logger():
#     global is_sigterm
#     nonlocal time4core_state, time4frame, time4locked_state, time4macro_calc_1, time4macro_calc_2, time4inference,\
#             time4trigonometry, time4mouse_move, time4fps_count
#
#     latency_dict = {
#         'core_state': 0,
#         'frame': 0,
#         'locked_state': 0,
#         'macro_calc_1': 0,
#         'macro_calc_2': 0,
#         'inference': 0,
#         'trigonometry': 0,
#         'mouse_move': 0,
#         'fps_count': 0
#     }
#
#     while not is_sigterm:
#         time.sleep(1)
#
#         if len(time4core_state) != 0:
#             latency = sum(time4core_state) / len(time4core_state)
#             latency_dict['core_state'] = latency * 1000
#             time4core_state.clear()
#             time4core_state.append(latency)
#         if len(time4frame) != 0:
#             latency = sum(time4frame) / len(time4frame)
#             latency_dict['frame'] = latency * 1000 - latency_dict['core_state']
#             time4frame.clear()
#             time4frame.append(latency)
#         if len(time4locked_state) != 0:
#             latency = sum(time4locked_state) / len(time4locked_state)
#             latency_dict['locked_state'] = latency * 1000 - latency_dict['frame'] - latency_dict['core_state']
#             time4locked_state.clear()
#             time4locked_state.append(latency)
#         if len(time4macro_calc_1) != 0:
#             latency = sum(time4macro_calc_1) / len(time4macro_calc_1)
#             latency_dict['macro_calc_1'] = latency * 1000 - latency_dict['locked_state'] - latency_dict['frame'] - latency_dict['core_state']
#             time4macro_calc_1.clear()
#             time4macro_calc_1.append(latency)
#         if len(time4macro_calc_2) != 0:
#             latency = sum(time4macro_calc_2) / len(time4macro_calc_2)
#             latency_dict['macro_calc_2'] = latency * 1000 - latency_dict['macro_calc_1'] - latency_dict['locked_state'] - latency_dict['frame'] - latency_dict['core_state']
#             time4macro_calc_2.clear()
#             time4macro_calc_2.append(latency)
#         if len(time4inference) != 0:
#             latency = sum(time4inference) / len(time4inference)
#             latency_dict['inference'] = latency * 1000 - latency_dict['macro_calc_2'] - latency_dict['macro_calc_1'] - latency_dict['locked_state'] - latency_dict['frame'] - latency_dict['core_state']
#             time4inference.clear()
#             time4inference.append(latency)
#         if len(time4trigonometry) != 0:
#             latency = sum(time4trigonometry) / len(time4trigonometry)
#             latency_dict['trigonometry'] = latency * 1000 - latency_dict['inference'] - latency_dict['macro_calc_2'] - latency_dict['macro_calc_1'] - latency_dict['locked_state'] - latency_dict['frame'] - latency_dict['core_state']
#             time4trigonometry.clear()
#             time4trigonometry.append(latency)
#         if len(time4mouse_move) != 0:
#             latency = sum(time4mouse_move) / len(time4mouse_move)
#             latency_dict['mouse_move'] = latency * 1000 - latency_dict['trigonometry'] - latency_dict['inference'] - latency_dict['macro_calc_2'] - latency_dict['macro_calc_1'] - latency_dict['locked_state'] - latency_dict['frame'] - latency_dict['core_state']
#             time4mouse_move.clear()
#             time4mouse_move.append(latency)
#         if len(time4fps_count) != 0:
#             latency = sum(time4fps_count) / len(time4fps_count)
#             latency_dict['fps_count'] = latency * 1000 - latency_dict['mouse_move'] - latency_dict['trigonometry'] - latency_dict['inference'] - latency_dict['macro_calc_2'] - latency_dict['macro_calc_1'] - latency_dict['locked_state'] - latency_dict['frame'] - latency_dict['core_state']
#             time4fps_count.clear()
#             time4fps_count.append(latency)
#
#         print('[LATENCY LOGGER] [I]: ', latency_dict)
