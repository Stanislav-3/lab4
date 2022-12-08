from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


class TimeWatcher(QThread):
    update_time_signal = pyqtSignal(str, float)

    def __init__(self):
        super(TimeWatcher, self).__init__()
        self.IS_RUNNING = False

        self.state = None
        self.state_start_time = None

    def set_state(
            self,
            new_state: str,
            new_state_time: float = None,
            delta: float = None
    ):
        if new_state != 'idle' and new_state != 'service' and new_state != 'broken':
            raise ValueError(f'Unknown state: {new_state}')

        if not self.isRunning():
            return

        if new_state_time:
            delta = new_state_time - self.state_start_time

        if delta < 0:
            print(f'TimeWatcher:\tduration: {delta:.10f},\told_state: {self.state},\tnew_state: {new_state}')

        prev_state = self.state

        # if self.state == 'service':
        #     print(f'TimeWatcher:\tduration: {delta:.10f},\tnew_state: {new_state}')

        self.state = new_state
        self.state_start_time += delta

        self.update_time_signal.emit(prev_state, delta)

    def run(self):
        self.IS_RUNNING = True

        self.state_start_time = time.time()
        self.state = 'idle'

    def stop(self):
        self.IS_RUNNING = False

        self.state = None
        self.state_start_time = None

    def isRunning(self) -> bool:
        return self.IS_RUNNING
