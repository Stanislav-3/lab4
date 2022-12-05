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
                self.signal.emit()

    def stop(self):
        self.IS_RUNNING = False
        self.wait()

    def isRunning(self) -> bool:
        return self.IS_RUNNING


class SimplestEvent(QThread):
    def __init__(self, intensity: float, start_service_signal: pyqtSignal, stop_service_signal: pyqtSignal,
                 finish_service_signal: pyqtSignal):
        super(SimplestEvent, self).__init__()
        self.IS_RUNNING = False
        self.IS_FINISHED = False

        self.intensity = intensity
        self.start_service_signal = start_service_signal
        self.stop_service_signal = stop_service_signal
        self.finish_service_signal = finish_service_signal

    def update_intensity(self, intensity):
        self.intensity = intensity

    def run(self):
        self.IS_RUNNING = True
        self.IS_FINISHED = False

        t = expon.rvs(scale=1 / self.intensity)
        self.start_service_signal.emit(float(t))
        self.usleep(int(t * 10**6))

        self.event_finished()

    def event_finished(self):
        if not self.IS_RUNNING:
            return

        self.IS_RUNNING = False
        self.IS_FINISHED = True

        self.finish_service_signal.emit()

    def stop(self):
        self.IS_RUNNING = False

        if not self.isFinished():
            self.stop_service_signal.emit()

        self.wait()

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

    def update_intensities(self, intensity_break_down, intensity_repair):
        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair

    def run(self):
        self.IS_RUNNING = True

        while self.IS_RUNNING:
            t = expon.rvs(scale=1 / self.intensity_break_down)
            self.usleep(int(t * 10**6))

            if not self.isRunning():
                break

            t = expon.rvs(scale=1 / self.intensity_repair)
            self.start_repair_signal.emit(float(t))
            self.usleep(int(t * 10**6))

            if not self.IS_RUNNING:
                return

            self.finish_repair_signal.emit()

    def stop(self):
        self.IS_RUNNING = False

    def isRunning(self) -> bool:
        return self.IS_RUNNING
