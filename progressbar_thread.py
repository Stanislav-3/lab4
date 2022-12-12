from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import time
from PyQt5 import QtCore


class ProgressBarThread(QThread):
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()

    def __init__(self, signal: pyqtSignal):
        super(ProgressBarThread, self).__init__()

        self.signal = signal
        self.interval = None
        self.IS_RUNNING = None
        # self.time = None

        self.timer = QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)

        self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        self.stop_timer_signal.connect(self.timer.stop)

        self.timer.timeout.connect(self.timeout)
        self.count = 0

    def timeout(self):
        self.count += 2

        if self.count <= 100 and self.IS_RUNNING:
            self.signal.emit(self.count)
        else:
            self.stop()

    def set_secs(self, secs):
        self.interval = secs / 100

    def start(self, priority: 'QThread.Priority' = QThread.InheritPriority) -> None:
        self.IS_RUNNING = False
        super(ProgressBarThread, self).start(priority)

    def run(self) -> None:
        self.IS_RUNNING = True
        self.start_timer_signal.emit(self.interval)

    def stop(self):
        self.IS_RUNNING = False
        self.stop_timer_signal.emit()
        self.count = 0
        self.signal.emit(0)

    def isRunning(self) -> bool:
        return self.IS_RUNNING