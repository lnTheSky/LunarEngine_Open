from typing import List
import math


__all__ = []


def __dir__():
    return []


def compute_sign(value, predict, damping, damping_power, damp_smooth=1.3):
    if not predict:
        return 0
    if abs(value) > damping:
        adjusted_value = (abs(value) - damping) * damping_power
        return (math.tanh(adjusted_value) ** damp_smooth) * math.copysign(1, value)
    return 0


def aim(targets: List[List[int]], settings, smooth: float = 1.0, al_x: float = 0, al_y: float = 0, macro_x: float = 0,
        macro_y: float = 0, flick: bool = False, d_height: bool = False, acc_x=0, acc_y=0):

    m_x: float = settings.x_center + macro_x
    m_y: float = settings.y_center + macro_y

    head_list: list = []
    body_list: list = []
    head_cords: list = []
    body_cords: list = []

    for target in targets:
        x_dist = m_x - (target[0] + target[2]) / 2
        y_dist = m_y - (target[3] + target[1]) / 2
        head_list.append(
            math.sqrt(
                x_dist ** 2 + (y_dist + (2 * settings.target_height - 1) * (target[3] - target[1]) + settings.static_height_offset) ** 2
            )
        )
        head_cords.append(
            (
                x_dist,
                y_dist + (2 * settings.target_height - 1) * (target[3] - target[1]) + settings.static_height_offset
            )
        )

        body_list.append(
            math.sqrt(
                x_dist ** 2 + y_dist ** 2 + 8
            )
        )
        body_cords.append(
            (
                x_dist,
                y_dist
            )
        )

    if d_height:
        if len(head_list) > 0 and len(body_list) > 0:
            dist: float = min(min(head_list), min(body_list))
            if dist in head_list:
                dist_x, dist_y = head_cords[head_list.index(dist)]
            else:
                dist_x, dist_y = body_cords[body_list.index(dist)]
        else:
            return 0, 0, False, 0, 0
    else:
        if len(head_list) > 0:
            dist: float = min(head_list)
            dist_x, dist_y = head_cords[head_list.index(dist)]
        else:
            return 0, 0, False, 0, 0
    is_head: bool = dist in head_list
    # is_head: bool = True

    # t: bool = dist <= settings.detect_distance_x
    t: bool = (((dist_x ** 2) / (settings.detect_distance_x ** 2)) + ((dist_y ** 2) / (settings.detect_distance_y ** 2))) <= 1

    if not t:
        return 0, 0, False, 0, 0

    if flick:
        smooth = 1

    sens: float = smooth * settings.sensitivity

    nonlinear_component: float = 1.0
    if settings.nonlinear_aim:
        nonlinear_component = (dist * settings.nonlinear_dist + settings.nonlinear_b) ** -settings.nonlinear_i

    # nonlinear_component: float = (dist * settings.nonlinear_dist + settings.nonlinear_b) ** \
    #                              -settings.nonlinear_i if settings.nonlinear_aim else 1.0

    # vFOV: float = 2 * math.atan(settings.fov_height / settings.fov_width * math.tan(math.radians(settings.fov / 2)))
    # vFOV = 1.2870022175865685  # 73.73979529168803 degrees vertical FOV constant
    # hFOV: float = 2 * math.atan((0.5 * settings.screen_width) / (0.5 * settings.screen_height / math.tan(vFOV / 2)))
    if is_head:
        target: list = targets[head_list.index(dist)]
        px2y: float = (
                              (target[3] + target[1]) / 2 - (2 * settings.target_height - 1) * (target[3] - target[1])
                      ) - m_y - settings.static_height_offset
    else:
        target: list = targets[body_list.index(dist)]
        px2y: float = (target[3] + target[1]) / 2 - m_y

    px2x: float = ((target[0] + target[2]) / 2) - m_x

    # a_x: float = math.degrees(math.atan(px2x / (settings.screen_width - 1) * 2 * math.tan(settings.hFOV / 2))) - al_x
    # a_y: float = math.degrees(math.atan(px2y / (settings.screen_height - 1) * 2 * math.tan(settings.vFOV / 2))) - al_y

    a_x: float = math.degrees(math.atan(px2x * settings.a_x_cached)) - al_x
    a_y: float = math.degrees(math.atan(px2y * settings.a_y_cached)) - al_y
    

    if settings.accumulate_mouse_movement:
        a_x -= acc_x / settings.full_rotate * settings.sensitivity
        a_y -= acc_y / settings.full_rotate * settings.sensitivity

    # target_height: float = target[3] - target[1]
    # prediction_normal: float = target_height / (0.15 * settings.screen_height)
    # prediction_normal: float = 1.0

    sign_x = compute_sign(a_x, settings.predict_x, settings.damping_x, settings.damping_power_x)
    sign_y = compute_sign(a_y, settings.predict_y, settings.damping_y, settings.damping_power_y)

    # sign_x = 0 if not settings.predict_x else (math.tanh((abs(a_x) - settings.damping_x) * settings.damping_power_x) ** 1.3) * math.copysign(1, a_x) if a_x > settings.damping_x or a_x < -settings.damping_x else 0
    # sign_y = 0 if not settings.predict_y else (math.tanh((abs(a_y) - settings.damping_y) * settings.damping_power_y) ** 1.3) * math.copysign(1, a_y) if a_y > settings.damping_y or a_y < -settings.damping_y else 0

    a_x += settings.prediction_x * sign_x
    a_y += settings.prediction_y * sign_y
    # print(settings.prediction_x, prediction_normal, target_height, sign_x)

    move_x: float = a_x * settings.stable_deg / sens
    move_y: float = a_y * settings.stable_deg / sens

    return move_x * nonlinear_component, move_y * nonlinear_component, t, a_x / smooth * nonlinear_component, \
        a_y / smooth * nonlinear_component


def rage_aim(targets: List[List[int]], settings):
    m_x = settings.x_center
    m_y = settings.y_center

    head_list: list = []

    for target in targets:
        x_dist = (m_x - (target[0] + target[2]) / 2) ** 2
        y_dist = m_y - (target[3] + target[1]) / 2
        head_list.append(
            math.sqrt(
                x_dist + (y_dist + (2 * settings.target_height - 1) * (
                            target[3] - target[1]) + settings.static_height_offset) ** 2
            )
        )

    if len(head_list) > 0:
        dist: float = min(head_list)
    else:
        return 0, 0, False

    sens = settings.sensitivity

    target: list = targets[head_list.index(dist)]
    px2y: float = ((target[3] + target[1]) / 2 - (2 * settings.target_height - 1) * (target[3] - target[1])) - m_y - settings.static_height_offset

    px2x: float = ((target[0] + target[2]) / 2) - m_x

    a_x: float = math.degrees(math.atan(px2x * settings.a_x_cached))
    a_y: float = math.degrees(math.atan(px2y * settings.a_y_cached))

    move_x: float = a_x * settings.stable_deg / sens
    move_y: float = a_y * settings.stable_deg / sens

    return move_x, move_y, True
