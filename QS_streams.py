from scipy.stats import expon
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


class SimplestStream(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    def __init__(self, intensity: float, signal: pyqtSignal):
        super(SimplestStream, self).__init__()
        self.IS_RUNNING = False

        self.intensity = intensity
        self.signal = signal

        # timer
        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.setSingleShot(True)

        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)
        self.timer.timeout.connect(self.signal.emit)

    def update_intensity(self, intensity):
        self.intensity = intensity

    def run(self):
        self.IS_RUNNING = True

        while self.IS_RUNNING:
            if self.timer.isActive():
                continue

            t = expon.rvs(scale=1 / self.intensity)
            self.start_timer_signal.emit(float(t))

    def stop(self):
        self.IS_RUNNING = False
        self.wait()

        self.stop_timer_signal.emit()

    def isRunning(self) -> bool:
        return self.IS_RUNNING


class SimplestEvent(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    def __init__(self, intensity: float, finished_signal: pyqtSignal):
        super(SimplestEvent, self).__init__()
        self.IS_RUNNING = False
        self.IS_FINISHED = False

        self.intensity = intensity
        self.finished_signal = finished_signal

        # timer
        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.setSingleShot(True)

        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)
        self.timer.timeout.connect(self.event_finished)

    def update_intensity(self, intensity):
        self.intensity = intensity

    def run(self):
        # print('SIMPLEST_EVENT.RUN(): START SERVICE')
        self.IS_RUNNING = True
        self.IS_FINISHED = False

        t = expon.rvs(scale=1 / self.intensity)
        self.start_timer_signal.emit(float(t))

    def event_finished(self):
        # print('SIMPLEST EVENT: Request finished')
        self.IS_RUNNING = False
        self.IS_FINISHED = True
        self.finished_signal.emit()

    def stop(self):
        self.IS_RUNNING = False
        self.wait()

        self.stop_timer_signal.emit()
        # print('SIMPLEST EVENT.STOP(): Request stopped to service')

    def isRunning(self) -> bool:
        return self.IS_RUNNING

    def isFinished(self) -> bool:
        return self.IS_FINISHED


class BreakDownEvent(QThread):
    start_break_down_timer_signal = pyqtSignal(float)
    stop_break_down_timer_signal = pyqtSignal()

    start_repair_timer_signal = pyqtSignal(float)
    stop_repair_timer_signal = pyqtSignal()

    def __init__(self, intensity_break_down: float, intensity_repair: float, repair_signal: pyqtSignal):
        super(BreakDownEvent, self).__init__()
        self.IS_RUNNING = None

        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair
        self.repair_signal = repair_signal

        # break down timer
        self.timer_break_down = QTimer(self)
        self.timer_break_down.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer_break_down.setSingleShot(True)

        self.start_break_down_timer_signal.connect(lambda secs: self.timer_break_down.start(secs * 1000))
        self.stop_break_down_timer_signal.connect(self.timer_break_down.stop)
        self.timer_break_down.timeout.connect(self.run_repair)

        # repair timer
        self.timer_repair = QTimer(self)
        self.timer_repair.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer_repair.setSingleShot(True)

        self.start_repair_timer_signal.connect(lambda secs: self.timer_repair.start(secs * 1000))
        self.stop_repair_timer_signal.connect(self.timer_repair.stop)
        self.timer_repair.timeout.connect(self.finish_repair)

    def update_intensities(self, intensity_break_down, intensity_repair):
        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair

    def run(self):
        self.IS_RUNNING = True

        while self.IS_RUNNING:
            self.usleep(15)
            if self.timer_break_down.isActive() or self.timer_repair.isActive() or not self.isRunning():
                continue

            t = expon.rvs(scale=1 / self.intensity_break_down)
            self.start_break_down_timer_signal.emit(float(t))

    def run_repair(self):
        t = expon.rvs(scale=1 / self.intensity_repair)
        self.start_repair_timer_signal.emit(t)

    def finish_repair(self):
        self.repair_signal.emit()

    def stop(self):
        self.stop_break_down_timer_signal.emit()
        self.IS_RUNNING = False

    def isRunning(self) -> bool:
        return self.IS_RUNNING
