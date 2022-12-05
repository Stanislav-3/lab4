from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


class TimeWatcher(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    update_time_signal = pyqtSignal(str, float)

    def __init__(self, interval: float):
        super(TimeWatcher, self).__init__()
        self.IS_RUNNING = False

        self.state = 'idle'
        self.prev_state_time = None

        self.interval = interval

        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.timeout)

        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)

    def set_state(self, state, _time):
        if not self.IS_RUNNING:
            return

        if not self.prev_state_time:
            self.state = state
            self.prev_state_time = _time

        if state != 'idle' and state != 'service' and state != 'broken':
            raise ValueError(f'Unknown state: {state}')

        delta = _time - self.prev_state_time
        prev_state = self.state

        self.state = state
        self.prev_state_time = _time

        self.update_time_signal.emit(prev_state, delta)

    def timeout(self):
        if self.prev_state_time is None:
            return

        new_time = time.time()
        secs = new_time - self.prev_state_time
        self.prev_state_time = new_time

        self.update_time_signal.emit(self.state, secs)

    def run(self):
        self.IS_RUNNING = True
        # self.start_timer_signal.emit(self.interval)

    def stop(self):
        self.IS_RUNNING = False
        self.state = 'idle'

        self.stop_timer_signal.emit()

    def isRunning(self) -> bool:
        return self.IS_RUNNING
