from scipy.stats import expon
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


class SimplestStream(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    def __init__(self, intensity: float, signal: pyqtSignal, random_state: float = None):
        super(SimplestStream, self).__init__()
        self.initial_start = True

        self.intensity = intensity
        self.signal = signal
        self.random_state = random_state

        self.IS_RUNNING = False

        # timer
        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.setSingleShot(True)

        # signals
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

            t = expon.rvs(scale=1 / self.intensity, random_state=self.random_state)

            self.start_timer_signal.emit(float(t))

    def stop(self):
        self.IS_RUNNING = False
        # maybe can start after stopping if run executes
        self.stop_timer_signal.emit()

        self.wait()

    def isRunning(self) -> bool:
        return self.IS_RUNNING


class SimplestEvent(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    def __init__(self, intensity: float, finished_signal: pyqtSignal, random_state: float = None):
        super(SimplestEvent, self).__init__()
        self.initial_start = True

        self.intensity = intensity
        self.finished_signal = finished_signal
        # self.started_signal = started_signal
        self.random_state = random_state

        self.IS_RUNNING = False
        self.IS_FINISHED = False

        # timer
        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.setSingleShot(True)

        # signals
        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)

        self.timer.timeout.connect(self.event_finished)

    def update_intensity(self, intensity):
        self.intensity = intensity

    def run(self):
        # print('SIMPLEST_EVENT.RUN(): START SERVICE')
        self.IS_RUNNING = True
        self.IS_FINISHED = False

        t = expon.rvs(scale=1 / self.intensity, random_state=self.random_state)

        if self.IS_RUNNING:
            # print('>>SIMPLEST_EVENT.RUN(): EMIT SIGNAL')
            self.start_timer_signal.emit(float(t))

    def event_finished(self):
        self.IS_RUNNING = False
        self.IS_FINISHED = True
        self.finished_signal.emit()

    def stop(self):
        self.stop_timer_signal.emit()
        self.IS_RUNNING = False

        self.wait()
        # print('SIMPLEST EVENT.STOP(): Request stopped to service')

    def isRunning(self) -> bool:
        return self.IS_RUNNING

    def isFinished(self) -> bool:
        return self.IS_FINISHED


class BreakDownEvent(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    def __init__(self, intensity_break_down: float,
                 intensity_repair: float,
                 break_down_signal: pyqtSignal,
                 repair_signal: pyqtSignal,
                 start_service_signal: pyqtSignal,
                 random_state: float = None):

        super(BreakDownEvent, self).__init__()
        self.initial_start = True

        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair
        self.break_down_signal = break_down_signal
        self.repair_signal = repair_signal
        self.start_service_signal = start_service_signal
        self.random_state = random_state

        # timer
        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.setSingleShot(True)

        self.timer.timeout.connect(self.repair_signal.emit)

        # signals
        self.start_service_signal.connect(self.check_break_down)

        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)

    def update_intensities(self, intensity_break_down, intensity_repair):
        self.intensity_break_down = intensity_break_down
        self.intensity_repair = intensity_repair

    def check_break_down(self, service_time: float):
        t = expon.rvs(scale=1 / self.intensity_break_down, random_state=self.random_state)

        # TODO: maybe change logic ( continuous break down stream )
        if t >= service_time:
            return

        t = expon.rvs(scale=1 / self.intensity_repair, random_state=self.random_state)
        self.break_down_signal.emit(t)
        self.start_timer_signal.emit(t)
        # print('TIME WHEN BREAK DOWN: ', time.time())

    def stop(self):
        self.stop_timer_signal.emit()