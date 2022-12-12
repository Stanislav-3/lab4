from scipy.stats import expon
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


class SimplestStream(QThread):
    def __init__(self, intensity: float, signal: pyqtSignal):
        super(SimplestStream, self).__init__()
        self.IS_RUNNING = False

        self.intensity = intensity
        self.signal = signal

    def update_intensity(self, intensity):
        self.intensity = intensity

    def start(self, priority: 'QThread.Priority' = QThread.TimeCriticalPriority) -> None:
        self.IS_RUNNING = True
        super().start(priority)

    def run(self):
        while self.IS_RUNNING:
            t = expon.rvs(scale=1 / self.intensity)

            self.usleep(int(t * 10**6))

            if self.IS_RUNNING:
                self.signal.emit(time.time(), float(t))

    def stop(self):
        self.IS_RUNNING = False

    def isRunning(self) -> bool:
        return self.IS_RUNNING


class SimplestEvent(QThread):
    def __init__(self, intensity: float, start_service_signal: pyqtSignal, stop_service_signal: pyqtSignal,
                 finish_service_signal: pyqtSignal):
        super(SimplestEvent, self).__init__()
        self.IS_RUNNING = False
        self.IS_FINISHED = None

        self.intensity = intensity
        self.start_service_signal = start_service_signal
        self.stop_service_signal = stop_service_signal
        self.finish_service_signal = finish_service_signal

        self.start_time = None

    def update_intensity(self, intensity):
        self.intensity = intensity

    def set_start_time(self, _time):
        self.start_time = _time
        # print(f'Set_start_time, {self.start_time}')

    def start(self, priority: 'QThread.Priority' = QThread.TimeCriticalPriority) -> None:
        # print('Service start')
        self.IS_RUNNING = True
        self.IS_FINISHED = False
        super().start(priority)

    def run(self):
        if not self.isRunning():
            return

        t = float(expon.rvs(scale=1 / self.intensity))
        self.start_service_signal.emit(t)

        self.usleep(int(t * 10**6))
        # print('service wake up after sleep, is running:', self.IS_RUNNING)

        if not self.isRunning():
            return

        self.IS_RUNNING = False
        self.IS_FINISHED = True

        if self.start_time:
            self.finish_service_signal.emit(t, self.start_time + t)

    def stop(self, _time: float):
        self.IS_RUNNING = False
        # print(f'Set self.IS_RUNNING = {self.isRunning()}')

        if self.start_time is not None and not self.isFinished():
            self.stop_service_signal.emit(_time - self.start_time)
            # print('Emitted stop_service_signal')

        self.start_time = None
        # print(f'Set self.start_time = {self.start_time}')

    def isRunning(self) -> bool:
        return self.IS_RUNNING

    def isFinished(self) -> bool:
        return self.IS_FINISHED


class BreakDownStream(QThread):
    def __init__(self, intensity_break_down: float, intensity_repair: float,
                 start_repair_signal: pyqtSignal, finish_repair_signal: pyqtSignal):
        super(BreakDownStream, self).__init__()
        self.IS_RUNNING = False

        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair

        self.start_repair_signal = start_repair_signal
        self.finish_repair_signal = finish_repair_signal

        self.IS_BLOCKED = True

    def update_intensities(self, intensity_break_down, intensity_repair):
        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair

    def set_blocked(self, value: bool):
        self.IS_BLOCKED = value

    def start(self, priority: 'QThread.Priority' = QThread.TimeCriticalPriority) -> None:
        self.IS_RUNNING = True
        super().start(priority)

    def run(self):
        while self.IS_RUNNING:
            if self.IS_BLOCKED:
                continue

            t = expon.rvs(scale=1 / self.intensity_break_down)
            self.usleep(int(t * 10**6))

            if not self.isRunning():
                break

            if self.IS_BLOCKED:
                continue

            start_repair_time = time.time()

            t = float(expon.rvs(scale=1 / self.intensity_repair))

            self.start_repair_signal.emit(t, start_repair_time)

            self.usleep(int(t * 10**6))

            # if self.IS_BLOCKED:
            #     continue

            if not self.IS_RUNNING:
                return

            self.finish_repair_signal.emit(t, start_repair_time + t)

    def stop(self):
        self.IS_RUNNING = False

    def isRunning(self) -> bool:
        return self.IS_RUNNING
