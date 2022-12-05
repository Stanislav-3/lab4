from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


class TimeWatcher(QThread):
    update_time_signal = pyqtSignal(str, float)

    def __init__(self):
        super(TimeWatcher, self).__init__()
        self.IS_RUNNING = False

        self.state = 'idle'
        self.state_time = None

    def set_state(self, state, _time):
        if state != 'idle' and state != 'service' and state != 'broken':
            raise ValueError(f'Unknown state: {state}')

        if not self.IS_RUNNING:
            return

        if self.state_time is None:
            self.state = state
            self.state_time = _time

        delta = _time - self.state_time
        prev_state = self.state

        self.state = state
        self.state_time = _time

        self.update_time_signal.emit(prev_state, delta)

    def run(self):
        self.IS_RUNNING = True

    def stop(self):
        self.IS_RUNNING = False
        self.state = 'idle'

    def isRunning(self) -> bool:
        return self.IS_RUNNING
