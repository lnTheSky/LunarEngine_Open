__all__ = []


def __dir__():
    return []


from multiprocessing import Value, Queue, Process, current_process, parent_process
from threading import Thread
from mouse import Mouse
import time
import os


class MouseFilter:

    def __init__(self, settings):
        self._started = False
        self._process = None
        self._exit = Value('b', False)
        self._queue = Queue()
        self._input = []
        self.api = settings.mouse_driver

    @property
    def is_alive(self):
        return self._started

    @staticmethod
    def _target(exit_var, queue, api):
        mouse = Mouse()

        if not mouse.connect(api=api):
            print(f'[MouseFilter] [E]: Cannot use API "{api}"')
            exit_var.value = True

        def parent_is_alive():
            par_p = parent_process()
            while True:
                time.sleep(5)
                if not par_p.is_alive():
                    break
            mouse.close()
            os.kill(current_process().pid, 15)

        is_alive = Thread(target=parent_is_alive)
        is_alive.start()

        while not exit_var.value:
            try:
                if queue.empty():
                    (to, xo, yo, flago), (t, x, y, flag) = queue.get()
                else:
                    while not queue.empty():
                        (to, xo, yo, flago), (t, x, y, flag) = queue.get()

                mouse.MoveRInterpolated(xo, yo, round(t - to, 5), flago)
            except Exception as e:
                print(f'[MouseFilter] [W]: Handled exception {e}')

        mouse.close()

    def clear(self):
        self._input.clear()

    def move(self, x, y, current_time, btn_flag=0):

        if len(self._input) != 0:
            self._queue.put([self._input, [current_time, x, y, btn_flag]])

        self._input = [current_time, x, y, btn_flag]

    def start(self):

        if self._started:
            print("[MouseFilter] [W]: Filter already started")
            return self._started

        self._exit.value = False

        self._process = Process(target=self._target, args=(self._exit, self._queue, self.api))

        print("[MouseFilter] [I]: Starting...")

        self._process.start()

        self._started = True

        return self._started

    def terminate(self):

        if not self._started:
            print("[MouseFilter] [W]: Unable to terminate process. Filter isn't running")
            return self._started

        print("[MouseFilter] [I]: Terminating process...")

        self._started = False
        self._exit.value = True

        time.sleep(0.4)

        self._process.terminate()

        print("[MouseFilter] [I]: Process terminated")
        print("[MouseFilter] [I]: Closing process")

        time.sleep(0.4)

        self._process.close()
        del self._process
        self._process = None

        print("[MouseFilter] [I]: Successfully closed!")

        return True


class MouseFilter2:

    def __init__(self, alpha: float = 0.5, samp_rate: int = 1000):
        self.alpha = alpha
        self.exp_value = 0

        self.sampling_rate = samp_rate
        self.buffer = []

        self.time_f = time.perf_counter
        self.current_time = self.time_f()

    def reset(self):
        self.exp_value = 0
        self.buffer.clear()

    def exp_smooth(self, value):
        self.exp_value = self.alpha * value + (1 - self.alpha) * self.exp_value
        return self.exp_value

    def move(self, x, y, btn_flag: int = 0, scroll: int = 0):
        self.buffer.append()
