from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


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
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
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

    def isRunning(self) -> bool:
        return self.IS_RUNNING