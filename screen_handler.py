__all__ = []


def __dir__():
    return []


import time

import cv2
import os

from typing import Tuple

from win32con import SRCCOPY
from win32gui import GetDesktopWindow, GetWindowDC, ReleaseDC, DeleteObject  # , GetWindowText, EnumWindows
from win32ui import CreateDCFromHandle, CreateBitmap
from cv2 import cvtColor, COLOR_BGRA2RGB, COLOR_RGBA2RGB
# from numpy import fromstring, uint8, ndarray
from numpy import frombuffer, uint8, ndarray
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Queue, Lock, Value, Process, current_process, parent_process
from threading import Thread

import dxcam
from interval_timer import IntervalTimer


class ScreenHandler:

    def __init__(self, queue_size: int = 1):

        self._shared_memory = None
        self._target_fps = None
        self._queue_mode = None
        self._started = False
        self.image = None
        self._process = None
        self._mutex = Lock()
        self._new_frame = Value('b', False)
        self._exit = Value('b', False)
        self._queue = Queue(queue_size)
        self._queue_size = queue_size

    @property
    def new_frame(self):
        return bool(self._new_frame.value)

    @property
    def is_alive(self):
        return self._started

    @staticmethod
    def _dxcam_target(region, queue_mode=True, exit_event=None, queue=None, new_frame=None, mutex=None, queue_size=None, target_fps=None):
        exited = False

        left, top, right, bottom = region

        width = right - left + 1
        height = bottom - top + 1

        left -= 1
        top -= 1
        region = (left, top, right, bottom)

        if not queue_mode:
            shared_memory = SharedMemory("frame_buf")
            data = ndarray((width, height, 3), dtype=uint8, buffer=shared_memory.buf)

        cam = dxcam.create(output_color="BGR", region=region)

        print("[Screen Handler] [I]: Successfully started!")

        if target_fps:
            cam.start(target_fps=target_fps)

        def parent_is_alive():
            par_p = parent_process()
            while True:
                time.sleep(5)
                if not par_p.is_alive():
                    break
            os.kill(current_process().pid, 15)

        is_alive = Thread(target=parent_is_alive)
        is_alive.start()

        while not bool(exit_event.value):
            time.sleep(0.0005)
            # try:
            if target_fps:
                img = cam.get_latest_frame()
            else:
                img = cam.grab()
                if img is None:
                    continue
            # for _ in IntervalTimer(1/400):
            #     img = cam.grab()
            #     if img is not None:
            #         if queue_mode:
            #             if queue.qsize() > queue_size - 1:
            #                 queue.get()
            #             queue.put(img)
            #             new_frame.value = True
            #         else:
            #             with mutex:
            #                 data[:] = img
            #                 # data[:] = img[..., :3]
            #             new_frame.value = True

            if queue_mode:
                if queue.qsize() > queue_size - 1:
                    queue.get()
                queue.put(img)
                new_frame.value = True
            else:
                with mutex:
                    data[:] = img
                    # data[:] = img[..., :3]
                new_frame.value = True
            # except:
            #     print("[Screen Handler] [W]: Handled exception")

        print("[Screen Handler] [I]: Release DXCam")

        if target_fps:
            cam.stop()

        del cam

        if not queue_mode:
            print("[Screen Handler] [I]: Release shared memory")
            shared_memory.close()

        exited = True

    @staticmethod
    def _target(region, queue_mode=True, exit_event=None, queue=None, new_frame=None, mutex=None, queue_size=None,
                target_fps=None):
        exited = False

        h_win = GetDesktopWindow()
        left, top, right, bottom = region

        width = right - left + 1
        height = bottom - top + 1

        hw_in_dc = GetWindowDC(h_win)
        src_dc = CreateDCFromHandle(hw_in_dc)
        mem_dc = src_dc.CreateCompatibleDC()
        bmp = CreateBitmap()
        bmp.CreateCompatibleBitmap(src_dc, width, height)
        mem_dc.SelectObject(bmp)

        if not queue_mode:
            shared_memory = SharedMemory("frame_buf")
            data = ndarray((width, height, 3), dtype=uint8, buffer=shared_memory.buf)

        print("[Screen Handler] [I]: Successfully started! (A Mode)")

        if target_fps:
            wait_time = 1 / target_fps
            sub_time = wait_time
            prev_time = time.time()

        def parent_is_alive():
            par_p = parent_process()
            while True:
                time.sleep(5)
                if not par_p.is_alive():
                    break
            os.kill(current_process().pid, 15)

        is_alive = Thread(target=parent_is_alive)
        is_alive.start()

        while not bool(exit_event.value):
            try:
                mem_dc.BitBlt((0, 0), (width, height), src_dc, (left, top), SRCCOPY)

                signed_int_s_array = bmp.GetBitmapBits(True)
                # img = fromstring(signed_int_s_array, dtype='uint8')
                img = frombuffer(signed_int_s_array, dtype='uint8')
                img.shape = (height, width, 4)

                if queue_mode:
                    if queue.qsize() > queue_size - 1:
                        queue.get()
                    queue.put(cvtColor(img, COLOR_RGBA2RGB))
                    new_frame.value = True
                else:
                    with mutex:
                        data[:] = cvtColor(img, COLOR_RGBA2RGB)
                        # data[:] = img[..., :3]
                    new_frame.value = True
                if target_fps:
                    time.sleep(wait_time)
                    new_time = time.time()
                    error_time = new_time - prev_time - sub_time
                    wait_time = 0 if error_time > wait_time else wait_time - error_time
                    prev_time = new_time

            except:
                print("[Screen Handler] [W]: Handled exception")

        print("[Screen Handler] [I]: Clean compatible DC")
        src_dc.DeleteDC()
        mem_dc.DeleteDC()
        ReleaseDC(h_win, hw_in_dc)
        DeleteObject(bmp.GetHandle())

        if not queue_mode:
            print("[Screen Handler] [I]: Release shared memory")
            shared_memory.close()

        exited = True

    def init(self,  region: Tuple[int, int, int, int], target_fps=None, use_dxcam=False):

        if self._started:
            print("[Screen Handler] [W]: The handler already started")
            return None

        self.left, self.top, self.right, self.bottom = region

        self.width = self.right - self.left + 1
        self.height = self.bottom - self.top + 1

        if not use_dxcam:
            self.h_win = GetDesktopWindow()

            self.hw_in_dc = GetWindowDC(self.h_win)
            self.src_dc = CreateDCFromHandle(self.hw_in_dc)
            self.mem_dc = self.src_dc.CreateCompatibleDC()
            self.bmp = CreateBitmap()
            self.bmp.CreateCompatibleBitmap(self.src_dc, self.width, self.height)
            self.mem_dc.SelectObject(self.bmp)

            # if not queue_mode:
            #     shared_memory = SharedMemory("frame_buf")
            #     data = ndarray((width, height, 3), dtype=uint8, buffer=shared_memory.buf)

            print("[Screen Handler] [I]: Successfully started! (S Mode)")

            if target_fps:
                self.wait_time = 1 / target_fps
                self.sub_time = self.wait_time
                self.prev_time = time.perf_counter()
        else:
            self.left -= 1
            self.top -= 1
            region = (self.left, self.top, self.right, self.bottom)

            self.cam = dxcam.create(output_color="BGR", region=region)

            if target_fps:
                self.cam.start(target_fps=target_fps)

        self._use_dxcam = use_dxcam
        self._target_fps = target_fps

        self._started = True

    def obtain_frame(self, *args, **kwargs):

        if not self._started:
            return None

        if not self._use_dxcam:

            self.mem_dc.BitBlt((0, 0), (self.width, self.height), self.src_dc, (self.left, self.top), SRCCOPY)

            signed_int_s_array = self.bmp.GetBitmapBits(True)
            img = frombuffer(signed_int_s_array, dtype='uint8')
            img.shape = (self.height, self.width, 4)

            if self._target_fps:
                new_time = time.perf_counter()
                error_time = new_time - self.prev_time - self.sub_time
                self.wait_time = 0 if error_time > self.wait_time else self.wait_time - error_time
                self.prev_time = new_time
                time.sleep(self.wait_time)

            return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        else:
            img = None
            if self._target_fps:
                img = self.cam.get_latest_frame()
            else:
                for _ in IntervalTimer(0.001):
                    img = self.cam.grab()
                    if img is not None:
                        break
            return img

    def release(self):

        if not self._started:
            return False

        if self._use_dxcam:
            if self._target_fps:
                self.cam.stop()

            del self.cam
        else:
            self.src_dc.DeleteDC()
            self.mem_dc.DeleteDC()
            ReleaseDC(self.h_win, self.hw_in_dc)
            DeleteObject(self.bmp.GetHandle())

        self._started = False

    def start(self, region: Tuple[int, int, int, int], queue_mode: bool = True, target_fps=None, use_dxcam=False):

        if self._started:
            print("[Screen Handler] [W]: The handler already started")
            return None

        self._exit.value = False

        if use_dxcam:
            self._process = Process(target=self._dxcam_target, args=(region, queue_mode, self._exit, self._queue,
                                                           self._new_frame, self._mutex, self._queue_size, target_fps))
        else:
            self._process = Process(target=self._target, args=(region, queue_mode, self._exit, self._queue,
                                                           self._new_frame, self._mutex, self._queue_size, target_fps))

        self._queue_mode = queue_mode

        print("[Screen Handler] [I]: Starting...")

        if not queue_mode:
            left, top, right, bottom = region

            width = right - left + 1
            height = bottom - top + 1

            n_bytes = ndarray((width, height, 3), dtype=uint8).nbytes
            try:
                self._shared_memory = SharedMemory('frame_buf', create=True, size=n_bytes)
            except FileExistsError:
                self._shared_memory = SharedMemory('frame_buf')
                self._shared_memory.close()
                self._shared_memory = SharedMemory('frame_buf', create=True, size=n_bytes)

            self.image = ndarray((width, height, 3), dtype=uint8, buffer=self._shared_memory.buf)

        self._process.start()

        self._started = True

    def get_frame(self, wait_next_frame=False):

        if not self._started:
            print("[Screen Handler] [W]: Unable to get a frame. The handler isn't running")

        if self._queue_mode:
            if wait_next_frame:
                self.image = self._queue.get()
                self._new_frame.value = False
                return self.image
            while not self._queue.empty():
                self.image = self._queue.get()
            self._new_frame.value = False
            return self.image
        else:
            if wait_next_frame:
                while not self._new_frame.value:
                    pass
            self._new_frame.value = False
            with self._mutex:
                return self.image

    def terminate(self):

        if not self._started:
            print("[Screen Handler] [W]: Unable to terminate process. The handler isn't running")
            return False

        print("[Screen Handler] [I]: Terminating process...")
        self._started = False
        self._exit.value = True
        time.sleep(1)
        self._process.terminate()
        print("[Screen Handler] [I]: Process terminated")
        self.image = None
        if not self._queue_mode:
            print("[Screen Handler] [I]: Closing memory object")
            self._shared_memory.close()
            self._shared_memory = None
        print("[Screen Handler] [I]: Closing process")
        # time.sleep(1)
        self._process.join()
        self._process.close()
        del self._process
        self._process = None
        print("[Screen Handler] [I]: Successfully closed!")
        return True


if __name__ == '__main__':
    a = ScreenHandler()
    a.start(region=(641, 221, 1280, 860), queue_mode=True)
    a.get_frame(wait_next_frame=True)
    time.sleep(3)
    a.get_frame(wait_next_frame=True)
    a.terminate()
