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

    def run(self):
        self.IS_RUNNING = True

        while self.IS_RUNNING:
            t = expon.rvs(scale=1 / self.intensity)

            self.usleep(int(t * 10**6))

            if self.IS_RUNNING:
                self.signal.emit(time.time())

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
        print('set_start_time')
        self.start_time = _time

    def start(self, priority: 'QThread.Priority' = QThread.InheritPriority) -> None:
        self.IS_RUNNING = False
        self.IS_FINISHED = False
        super().start(priority)

    def run(self):
        print('RUN'*10)
        self.IS_RUNNING = True
        self.IS_FINISHED = False

        t = float(expon.rvs(scale=1 / self.intensity))
        self.start_service_signal.emit(t)

        self.usleep(int(t * 10**6))

        if not self.isRunning():
            return

        self.IS_RUNNING = False
        self.IS_FINISHED = True

        self.finish_service_signal.emit(t)

    def stop(self):
        self.IS_RUNNING = False

        if self.start_time is not None and not self.isFinished():
            print('Emit stop service signal')
            # TODO: IMPROVE TIME MAYBE USING BREAKDOWN TIME
            # TODO: MAYBE ADD SIGNAL TO BREAKDOWN ADD STOP SERVICE VIA IT
            # TODO: AND ALSO PARSE BREAK DELTA OT TIME
            # TODO: INSTEAD OF USAGE OF time.time() below
            self.stop_service_signal.emit(time.time() - self.start_time)
            print('after emit')

        self.start_time = None

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

        self.is_blocked = True

    def update_intensities(self, intensity_break_down, intensity_repair):
        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair

    def set_blocked(self, value: bool):
        self.is_blocked = value

    def run(self):
        self.IS_RUNNING = True

        while self.IS_RUNNING:
            # if self.is_blocked:
            #     continue

            t = expon.rvs(scale=1 / self.intensity_break_down)
            self.usleep(int(t * 10**6))

            if not self.isRunning():
                break

            if self.is_blocked:
                continue

            t = expon.rvs(scale=1 / self.intensity_repair)
            self.start_repair_signal.emit(float(t), time.time())
            self.usleep(int(t * 10**6))

            if not self.IS_RUNNING:
                return

            self.finish_repair_signal.emit(t)

    def stop(self):
        self.IS_RUNNING = False

    def isRunning(self) -> bool:
        return self.IS_RUNNING
