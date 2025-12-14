__all__ = []


def __dir__():
    return []


import math
import sys
import time
from warnings import filterwarnings
import pickle
import struct
import psutil
import socket
import argparse
import random
import winsound
from threading import Thread
from multiprocessing.shared_memory import SharedMemory

from core_utils import CoreState, SETTINGS_LIST, Settings, check_settings
from hid_utils import num2buttons

import numpy as np
import cv2

from aim import aim, rage_aim
from hook_manager import HookManager
from screen_handler import ScreenHandler
from mouse import Mouse
# from isolated_mouse import MouseIs
from compiler import autocompile
from predictor import Predictor
from color_boundings import hex2rgb, enhanced_image2bboxes

from aim_mouse import AimMouse

# # ====FOR NUITKA====
# import torch
# import cv2
# from ultralytics import YOLO
# from yolo_model import YOLO as yolo
# # ==================

# from license_client import generate_uid_file, open_license, is_online
# import license_client


APP_VERSION = '1.5.2'

def relu(z):
    return z if z >= 0 else 0


def sigterm():
    global is_sigterm
    while not is_sigterm:
        exit_msg = input()
        if exit_msg == 'stopped':
            break
    print('[Main] [I]: Exiting', exit_msg)
    is_sigterm = True


def parent_is_alive():
    global is_sigterm, sst
    while not is_sigterm:
        time.sleep(3)
        if not psutil.pid_exists(core_state.parent_pid):
            break
        if time.time() - sst > 3600:
            for _ in range(10):
                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                time.sleep(1)
            winsound.PlaySound('button_deactivate.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
            time.sleep(1)
            break
        elif time.time() - sst > 0 and time.time() - sst < 12:
            for _ in range(10):
                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)
                time.sleep(0.05)
            for _ in range(5):
                time.sleep(0.15)
                winsound.PlaySound('button.wav', winsound.SND_ASYNC | winsound.SND_ALIAS)

    print('[Main] [I]: Exiting')
    is_sigterm = True

    # os.kill(current_process().pid, 15)


def main(core_memory_name):

    # def adjust_pointer_speed(slow):
    #     SPI_SETMOUSESPEED = 0x0071
    #     speed = 1 if slow else 10  # Slow speed = 1, Normal speed = 10
    #     ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, 0)

    lic_apis = {
        0: ['user32', 'ghub'],
        1: ['user32', 'ghub', 'driver', 'rdriver'],
        2: ['user32', 'ghub', 'driver', 'rdriver'],
        3: ['user32', 'ghub', 'driver', 'rdriver', 'proxy', 'interception', 'stm32']
    }

    def shoot_target():
        global shoot
        while not is_sigterm:
            if shoot:
                shoot = False
                _count = 1
                if s.trigger_burst_mode:
                    _count = s.trigger_burst_count
                for _ in range(_count):
                    _reaction_time = relu(np.random.normal(hm.reaction, s.trigger_reaction_dispersion) / 1000)
                    _duration_time = relu(np.random.normal(hm.duration, s.trigger_duration_dispersion) / 1000)
                    _cooldown_time = relu(np.random.normal(s.trigger_cooldown, s.trigger_cooldown_dispersion) / 1000)

                    time.sleep(_reaction_time)
                    # mouse.BtnEvent('left_up', api=s.mouse_driver)
                    mouse.BtnEvent('left', api=s.mouse_driver, btns_pressed=mouse_btns())
                    time.sleep(_duration_time)
                    mouse.BtnEvent('left_up', api=s.mouse_driver, btns_pressed=mouse_btns())
                    time.sleep(_cooldown_time)
            else:
                time.sleep(0.006)

    global is_sigterm, core_state, shoot, sst

    filterwarnings('ignore')

    # ================ Load CoreState and Settings ================

    core_memory = SharedMemory(core_memory_name)

    if core_memory.buf[0] == 128:
        s: Settings = pickle.loads(core_memory.buf[:])
        core_memory.buf[:] = len(core_memory.buf) * b'\x00'
    else:
        print('[Main] [F]: CoreSettings undefined')
        sys.exit()

    while core_memory.buf[-1] != 35:
        time.sleep(0.5)
    time.sleep(0.2)

    core_memory.buf[-1] = b'\x00'[0]
    core_state = pickle.loads(core_memory.buf[:])

    if core_state.parent_pid == -1:
        print('[Main] [F]: CoreState parent pid undefined')
        core_state.ready = 'exit'
        core_state_bytes = pickle.dumps(core_state)
        core_memory.buf[:len(core_state_bytes)] = core_state_bytes
        sys.exit()

    # =============================================================

    s.region = (s.screen_width // 2 - s.neural_input_area_size // 2,
                s.screen_height // 2 - s.neural_input_area_size // 2,
                s.screen_width // 2 - s.neural_input_area_size // 2 + s.neural_input_area_size - 1,
                s.screen_height // 2 - s.neural_input_area_size // 2 + s.neural_input_area_size - 1)

    trigger_width_1 = s.neural_input_area_size // 2 - s.trigger_zone[0] // 2
    trigger_height_1 = s.neural_input_area_size // 2 - s.trigger_zone[1] // 2
    trigger_width_2 = s.neural_input_area_size // 2 - s.trigger_zone[0] // 2 + s.trigger_zone[0] - 1
    trigger_height_2 = s.neural_input_area_size // 2 - s.trigger_zone[1] // 2 + s.trigger_zone[1] - 1

    s.vFOV = 2 * math.atan(s.fov_height / s.fov_width * math.tan(math.radians(s.fov / 2)))
    s.hFOV = 2 * math.atan((0.5 * s.screen_width) / (0.5 * s.screen_height / math.tan(s.vFOV / 2)))
    s.stable_deg = s.full_rotate / 360
    s.a_x_cached = 2 * math.tan(s.hFOV / 2) / (s.screen_width - 1)
    s.a_y_cached = 2 * math.tan(s.vFOV / 2) / (s.screen_height - 1)
    s.x_center = (s.screen_width - 1) / 2
    s.y_center = (s.screen_height - 1) / 2
    s.nonlinear_dist = s.nonlinear_k / max(s.detect_distance_x, s.detect_distance_y)

    s.ragebot_flick_time /= 1000
    s.ragebot_retract_time /= 1000
    s.ragebot_cooldown_time /= 1000

    lower_color_rgb = hex2rgb(s.low_trigger_color)
    upper_color_rgb = hex2rgb(s.high_trigger_color)

    lower_color_hsv = cv2.cvtColor(np.array(lower_color_rgb, dtype='uint8').reshape((1, 1, 3)), 
        cv2.COLOR_RGB2HSV)[0, 0]
    upper_color_hsv = cv2.cvtColor(np.array(upper_color_rgb, dtype='uint8').reshape((1, 1, 3)), 
        cv2.COLOR_RGB2HSV)[0, 0]

    lower_aim_rgb = hex2rgb(s.low_aim_color)
    upper_aim_rgb = hex2rgb(s.high_aim_color)

    lower_aim_hsv = cv2.cvtColor(np.array(lower_aim_rgb, dtype='uint8').reshape((1, 1, 3)), 
        cv2.COLOR_RGB2HSV)[0, 0]
    upper_aim_hsv = cv2.cvtColor(np.array(upper_aim_rgb, dtype='uint8').reshape((1, 1, 3)), 
        cv2.COLOR_RGB2HSV)[0, 0]

    s.lower_color_hsv = lower_aim_hsv
    s.upper_color_hsv = upper_aim_hsv

    psutil.Process().nice(s.core_priority)

    if s.cuda_runtime != 'trt':
        s.rtx_gpu = False
    
    ###############################################################################
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pss
    from hashlib import pbkdf2_hmac
    from Crypto.Hash import SHA256
    import license_client

    # try:
    #     with open(license_client.__spec__.origin, 'rb') as file:
    #         lc_bytes = file.read()
    # except:
    #     print('[Main] [F]: Integrity check failed')
    #     core_state.ready = 'exit'
    #     core_state_bytes = pickle.dumps(core_state)
    #     core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    #     sys.exit()

    # try:
    #     lc_sign_len = struct.unpack('=Q', lc_bytes[-8:])[0]
    #     lc_sign = lc_bytes[-lc_sign_len - 8:-8]
    #     lc_extra_len = struct.unpack('=Q', lc_bytes[-lc_sign_len - 16:-lc_sign_len - 8])[0]
    #     pub_key = pickle.loads(lc_bytes[-lc_sign_len - 16 - lc_extra_len:-lc_sign_len - 16])
    # except Exception as e:
    #     print('[Main] [F]: Integrity check failed')
    #     core_state.ready = 'exit'
    #     core_state_bytes = pickle.dumps(core_state)
    #     core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    #     sys.exit()

    # verifier = pss.new(RSA.import_key(pub_key))
    # h = SHA256.new(lc_bytes[:-8 - lc_sign_len])

    # try:
    #     verifier.verify(h, lc_sign)
    # except (ValueError, TypeError):
    #     print('[Main] [F]: Integrity check failed')
    #     core_state.ready = 'exit'
    #     core_state_bytes = pickle.dumps(core_state)
    #     core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    #     sys.exit()
    
    # # ===============

    # for lib in [__file__[:-2] + 'cp311-win_amd64.pyd']:
    #     if lib is None:
    #         continue
    #     try:
    #         with open(lib, 'rb') as file:
    #             lib_bytes = file.read()
    #     except Exception as e:
    #         print('[Main] [F]: Integrity check failed')
    #         core_state.ready = 'exit'
    #         core_state_bytes = pickle.dumps(core_state)
    #         core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    #         sys.exit()
    #     try:
    #         lib_sign_len = struct.unpack('=Q', lib_bytes[-8:])[0]
    #         lib_sign = lib_bytes[-lib_sign_len - 8:-8]
    #         lib_extra_len = struct.unpack('=Q', lib_bytes[-lib_sign_len - 16:-lib_sign_len - 8])[0]
    #         lib_extra = pickle.loads(lib_bytes[-lib_sign_len - 16 - lib_extra_len:-lib_sign_len - 16])
    #     except Exception as e:
    #         print('[Main] [F]: Integrity check failed')
    #         core_state.ready = 'exit'
    #         core_state_bytes = pickle.dumps(core_state)
    #         core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    #         sys.exit()
    #     lib_junked_hash, lib_offs, lib_salt, lib_iters, lib_hash_len = lib_extra
    #     lib_hash = b''

    #     for i in range(len(lib_offs) // 2):
    #         lib_hash += lib_junked_hash[lib_offs[i * 2]:lib_offs[i * 2 + 1]]
        
    #     if not lib_hash == pbkdf2_hmac("sha256", pub_key, lib_salt, lib_iters, lib_hash_len):
    #         print('[Main] [F]: Integrity check failed')
    #         core_state.ready = 'exit'
    #         core_state_bytes = pickle.dumps(core_state)
    #         core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    #         sys.exit()
        
    #     verifier = pss.new(RSA.import_key(pub_key))
    #     h = SHA256.new(lib_bytes[:-8 - lib_sign_len])

    #     try:
    #         verifier.verify(h, lib_sign)
    #     except (ValueError, TypeError):
    #         print('[Main] [F]: Integrity check failed')
    #         core_state.ready = 'exit'
    #         core_state_bytes = pickle.dumps(core_state)
    #         core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    #         sys.exit()

    ###############################################################################
    BPU = license_client.encrypt(
    b'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJRUlqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0JB\nOEFNSUlFQ2dLQ0JBRUF3LzBQRnB6Ri9GTUcvQ1g0ZkRESQp4bkNtTW8yMVVKVjdUc2hUSzM3WVF5\nYzlKejBmMmQ5OEpZbHJ2czVVZWtRTURTRkxWMG9veFpWRDMrU1BYZm9ECmN6ZWNaL3BpaVUyNUpt\naE1pc0I5SXJkbFJpbUhpekN1ajhjOWVZNUx2Y0RNMG5WUFBBUG45bitVbkpHTkpyZkEKSGVVWXlm\nYUYwYmhqOW1FN0JNZTVaRVhYT0dqRmtlWDM2ejhpd3VKVWdxQkE0QmxKZW1OZS9icWF0SHA1K1B5\nZQpjODdHS09Qb3JqK2RZaUU4RURaUUw2WUNENlE5ZTF0bndTcVJWZGhXbmdhd05Ua01oYVUvejQw\nV0cxaGNCaElGCitUSy9oU0tWSFRsckN2alAvRmFVaHc1NVN0ZXpSd004dU13QVBZRzRBN0haQklV\nLzl4N2l0a2d1SjB6ZWh5RUQKTXByalREN1cxNDVvWVBMWExQcmFBeGZPVExWa1l3ME0xN2crZ3lS\nMkFybXZHQ0NzcCt6bTkxM1MyZHgwN0VzYwpIeXFvRHA1ZFUxM1RBb2pxWjZ4QjNHWXFFYWQ1SFdG\nYXdJUWs0WitZenloUWZ0RmgzYjdJSURza1ZkRDBXLzhaCmcwd0FkdG1SMXRKMHhkVFNERFhZaG41\nVys0d3oyTFV0L1JkV2NxbGRpUFZIRXhabk90T3o5ZzltSHphNUJLTDMKU3R0VXZSUEZaQUhmYm9N\nUjhsVmJ4b25qMzFGRWhMS2VsUFpoMnNOZVA3dmxoUUtKdjlSdXdUbG9PcHhtb1lSVgpFMWVwNWpO\ncW1tbXJJNkRERTVSUmRIUmZ4R1ppbHNNTzZqVGtHclQ3aUtyM0VpTlpVcGJrNHZkNFhXc084NC9q\nCk5abFExQlF4OElBQm9nV2hYd05yTXBUYi9PYnBoYXhKVWdJNlo4dXhvMXozczhSeUsxVTN0elZm\nMTVkQWxSNUoKN0VTWE5PNkhKcCszRlFUc3EvZXFPcktORE81SVU0ZUc1SDErTHNpbEh0RlRiaEpi\nSjY5YllyOXRNb1lrSGtBWgpGRDIxTDBhMzNpdlM0bEVjUnhqVmhsbEJaZWtTMnNEVkxyNEJUUkJH\nL1ZxTUZoTmNPa1NpSEh2bDhaZGVJU1YvClpMUXpqM1prSVE3ejBZSWl4NTRwUDg0UllJQUlQMzhJ\nRUJKZzRWYWFRRUgzVjVCamcxdndDR01HdnJCTmd4NEoKUm5oUFhkNit0amlzZUtnc09vdHAzNVl3\nTkU3dTRreG5qZjd2Z2hkYlZ3Wk51NGVWQ2psdVZZVXlDWHJnNlVSdQpycjlMRnBoNHNZYTJ5MHlx\nUzE2Yk5FV2FaNjA2azgyNk9kbE1NRnpxYjluY3AvUEJLVEFBRWc3YmQ2TzJLUXB0ClJYcHZGRnNL\nUGdYMGY3b3pPUnh4WWtlTWNXWDhoeHRjM2xWWW1mS2pTZlFuaWZYUllINThObjV0MktJQ3oyYmIK\nK05jeW51SmVlb0d1akhMemd4MjZJVFJXb21OdzBsbUFoR09BcWdLUFBnTUIyYW5uL1J1RVgzZHVh\nWDNjQzIreQpHOXlQa3JRT2xMTW94OVpuRTJXZk1RaThlcmdYSmQzdi92RkxRKzlEVDNidk1yd3hT\nMnBkRmdXMTh3clhEa0ZHCm5SVVZvTFo5QnB0dnRPcFpCbldNT0p3SXVsakROZGxQRXErcjFQMklq\nU05tSmxPUm1TQkpsWkZ4ZGpDNERXYjEKclUxcTdhTW9KYzdlY2Y5cDZ3Q0dzY1RHeVlWNldOc2Fn\nd0xpaGtaNlhodVpFeE9lazJtZndLWG1kcTJqdzhIcgpsUUlEQVFBQgotLS0tLUVORCBQVUJMSUMg\nS0VZLS0tLS0K\n')
    RPI = license_client.encrypt(
    b'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSVNRZ0lCQURBTkJna3Foa2lHOXcwQkFRRUZB\nQVNDRWl3d2doSW9BZ0VBQW9JRUFRRHZrc1BMY3JsRVE2dEgKQXlIZWI3L2QwSGxIWjR6Ukw0Rnl5\nU0t5aThrWGxHaUc0VmF2V1NURjdmSTZzcnNnRHR2S0NNcUZ0TlhJWDUyZgpXUFZXTEEycWovZzk5\nckZQMWRNT1dYTElRVHJ0TVhCV0NHQ3UwMklPTGZWUEZrYUFHcml5UjhIZTA5S2paOFNjClpYS091\nTHMvc2dhWlY3ei9wV0F4OEVBMnBZV0VpY0lhZE13SWtEaUltMC9SYkJrVWJTblZENE14VkZncnVy\nV0MKcGZHNFhkd1lxZ2ZDU1g5NVg4V3hNeXlIcTZkZG9FaFBvcUlJbUhQeThjQ2dzQXg4SUFoQUxE\nakdzUElCNHRwTwowQTRRcE1qSXNVZjlSRjZDK205MXdldDNJOENYZzV0SUdqS0R4amE2TmxBVkVk\nWFNkSjUxT2wvbTRKUmlXbVkxCkdTK2I3TzJnc0RzRThVUDRJREoyQ25tQmZFM1AzWFJvWWpudElH\nWGtFOHNqSVp4TzJZNDNXZWxyTGtic1puUGwKRVdMcWRmZk04SGNEUFZQQlgyNzZTRkFYMjlWcnFv\nemt0ckttVE9BUHQ5WDlBajczVERIUld6MXMyb001RjdIcAo1MmF1MXhyRnpoZGVCYlpKK2UySEh4\nRkNJNHdqVGVKT2QvYWsxYW1OMEVKQTlDRWF6bDdlbHJndENhbnJJTi9EClRhRTdIYlZiZmg1Sksv\nRWlvS1hHa1F5c3JjQ1BUSnorUVAxU3NrRkYzUTlETTh2WkZxSHQ4VHdGdFZZQ2hibHMKRFgxOW5H\nMEcrUE1qckF4NlpzV1ZjOEQ4NWJhVDI0eFBWeTBtQVprQWMxVmRrZm8wRFFvZzI5aFdmclkwR2pF\ndApyWSsvQi9VbzJkanN0b0VDa3VGRUVKU1Fubk5iNVgxVldndSs5K0FyZzFBVUxLWllNRE15RDNk\na1ZjamtNZHJMCmVsQWtSYzhCclNFa3RlTjlvemx0MGIxY2ZxZE1ZTGJYQ2tMb0xKM29OWWZXdE5t\nV2tOM0tKUzZaUm8rd2VUUnIKeEJ3NUVUbEhXWldFdjlVc3hPaXUzdTlPMkNPTWxjbkcvRG1CREhR\nZUxDZlhZZmNmemlrSlBDM2YvaVYvNWh0RwppU0NkaHg5WnJQK2lyazZTMXNvd0NkNHRielloU1pL\ndDhPNFpHKzZJM2s0dklSU1VBb25BcS9DUHlWS1h5Sm9ZCnFHalZRZFJWekhWRzNTQnZzblI5aG54\nQStoUmgvMjhySU1GVmNPUy9FdHhPQ2VrZGJ1T2RUWmRLdmh6WVdydWUKb3grOWxTeW1tcnArRjJt\nTEJySlBkdVZEK3d0TWdKVVo1bEVHeFU0YTEzQUNiT0xtQ3QzT1ZQZ0xORnlJeXZDUQpIVnlKN0ZV\nOHFwKzVUNXdvU0hBTVQ4bzBUZENDWVJwQVFHV3dpOWNQL2cyVkw0Z3FCaS94WmJqSVNhdkN0L0xZ\nCjN4MzhjdWZLVUNKbHpzYk5rOUdKeUVaYlg0NHVhcUViUjlKdDQ5cVBSTDI2TkVnU25DQ2I0eVJH\nRVArQ2JLZzIKdHo4SXV3N0lPQnFJdVFjN0lyNURaWDVUVytkdnVTQTBMQjFaYVhZc0V2YlVETXVF\nK29lL2NicjIxMnVGenprRgpZMi9mK2pFOG51RFZBU1VqcDgwM0o1UE5oMVo4RTA0WTVWNUl6cW5l\nb2I3c1pJNExaM0dnelBFR1AxTXpvMk9nCjNiSVI5S0dZVE91K0dCeTZXaVY2anJZQmZoM2R4WkRr\nbFo1b3A0MG50eU9uYkUxSXc1RVhmSGFENGkwZ2dNL1AKVWpldG9ZS2xBZ01CQUFFQ2dnUUFmaVU5\nUzBiaEhueXpGdlVqUkVoN01vU3ZGMVlDNDdLcjZwRFY0RVdTWVFRWAo5YzE1STJOQTVhZGd3RitV\nQUZGU2taTUhjRmZEcVhvUE9QUlNXa2xmK010TjN2S2ljbk1ZYXBuV3duTDJZQ2FFCkRBamxQNmky\nSE5rK0xhS0JCTHNOUFhKak5yMDZVQ2czY2xKSWU3WHhncHh1dFJkcHdRS0hJRVJzeTFsa2NHRkkK\nL3owNG9kbXVxdDk4cTd6TGgrSGpBUGptRDNkbDVjQ3VDbGp1YWpHaHpxclk0d2hvUXJTWEY3TG1Z\nNW1TeXMyMgp4WmZRMGMzVVg3dkR2ZGgwK25hellYYm5mbGQxVm1Eb3FrOEsyT0NyaUdFd2tyOEpO\nTlpCRWpSRms3b1RrclFOCmMyMjM0NExmRmpXNi9SMGpCV202ZGVlQ3o4SzQzd0RTaUdyMmtwZXls\nOFd6amVxcjYxNm9zMWJZbThHa0J5dUkKTzk1Y3Vlc3hPMkxndDJMZk52VisyTTVUQmNpY042WEtx\nSGI3S3BGckpWSUltSUFXTmQvV1E1c0g4VWdqbkVsMQpYb2lFa09ReHBwVVo2OXJlNU1BT0N6cUxv\nV0Y5YnZaM0M3NTRadCtFalZyekd1TFBGU3l3VVZHZWVNRFc3VS81Ck5YQWRRclh1VFdtM09SUlN5\naGFZQllRKy9oZjBqSVlHeklOM3ZmVHFwWDVHM0NoekU5U2E5Vzh5eVVuRDlyQlUKaWR3V2h4Q3RK\nZWc4UFJwczM2WDNKWjY4Q0JWdmNHeVJNYi80cjhkSjhUM3NhSUFUSWZBellYcE54OXY4d3VYNwpm\nMXRidm9OZzJNZmh6eDhxSzNZaU95TUhTcVAxdElHR0c1TWorV1pyUkZOUTBYTlhnczlzSmJiRlEx\nRHJWUnNBCmtqL3RObFVKVGk3VUNRaGZwTzZ5d2EwOURUenNnUUs1RDQzV2x0dmRpWkxWeHlmbDJ4\nNW9wQTVETnlta0VyaHEKeFN3VHdCbGx1RFEwN1lFUUdKWDRXaHlVT1Zqd3pOOXpFaTc4V1pWY3Ar\nUUV6Y0hPcHp4a3ExSHY5Tlk2MWdKRQpTOHdlVEJKcDdrU2hER1NybU5WSVJSdUtMcGVxUHRpSUlC\neDdQaHhCYnVnQXdvR0l3SkpUTUdTVFVuWVRCT3JaCmt5Wi9od2pPa1JYdVBrZU9xTE5JZ0NnUXBy\nUTluWE5IYlV0dnA4ZkNNbEF1aWl4RU8rQ3BPaC8yV3hTQy9zSTYKdUZ0MVhtRTBueGFyMHVRdUQ2\nUDFSRjRoNjVBa3lQa1FpeGVCNEFSSytwckRuYmhQdm5qNmZJNzZqeWR6bUtKNQo2YlFVVUhrOVFz\ndTB6eU1sNHdiSWRqM0ozMUpyS0VIQXhKdXI3dTZ2TjYyMnlyTytjNk5QbjJiTEhvNzBwUVBGCnBG\najJKd1Ywdy85NTd2c2JRb1RycFpQRTcvZSsyYUVYd05neVFkYlZuUFJMQURSUS9mNEI3Q3haQ2xh\ndU5XTWkKRGJzcit0NEFaSzZpbDl6TDNJY1AxS1Y1aGp0N2VCK2pqZ3RyMGFwekZGa2FvdDYyMktp\nSGI2M3l5TkhPWHpwNgp6ZDVWaWR2SEh0bDZYbzl0Nys5LzVoa1E4Tzc1Qy85VGZQOXVFcW9BVFhv\nYlJUUWx0S1VUUkNqR1dGU3N0citoCkJhb2pSTkVVdU11UjZPNU5wTlJmaHFDdGlPNHc4bEtWK000\nSFlZMDJEdjRYaklCb3VmZThnc2ZDTkw0S0VBcGEKMDR6dEkwdVNTRVgwT0dYZ1g4UTFNQmcwQ0VE\nbVRoS0Vmb0FWKy9Sb0FRS0NBZ0VBK0Z6Y05yZ2JiVnFzRzRDZwordHFlTWZSTXBQUXQrUWxYUzZm\ncVpBdG5ORnZocUV0ckUwMFF2eExsRGYwNDNpV1FvYTZONzFyb2dXYWlHU0tPCmlOUU5zUGFmN2VM\nNUNlUjVMUUwxQUlmekFwTTF6QWJDa1V1enA5RzdrWmFJM2tmcVV1SXBPUUpLTkZjQlF2dUIKclln\nalFMWVorbXZjMmVyeVRSSkY5Z3M5L0pkRjlxTUxrNmF5Vnl5emlXcUVZOWRXWFUzNWFJRE1lZk5D\nSGhBVAovZTdVakt5SlNRaE5aSExLVXBKYUZCSHJ3RWxHWVVYaTgvMWUraDJDL3N3RjFXS0wwS3k0\nUjF6K0gvRGYyMC95Cmh2YlI2UUpKNDFoSWFuRHFaZ3VxUGN1SjVFcEZ1TXQyci9aYzNTYjdTM2lX\nWnB6MFRzTGptaWhwRFJXaHBKWjUKVGFDMWFMbEhaUUhnVUkrZjZjU2g4NjQ4c3Y5aG9jcm12QnhK\naDVLRmRUV2FzRjdjYW5ZUGJ5SFBtK3pLMmdzWApqQmF0RUZjMW1aOFNSNnNOSURyOVpITWtKcEdF\nMXdLcStZcU9VTUpzcXZ6OWRSOXJ5SHVFRzJibmhMMExlSmg3CkVsWkNiZzF0MjFpTk1pVDIwYnd6\nakl5V0g4Z0hFdURBZW5nMGpJNHcwVzl5UFlpQkRwSitxMlZiZFhQOFZuZ1UKdVlxb1dNdFNnOHZC\nMnM3bkJLSkRrNE1SQTVCWmVRYStTdWdBNnVKNnVxOE40VHF1a2ExeGViY1RBS2dOYW4vcQozK2Ri\nQ0xvWDFXMWNRZmhlSVQrLzFzTDBma0xmSGhqc20yRlNsbjFOU0hpNUI4UkdaQ0w5MUE0VkQxOUZr\ncnRHCkM3aVNrTENzWnFVb2RJN1poVnA2dE1wN2s0RUNnZ0lCQVBid3RwTEc3Ukdiejh6T2NpeTJX\nWHBIcElFY3VmbDUKT3luSXkvZVRiNDljV1NSU1dkSW4wUGxJa0haNTJyb0QybGJCbFhRaUE4T1hF\nMUgzWUhjV05VMkcxZFN1OXZKawpLdjlxTjlidXJmQjBrbzVXa0FCY3lWcHg5d25BTjJvMkFLUm1I\nS3Jwd2tzcStRdlg0eE94VytnS09hMjV1M0pvCkp6MFhsNjcxZGZvY29aMVo4bmh2dVpnT1dSOWli\nNUs3NmtJUGhQV1RCcDl6SC9uMjFFRllPRWJTeWRWVFppMDQKTDVkdTVzTEZlaVhIWFhLZUhJVEJs\nRlo2YWpnR3NWL2g0eENTZXo5WnBHUStRU3FreFpCNVJWQjdBQmhwWVFMbQo3M293NWZrUXRoREo5\nekNVWEZDYUpkV1hnMW92eThWTUVId0U4a29idHhxUDdpSllva1NabXBLU0pLRmoreWRtCjlNWThY\nQmxtbWdQU0VLYmRKbTBJc0ZZSzhHS3FMQVpEVTNlT1lOYS9NajlIOXZLK0JCWVdmZ1d0bVdyRjVE\na0cKWGhxOWt3RnNDbXRCelF1c1F5aWNuWldZQ2twV2hZWmd6Q3Fxdzd0ZjBOYVdiKzk1SmY5em9I\nQTArd0xBRTNqeAoxcHVtMDJOMFN4NXQzY1Y3a1hMY1J1UFBzZEs3NythNlVNWEFlSkhwUGxXKy80\nQkg5SWtKSmNNaWxhNnVjL0hKClpEQUZ6bzltNlJqWWNEQzBxQlJiNnJoY3QzUHpnMnU3K2JQZEs3\nZlVCZFhVVTJIa1l6S2MvR0lOeVhhUkRoVEMKU3I4eG8wVldnUFQ3SVFSZi85Lzl0K1QzZDVONzQ3\nQjZ2SDJEOWhjVy82YThFVlFwYVVqWjFySVd4VmxBU1o5TApTaWRuVGxwcFNiRWxBb0lDQUZlKzV3\nWm1FVHFYV0VyM0xPaXpxRVJaM1dKQjZxUWJpcjN0K3orUlQ4c04wekhVClEyWTBTZ0JYdXBrd3A1\nREVrTTZ1anZMTG1XMXVSMEsrRk1GK3ViK1Z3bmNYUTRrZE1UcVgydHR2TElueVhJVlMKdGhjRE9k\ndkdtNUFhTVF6bk40QkU2dTk3UWFBd1JQL1hQNytCWTRNUFV5cElSV1N3UHg2L24vd0hpTVRlNVJi\nNApEN1VBcGUxcW01dW5DRk1GMXp0cnV2d1MxU3NZcUhsYWtOV2NOWGZsMVRMNlBlMkpLTFgzZ3Qr\nb1hUUTRMeWRhCnU0NGNMQndOcFNSRURLT1JCM2lZTFJyNVhjY0hJTytvMVRTZHF4ZTVlVVZiQVdx\ncHJnYVRoSGdFbXhrT3JJZFgKU3Yxcit1OGZRSlV2YTJPaGZDYi9iODRkRE5CVW5pRTZFRzArcEJq\nMXJLV2cvaEU0VFBVWVJXZUVYV21ZRkhSRwo3VEgwaEgzalpFYyt3d0lnNFpxelQweWlFMmt4UlpH\nM2JZQk8ycUgxVGJpU25MQzVYQS9SQjRrZnJOdjdlWVZGCktnYXp6d2YxU05NNFFvdklxQm5TbVov\nY3dWc0NOelZLR2VFbW5KMnBIUERyM2lhakxKaDQ5M1ZtamZ0NGZoZEwKVkhWd1ZwQjZCQUZhY0hB\nUTlCZWo1aUREMUlZd2ppdzJqSXZvMHdWY0FERVVJYzhlWGp3aTMrRVQ0MFR4RU10VAplSk9hV0Fp\na0wxd1pVTHdNTVhUQ1pGN3VNVWFBR1ExUldEZjIweERJUG5kbkJidEE5bkNreHpBbS9KNUhIZkRT\nCk9YWEQ4cHU4ZFR0dmUxK2xGb0YyWTFzeUJuckIzQ0MxRFZCQ3kzVlhGZkhGMC84cUlPdWVSYy90\nNGE4QkFvSUMKQVFDTmxhYVlzWVhydXJLQ2N6dnpkdm9HcWwwZnlpQzNjVk1DdWlaNFpRaHA0a0Vh\nR2oxMXlXNS8vNk1VeXZrbAovbCtKcnFUS1dWWmZKcGZsUHprSURxdXhMOFlhazlielU0dHp0cXNk\naU93aUdqU05lQVJJc09xaCtRWHppVW84Cms0bjZ1TEZuTFhCQk9QcGlWLzNTcExaVmJNZDFYRENs\nZ0NJL1hPK1RXUm16dGdiVCtXYVV0enBxZkkrTTl4dVIKdmp5cWM4dUFJalNCNTdoRjBjZ1JUMHUx\nRDlhNWdYL3NIWExzR0tJbXVxTTJWZ0MyWHdGcS9MTFlnb2UwWitINwpYOENaRitPaWh2dENubzh1\nckJxNm8wMml2Mk5tbThVTHJPMVIyZ2VCcnBzMU5SZU51d0xURkE3dFVGbjNzNy9aCjk2cmI4Tm9h\nczVsZ21YV29LN21lSzVQOHhkNUt5dENOM3ZJcFZ5SlhUZ1N3ZkJrZ0UxeWMxNGFEVHZKVkg4enUK\nS2x3SkNKRnRqMkozOWdNWld1bHM0S2lSQ09BVjRERGlvVXdEZVA1NHFrR3ZEYU5MTmhHcmoyQ3JE\nT21aaGRJNQpJZmJ0MzhzcCs5MzVxM2V5am52QzQ4RHhsTzcydkxwdGRmdmVjdUJ3L1pTMGRibmFL\nT2RVUEFoSlJpUm05MnF0Cmw5WUlERHNWTGU2WHExTkRjZjQ3TkF0NnZyR2ozbEtNSnpSU2RJSGlw\ndGF2Y0NtalEzRzdlcGd4N0xjaXZGUjEKeU9sNnZ5ejUwWThtOHY1NytqOEdIZ3gzREFDZkFyeFlH\ncTVRd1YwanZGMWtHVGp0RVQzY1o5U3dhMU1jTk1Sdgp3MitmWjdJSnV4NEpzM3NjRGtKWGlzOFdm\nUWZhRElvcDB6bEpMbW8yWEhmc0lRS0NBZ0JHVDJ6MnpLcFdZZmR2CmFOYVlYaGJVM1draVJyUWpt\nc2Rmd0JyZ0VhMDdCRThNNU5kK2Y1dnVCcDNCTEFaZS9OZUpKUE9PZ1IwQjNlM24KVkZZWnRwSHJi\nMTBSVmRBbjBweDhwWlB0OEM1M29xQjlOTWV4dGs3cHFhRUJON1JyU1g4aFBOS0Zjd1Zzc1c4MQpk\nVFFvd3B1N1ZFV2w2RmhWdURTaWluTHdXblliQ1RhQkxRNVduQjQ3Y0FPZ1l6Nzd5Q1hzcWpGS083\nL3l4SkV6Cm5oTEVLUmZyUFVDYWQyOC9lWGg3aHRRb1NUd28rOUdJdThjdFFwcGhtMTZVYVc0eURY\ncDk4dnBIWi9zc1NjSkYKaFlBQTRQTUhNbzltRms2cUFvOG5JcjBKRHdqUGxXVkwyN3B6MjRoOVdk\nSk5HNzNsYlh2RUlNVVIxajY3UVFVSQp6SXFYaGtTQWQzcDFmM2IrUytJVWNFOXUxaytIOGVJeFRD\ndVNFQjhnQktzKyt1WitFNm8xNHJyRDNRNkM0YllFCkZZYTJPc2ZqZ2dENkw0N3ZjRGk5RkhJVFhy\nQ2Nsd0RuR0Q4MTBtYzY3bjEydTFML2hMdFdMVDJsd3paQmdWc0YKYXpMZzE1Qi96WVlWR0JLM3Zr\nd2ZQL1FXT3crRnBKUnJoVThsZ2x6ZFZEdEhQUGZTUFNId0k1Vmg5ZlNza0h0bQo4SHYxbC9DdExo\neGVWS3lPVXJVTmlFRmoyRDU1UnhkYkl0VWg4d1ptWVZUZExEZXJoQW5UcEEyWEpwOVRQeHlhCisw\ndURmRFlndk9EMDFOMEo1NUVSRndoNm5xekpVemlBVi80UnZmQkN2V2h3QTFocnkzOEJMUDVhZElO\nUVpqUjgKNko0Yk5TSGo5NHpibEsvRnBiYzhObUdGM3B2NHV3PT0KLS0tLS1FTkQgUFJJVkFURSBL\nRVktLS0tLQo=\n')

    from license_client import open_license, is_online, generate_uid_file

    if not is_online():
        print('[Main] [F]: No internet connection')
        core_state.ready = 'exit'
        core_state_bytes = pickle.dumps(core_state)
        core_memory.buf[:len(core_state_bytes)] = core_state_bytes
        sys.exit()

    if not generate_uid_file(license_client.decrypt(BPU), bytes(APP_VERSION, encoding='utf-8')):
        print("[Main] [F]: Couldn't generate uid.encrypted")
        core_state.ready = 'exit'
        core_state_bytes = pickle.dumps(core_state)
        core_memory.buf[:len(core_state_bytes)] = core_state_bytes
        sys.exit()

    code_err, data_err, lic_type, date_now = open_license(license_client.decrypt(RPI), bytes(APP_VERSION, encoding='utf-8'),
                                                license_client.__spec__.origin)
    # code_err, data_err = 'J29dJ3ue87CV2987IUESNP1Phd83E3h', 'now'

    match code_err:
        case 'J29dJ3ue87CV2987IUESNP1Phd83E3h':
            print(f'[Main] [I]: Expires on {data_err}')
            print('[Main] [I]: Activated')
        case 0:
            print("[Main] [F]: There's no activation file. Program not activated")
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()
        case -1:
            print(f'[Main] [F]: Activated client version: {APP_VERSION} doesn\'t match server version: {data_err}')
            # core_state.ready = 'exit'
            # core_state_bytes = pickle.dumps(core_state)
            # core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            # sys.exit()
        case -2:
            print('[Main] [F]: No internet connection')
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()
        case -3:
            print('[Main] [F]: Datetime is not available')
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()
        case -4:
            print('[Main] [F]: Subscription is outdated')
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()
        case -5:
            print('[Main] [F]: License is corrupted')
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()
        case any:
            print('[Main] [F]: Integrity check failed')
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()

    def core_state_updater(refresh_rate, *args):
        # nonlocal core_state, core_memory
        period = 1 / refresh_rate
        while not is_sigterm:
            time.sleep(period)
            state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(state_bytes)] = state_bytes

    def mouse_btns():
        return 0

    if s.mouse2driver_translate:
        from usb2driver import Mouse2Driver

        if not s.mouse_device:
            print('[Main] [F]: No specified mouse USB device')
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()

        if lic_type not in [2, 3]:
            print("[Main] [F]: The driver doesn't support mouse movements")
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()

        mouse_info = list(map(int, s.mouse_device.split()))
        vid, pid = mouse_info[0], mouse_info[1]

        mouse2driver = Mouse2Driver(vid, pid, mouse_log=s.mouse_report_log,
                                    accumulate_movement=s.accumulate_mouse_movement,
                                    interface=s.mouse_interface,
                                    mouse_api=s.mouse_driver)
        mouse2driver.start(priority=s.driver_priority, manual_parse=s.mouse_manual_parse, parse_dict=s.mouse_parse_dict)
        def mouse_btns():
            return mouse2driver.click
        print('[Main] [I]: Loaded Mouse2Driver')
    # mouse = MouseIs()
    mouse = Mouse()
    # input()
    # time.sleep(2)
    ###mouse.start()
    # time.sleep(3)
    # mouse.connect(api='stm32')
    # time.sleep(2)

    try:
        if s.mouse_driver not in lic_apis[lic_type]:
            print("[Main] [F]: The driver doesn't support mouse movements")
            core_state.ready = 'exit'
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
            sys.exit()
    except Exception as e:
        print("[Main] [F]: The driver doesn't support mouse movements")
        core_state.ready = 'exit'
        core_state_bytes = pickle.dumps(core_state)
        core_memory.buf[:len(core_state_bytes)] = core_state_bytes
        sys.exit()

    if s.mouse_driver == 'proxy' and s.mouse_proxy_manual:
        print('[Main] [I]: Trying auto-connect to LunarBox')
        mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mouse_socket.connect((s.mouse_l_ip, s.mouse_l_port))
        s.mouse_c_ip = mouse_socket.getsockname()[0]
        mouse_socket.close()
    
    if s.mouse_driver == 'interception':
        mouse_info = list(map(int, s.mouse_device.split()))
        vid, pid = mouse_info[0], mouse_info[1]
        if not mouse.connect(vid, pid, api=s.mouse_driver):
            print(f"[Main] [W]: Used mouse API '{s.mouse_driver}' doesn't work!")

            
    ############################################################################################################
    
    elif not mouse.connect(api=s.mouse_driver, c_ip=s.mouse_c_ip, l_ip=s.mouse_l_ip, l_port=s.mouse_l_port):
        # elif not mouse.connect(api='stm32', vid=0x09da, pid=0x5a24, col=1):
        # print(f"[Main] [W]: Used mouse API '{s.mouse_driver}' doesn't work!")
        pass
    # s.mouse_driver = 'stm32'
    ############################################################################################################


    sh = ScreenHandler(queue_size=s.screen_handler_queue_size)
    hm = HookManager(settings=s)

    if s.mouse2driver_translate:
        aim_mouse = AimMouse(s, hm, mouse2driver, aim_hz=s.interpolation_filter_refresh_rate)
    else:
        aim_mouse = AimMouse(s, hm, aim_hz=s.interpolation_filter_refresh_rate)
    aim_mouse.start()
    # mouse_filter = MouseFilter(settings=s)

    models_loaded, aim_model, trigger_model = autocompile(s)
    if not models_loaded:
        print('[Main] [F]: Not all models are loaded')
        hm.terminate()
        sh.terminate()
        # mouse_filter.terminate()
        core_state.ready = 'exit'
        core_state_bytes = pickle.dumps(core_state)
        core_memory.buf[:len(core_state_bytes)] = core_state_bytes
        sys.exit()

    hm.start(bind_sounds=s.bind_sounds, api=s.hookmanager_api)
    # sh.start(region=s.region, queue_mode=s.screen_handler_queue_mode, target_fps=s.screen_handler_fps,
    #          use_dxcam=s.use_dxcam)
    # mouse_filter.start()
    sh.init(region=s.region, target_fps=s.screen_handler_fps, use_dxcam=s.use_dxcam)
    stored_exception = None
    # image = sh.get_frame(wait_next_frame=True)
    image = sh.obtain_frame()

    predictor = Predictor(settings=s, aim_model=aim_model, trigger_model=trigger_model)
    predictor.yolo_get_aims('aim', image)
    predictor.yolo_get_aims('trigger', image)

    # yolo_get_aims(aim_model, 'aim', image, s)
    # yolo_get_aims(trigger_model, 'trigger', image, s)

    core_state.ready = True
    core_state_bytes = pickle.dumps(core_state)
    core_memory.buf[:len(core_state_bytes)] = core_state_bytes

    print("[Main] [I]: Ready")
    print(f"[Main] [I]: Trigger reaction and duration: {hm.reaction} {hm.duration}")
    print(f"[Main] [I]: Aimbot smoothness: {hm.smoothness}")

    # al_x, al_y = 0, 0
    # m_x, m_y = 0, 0

    inference_latency_list = []
    frame_latency_list = []
    # i = 0
    # pidx = PID(0.81, 2.5, 0)
    # pidy = PID(0.58, 0.59, 0)
    # pidx = PID(s.pidx_k, s.pidx_i, s.pidx_d)
    # pidx.differential_on_measurement = False
    # pidx.proportional_on_measurement = True
    # pidy = PID(s.pidy_k, s.pidy_i, s.pidy_d)
    # pidy.differential_on_measurement = False
    # pidx.sample_time = 0.0005
    # pidy.sample_time = 0.0005
    # pidx.output_limits = (-16364, 16364)
    # pidy.output_limits = (-16364, 16364)

    flick_triggered = not s.flick_aim
    triggered_image = None
    is_sigterm = False
    shoot = False
    sst = time.time() + data_err.timestamp() - date_now.timestamp()

    # macro_time = 0
    # hold_time = 0
    # start_time = 0
    # reset_start_time = None

    # max_retraction_time = 0

    # targets_queue = Queue()

    # m2v_click = None
    # if s.mouse2driver_translate:
    #     m2v_click = mouse2driver._click
    #
    # aim_mouse.start()

    # targets_process = Process(target=aimp_target)

    # targets_process = Process(target=aim_process_target, args=(
    #     s, targets_queue, m2v_click, None, None, None, None, None, None, None, None
    # ))

    # s, targets_queue, m2v_click, aim_enabled, lock_mode, lock_hold, lock_toggled, rcs, smoothness,
    #                        dynamic_height, use_pid

    # targets_process = Process(target=aim_process_target, args=(
    #     s, targets_queue, m2v_click, hm._aim_enabled, hm._lock_mode, hm._lock_hold, hm._lock_toggled, hm._macro,
    #     hm._smoothness, hm._dynamic_height, hm._use_pid
    # ))

    # targets_process.start()
    # print(targets_process.is_alive())

    input_terminate = Thread(target=sigterm)
    parent_terminate = Thread(target=parent_is_alive)
    shoot_thread = Thread(target=shoot_target)
    state_updater = Thread(target=core_state_updater, args=(10,))
    # latency_logger_thread = Thread(target=latency_logger)

    # time4core_state = []
    # time4frame = []
    # time4locked_state = []
    # time4macro_calc_1 = []
    # time4macro_calc_2 = []
    # time4inference = []
    # time4trigonometry = []
    # time4mouse_move = []
    # time4fps_count = []

    # latency_logger_thread.start()
    input_terminate.start()
    parent_terminate.start()
    shoot_thread.start()
    state_updater.start()

    while not is_sigterm:
        try:
            if stored_exception is not None:
                break

            st = time.perf_counter()

            core_state.smoothness = round(hm.smoothness, 2)
            core_state.reaction = hm.reaction
            core_state.duration = hm.duration
            core_state.interpolation = hm.interpolation
            core_state.aim = hm.lock_mode or hm.lock_toggled or hm.lock_hold
            core_state.aim_enabled = hm.aim_enabled
            core_state.flickbot_enabled = hm.flickbot_enabled
            core_state.trigger = hm.trigger_mode
            core_state.macro = hm.macro
            core_state.use_pid = hm.use_pid

            # time4core_state.append(time.perf_counter() - t)

            # image = sh.get_frame(wait_next_frame=s.frame_synchronization)
            image = sh.obtain_frame()

            t = time.perf_counter()

            # time4frame.append(time.perf_counter() - t)

            if s.mouse2driver_translate:
                # locked = num2buttons(mouse2driver.click)[0] and hm.aim_enabled
                locked = mouse2driver.click & 1 and hm.aim_enabled
            else:
                locked = hm.lock_mode

            # time4locked_state.append(time.perf_counter() - t)

            if locked or hm.lock_toggled or hm.lock_hold:

                aims, boxes = predictor.yolo_get_aims('aim', image)
                # time.sleep(0.018)

                # time.sleep(0.036)

                aim_mouse.send_targets(aims)

                # if hm.trigger_mode or bool(num2buttons(mouse2driver.click)[4]):
                if hm.trigger_mode and not hm.is_moving and random.randint(1, 100) <= s.trigger_hit_chance:
                    if trigger_model == 'color' and s.color_trigger_mode != 'bbox':
                        if hm.color_trigger_mode == 'color':
                            # image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[
                            #         trigger_width_1:trigger_width_2,
                            #         trigger_height_1:trigger_height_2
                            #         ]

                            # lower_color_rgb = hex2rgb(s.low_trigger_color)
                            # upper_color_rgb = hex2rgb(s.high_trigger_color)

                            # lower_color_hsv = cv2.cvtColor(np.array(lower_color_rgb, dtype='uint8').reshape((1, 1, 3)),
                            #                                cv2.COLOR_RGB2HSV)[0, 0]
                            # upper_color_hsv = cv2.cvtColor(np.array(upper_color_rgb, dtype='uint8').reshape((1, 1, 3)),
                            #                                cv2.COLOR_RGB2HSV)[0, 0]
                            image_hsv = cv2.cvtColor(image[trigger_width_1:trigger_width_2, trigger_height_1:trigger_height_2], cv2.COLOR_BGR2HSV)
                            mask = cv2.inRange(image_hsv, lower_color_hsv, upper_color_hsv)

                            # mask = cv2.inRange(image, lower_color_hsv, upper_color_hsv)

                            changed_pixels = cv2.countNonZero(mask)

                            if changed_pixels >= s.changed_pixels:
                                shoot = True
                        elif hm.color_trigger_mode == 'pixel':
                            if triggered_image is not None:
                                diff = cv2.absdiff(triggered_image, image[
                                                                    trigger_width_1:trigger_width_2,
                                                                    trigger_height_1:trigger_height_2])
                                gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
                                _, threshold_diff = cv2.threshold(gray_diff, s.changed_pixels, 255, cv2.THRESH_BINARY)
                                changed_pixels = cv2.countNonZero(threshold_diff)
                                if changed_pixels >= s.changed_pixels:
                                    shoot = True
                            else:
                                triggered_image = image.copy()[
                                                  trigger_width_1:trigger_width_2, trigger_height_1:trigger_height_2]
                    else:
                        x, y = (s.screen_width - 1) / 2, (s.screen_height - 1) / 2
                        for box in aims:
                            if box[2] >= x >= box[0] and box[3] >= y >= box[1]:
                                # mouse.BtnEvent('left_up', api=s.mouse_driver)
                                # mouse.BtnEvent('left', api=s.mouse_driver)
                                shoot = True
                        # for box in boxes:
                        #     if box[2] + s.region[0] - 1 >= x >= box[0] + s.region[0] - 1 and box[3] + s.region[1] - 1 \
                        #             >= y >= box[1] + s.region[1] - 1:
                        #         # mouse.BtnEvent('left_up', api=s.mouse_driver)
                        #         # mouse.BtnEvent('left', api=s.mouse_driver)
                        #         shoot = True

            # elif hm.trigger_mode or bool(num2buttons(mouse2driver.click)[4]):
            elif hm.trigger_mode and not (s.wait_stop_moving and hm.is_moving) and random.randint(1, 100) <= s.trigger_hit_chance:
                if trigger_model == 'color':
                    if hm.color_trigger_mode == 'bbox':
                        aims = []
                        boxes = enhanced_image2bboxes(image, s.low_trigger_color, s.high_trigger_color,
                                                      morph_iterations=s.morph_iterations_trigger,
                                                      dilate_iterations=s.dilate_iterations_trigger,
                                                      morph_kernel=s.morph_kernel_trigger,
                                                      dilate_kernel=s.dilate_kernel_trigger,
                                                      min_ratio=s.min_ratio_trigger,
                                                      max_ratio=s.max_ratio_trigger)
                        if len(boxes) == 0:
                            continue

                        for box in boxes:
                            aims.append([box[0] + s.region[0] - 1, box[1] + s.region[1] - 1,
                                         box[2] + s.region[0] - 1, box[3] + s.region[1] - 1])

                        x, y = (s.screen_width - 1) / 2, (s.screen_height - 1) / 2

                        for a in aims:
                            if a[2] >= x >= a[0] and a[3] >= y >= a[1]:
                                count = 1
                                if s.trigger_burst_mode:
                                    count = s.trigger_burst_count
                                for _ in range(count):
                                    reaction_time = relu(np.random.normal(hm.reaction,
                                                                          s.trigger_reaction_dispersion) / 1000)
                                    duration_time = relu(np.random.normal(hm.duration,
                                                                          s.trigger_duration_dispersion) / 1000)
                                    cooldown_time = relu(
                                        np.random.normal(s.trigger_cooldown, s.trigger_cooldown_dispersion) / 1000)

                                    time.sleep(reaction_time)
                                    mouse.BtnEvent('left', api=s.mouse_driver, btns_pressed=mouse_btns())
                                    time.sleep(duration_time)
                                    mouse.BtnEvent('left_up', api=s.mouse_driver, btns_pressed=mouse_btns())
                                    time.sleep(cooldown_time)
                    elif hm.color_trigger_mode == 'color':
                        image_hsv = cv2.cvtColor(image[trigger_width_1:trigger_width_2, trigger_height_1:trigger_height_2],
                            cv2.COLOR_BGR2HSV)

                        mask = cv2.inRange(image_hsv, lower_color_hsv, upper_color_hsv)

                        changed_pixels = cv2.countNonZero(mask)

                        if changed_pixels >= s.changed_pixels:
                            count = 1
                            if s.trigger_burst_mode:
                                count = s.trigger_burst_count
                            for _ in range(count):
                                reaction_time = relu(np.random.normal(hm.reaction, s.trigger_reaction_dispersion)
                                                     / 1000)
                                duration_time = relu(np.random.normal(hm.duration, s.trigger_duration_dispersion)
                                                     / 1000)
                                cooldown_time = relu(np.random.normal(s.trigger_cooldown, s.trigger_cooldown_dispersion)
                                                     / 1000)

                                time.sleep(reaction_time)
                                mouse.BtnEvent('left', api=s.mouse_driver, btns_pressed=mouse_btns())
                                time.sleep(duration_time)
                                mouse.BtnEvent('left_up', api=s.mouse_driver, btns_pressed=mouse_btns())
                                time.sleep(cooldown_time)
                    elif hm.color_trigger_mode == 'pixel':
                        if triggered_image is None:
                            triggered_image = image.copy()[
                                              trigger_width_1:trigger_width_2, trigger_height_1:trigger_height_2]
                            continue
                        diff = cv2.absdiff(triggered_image, image[
                                              trigger_width_1:trigger_width_2, trigger_height_1:trigger_height_2])
                        gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
                        _, threshold_diff = cv2.threshold(gray_diff, s.changed_pixels, 255, cv2.THRESH_BINARY)
                        changed_pixels = cv2.countNonZero(threshold_diff)
                        if changed_pixels >= s.changed_pixels:
                            count = 1
                            if s.trigger_burst_mode:
                                count = s.trigger_burst_count
                            for _ in range(count):
                                reaction_time = relu(np.random.normal(hm.reaction, s.trigger_reaction_dispersion)
                                                     / 1000)
                                duration_time = relu(np.random.normal(hm.duration, s.trigger_duration_dispersion)
                                                     / 1000)
                                cooldown_time = relu(np.random.normal(s.trigger_cooldown, s.trigger_cooldown_dispersion)
                                                     / 1000)

                                time.sleep(reaction_time)
                                mouse.BtnEvent('left', api=s.mouse_driver, btns_pressed=mouse_btns())
                                time.sleep(duration_time)
                                mouse.BtnEvent('left_up', api=s.mouse_driver, btns_pressed=mouse_btns())
                                time.sleep(cooldown_time)
                else:
                    aims, boxes = predictor.yolo_get_aims('trigger', image)

                    if len(aims) == 0:
                        continue

                    x, y = (s.screen_width - 1) / 2, (s.screen_height - 1) / 2

                    reaction_time = relu(np.random.normal(hm.reaction, s.trigger_reaction_dispersion) / 1000)
                    duration_time = relu(np.random.normal(hm.duration, s.trigger_duration_dispersion) / 1000)
                    cooldown_time = relu(np.random.normal(s.trigger_cooldown, s.trigger_cooldown_dispersion) / 1000)

                    if hm.flickbot_enabled and not flick_triggered:
                        flick_triggered = True
                        m_x, m_y, move, a_x, a_y = aim(aims, settings=s)
                        if reaction_time > 0.01:
                            mouse.MoveRInterpolated(m_x, m_y, reaction_time, api=s.mouse_driver)
                        else:
                            mouse.MoveR(m_x, m_y, api=s.mouse_driver)
                            time.sleep(reaction_time)
                        mouse.BtnEvent('left', api=s.mouse_driver, btns_pressed=mouse_btns())
                        time.sleep(duration_time)
                        mouse.BtnEvent('left_up', api=s.mouse_driver, btns_pressed=mouse_btns())
                        time.sleep(cooldown_time)
                        continue
                    for a in aims:
                        if a[2] >= x >= a[0] and a[3] >= y >= a[1]:
                            time.sleep(reaction_time)
                            # mouse.BtnEvent('left', api='proxy')
                            mouse.BtnEvent('left', api=s.mouse_driver, btns_pressed=mouse_btns())
                            time.sleep(duration_time)
                            # mouse.BtnEvent('left_up', api='proxy')
                            mouse.BtnEvent('left_up', api=s.mouse_driver, btns_pressed=mouse_btns())
                            time.sleep(cooldown_time)
            elif hm.ragebot:
                aims, boxes = predictor.yolo_get_aims('aim', image)

                m_x, m_y, move = rage_aim(aims, s)

                if move and (abs(m_x) <= s.ragebot_max_flick >= abs(m_y)):
                    if s.mouse2driver_translate:
                        mouse.MoveR(m_x, m_y, api=s.mouse_driver, btn_flag=mouse2driver.click)
                        # mouse.DriverMoveRA(m_x, m_y, btn_flag=mouse2driver.click)
                        time.sleep(s.ragebot_flick_time)
                        mouse.BtnEvent(mouse2driver.click ^ 1)
                        time.sleep(s.ragebot_retract_time)
                        mouse.MoveR(-m_x, -m_y, api=s.mouse_driver, btn_flag=mouse2driver.click)
                        # mouse.DriverMoveRA(0, 0, btn_flag=mouse2driver.click)
                        # mouse.DriverMoveRA(-m_x, -m_y, btn_flag=mouse2driver.click)
                        mouse.BtnEvent(mouse2driver.click)
                        time.sleep(s.ragebot_cooldown_time)
                    else:
                        mouse.MoveR(m_x, m_y, api=s.mouse_driver)
                        time.sleep(s.ragebot_flick_time)
                        mouse.BtnEvent('left', btns_pressed=mouse_btns())
                        time.sleep(s.ragebot_retract_time)
                        mouse.MoveR(-m_x, -m_y, api=s.mouse_driver)
                        mouse.BtnEvent('left_up', btns_pressed=mouse_btns())
                        time.sleep(s.ragebot_cooldown_time)
                    # print(f'Flick {m_x} {m_y}')
            else:
                flick_triggered = not s.flick_aim
                triggered_image = None
                time.sleep(0.0023)

            inference_latency_list.append((time.perf_counter() - t) * 1000)
            inference_latency_list = inference_latency_list[-20:]
            frame_latency_list.append((t - st) * 1000)
            frame_latency_list = frame_latency_list[-20:]

            core_state.inference_latency = round(sum(inference_latency_list) / len(inference_latency_list), 3)
            core_state.frame_latency = round(sum(frame_latency_list) / len(frame_latency_list), 3)

            # # if len(fps_list) > 0:
            # #     core_state.fps = round(sum(fps_list) / len(fps_list), 3)
            # #     fps_list.clear()

            # fps_list.append(1 / (time.perf_counter() - t + 1.e-05))
            # fps_list = fps_list[-200:]

            # time4fps_count.append(time.perf_counter() - t)

        except KeyboardInterrupt:
            stored_exception = sys.exc_info()
            print("[Main] [I]: CTRL+C detected")
            mouse.close()
            # sh.terminate()
            sh.release()
            hm.terminate()
            if s.mouse2driver_translate:
                mouse2driver.stop()
            core_state.ready = False
            core_state_bytes = pickle.dumps(core_state)
            core_memory.buf[:len(core_state_bytes)] = core_state_bytes
        except Exception as e:
            print(f'[Main] [F] Unknown exception! {type(e)} | {e}')
            break

    # targets_process.terminate()
    aim_mouse.terminate()
    # sh.terminate()
    sh.release()
    mouse.close()
    hm.terminate()
    shoot_thread.join()
    state_updater.join()
    # latency_logger_thread.join()
    # update_pidx_controls_thread.join()
    if s.mouse2driver_translate:
        mouse2driver.stop()
    core_state.ready = False
    core_state_bytes = pickle.dumps(core_state)
    core_memory.buf[:len(core_state_bytes)] = core_state_bytes
    parent_terminate.join()
    input_terminate.join()
    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LunarCore')
    parser.add_argument('core_memory', type=str)
    args = parser.parse_args()
    main(args.core_memory)
