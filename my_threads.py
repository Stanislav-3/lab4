from scipy.stats import expon
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time


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
            # time.sleep(t)
            # if self.IS_RUNNING:
            #     self.signal.emit()

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
        self.timer.setSingleShot(True)

        # signals
        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)

        self.timer.timeout.connect(self.event_finished)

    def update_intensity(self, intensity):
        self.intensity = intensity

    def run(self):
        self.IS_RUNNING = True
        self.IS_FINISHED = False

        t = expon.rvs(scale=1 / self.intensity, random_state=self.random_state)
        self.start_timer_signal.emit(float(t))

    def event_finished(self):
        self.IS_RUNNING = False
        self.IS_FINISHED = True
        self.finished_signal.emit()

    def stop(self):
        self.stop_timer_signal.emit()
        self.IS_RUNNING = False

        self.wait()

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

        self.break_down_signal.emit(t)
        t = expon.rvs(scale=1 / self.intensity_repair, random_state=self.random_state)
        self.start_timer_signal.emit(t)

    def stop(self):
        self.stop_timer_signal.emit()


class ProgressBarThread(QThread):
    def __init__(self, signal: pyqtSignal):
        super(ProgressBarThread, self).__init__()

        self.signal = signal
        self.interval = None
        self.IS_RUNNING = None

    def set_secs(self, secs):
        self.interval = secs / 100

    def run(self) -> None:
        self.IS_RUNNING = True

        i = 1
        while i <= 100 and self.IS_RUNNING:
            time.sleep(self.interval)
            self.signal.emit(i)
            i += 1

        self.stop()

    def stop(self):
        self.IS_RUNNING = False
        self.signal.emit(0)


# TODO: timers move to QThread
class TimeWatcher(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    update_idle_time_signal = pyqtSignal(float)
    update_service_time_signal = pyqtSignal(float)
    update_broken_time_signal = pyqtSignal(float)

    def __init__(self, interval: float):
        super(TimeWatcher, self).__init__()

        self.IS_RUNNING = False

        self.state = 'idle'
        self.prev_time = None

        self.interval = interval

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)

        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)

    def set_state(self, state):
        if not self.IS_RUNNING:
            return

        if state == 'idle' or state == 'service' or state == 'broken':
            self.state = state
            self.prev_time = time.time()
        else:
            raise ValueError(f'Unknown state: {state}')

    def timeout(self):
        if self.prev_time is None:
            return

        new_time = time.time()
        secs = new_time - self.prev_time
        self.prev_time = new_time

        if self.state == 'idle':
            self.update_idle_time_signal.emit(secs)
        elif self.state == 'service':
            self.update_service_time_signal.emit(secs)
        elif self.state == 'broken':
            self.update_broken_time_signal.emit(secs)

    def run(self):
        self.IS_RUNNING = True

        self.start_timer_signal.emit(self.interval)

    def stop(self):
        self.IS_RUNNING = False

        self.stop_timer_signal.emit()
        self.state = 'idle'



