# import time
# import scipy
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
from my_threads import SimplestStream, SimplestEvent, BreakDownEvent, TimeWatcher
import random


class QueueingSystem(QThread):
    # Signals
    new_request_signal = pyqtSignal()
    request_finished_signal = pyqtSignal()
    break_down_signal = pyqtSignal(float)
    repair_signal = pyqtSignal()

    # Additional signals
    # service_started_signal = pyqtSignal(float)
    start_timer_signal = pyqtSignal(float)
    stop_timer_signal = pyqtSignal()
    update_timer_signal = pyqtSignal(float, float, float, float, float)
    update_theoretical_characteristics_signal = pyqtSignal(float, float, float, float, float)

    def __init__(self, X, Y, R, random_state=None) -> None:
        # Super class init
        super(QueueingSystem, self).__init__()
        self.IS_RUNNING = False

        # Intensities
        self.X = X
        self.Y = Y
        self.R = R
        self.random_state = random_state

        # Statistics
        self.requests = 0
        self.finished = 0
        self.rejected_on_break_down = 0
        self.rejected_on_request = 0
        self.rejected_on_service = 0
        self.break_downs = 0

        self.idle_time = 0
        self.service_time = 0
        self.broken_time = 0

        # Characteristics
        self.s0 = None
        self.s1 = None
        self.s2 = None
        self.A = None
        self.Q = None

        self.s0_empirical = None
        self.s1_empirical = None
        self.s2_empirical = None
        self.A_empirical = None
        self.Q_empirical = None

        # Signal connections
        self.new_request_signal.connect(self.new_request)
        self.request_finished_signal.connect(self.request_finished)

        self.break_down_signal.connect(lambda secs: self.break_down(repaired=False))
        self.repair_signal.connect(lambda: self.break_down(repaired=True))

        # Streams & events
        self.request_stream = SimplestStream(X, self.new_request_signal, random_state=self.random_state)
        self.service_event = SimplestEvent(Y, self.request_finished_signal, random_state=self.random_state)
        self.break_stream = BreakDownEvent(self.X, self.R, self.break_down_signal, self.repair_signal,
                                           self.service_event.start_timer_signal, random_state=self.random_state)

        # States
        self.is_channel_blocked = False

        # Update outputs timer
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_characteristics_empirical)
        # self.start_timer_signal.connect(lambda secs: self.timer.start(secs * 1000))
        # self.stop_timer_signal.connect(self.timer.stop)

        self.timer_update_interval_secs = 0.15

        self.time_watcher = TimeWatcher(self.timer_update_interval_secs)
        self.time_watcher.update_idle_time_signal.connect(lambda secs: self.update_time_and_characteristics('idle', secs))
        self.time_watcher.update_service_time_signal.connect(lambda secs: self.update_time_and_characteristics('service', secs))
        self.time_watcher.update_broken_time_signal.connect(lambda secs: self.update_time_and_characteristics('broken', secs))

    def update_time_and_characteristics(self, state, secs):
        if state == 'idle':
            self.idle_time += secs
        elif state == 'service':
            self.service_time += secs
        elif state == 'broken':
            self.broken_time += secs
        else:
            raise ValueError('Unknown state')

        self.update_empirical_characteristics()

    def update_empirical_characteristics(self):
        all_time = self.idle_time + self.service_time + self.broken_time
        s0 = self.idle_time / all_time
        s1 = self.service_time / all_time
        s2 = self.broken_time / all_time

        A = self.finished / all_time
        Q = A / self.X

        self.update_timer_signal.emit(s0, s1, s2, A, Q)

    def update_theoretical_characteristics(self):
        self.s0 = 1 / (1 + self.X / self.Y + self.X**2 / (self.R * self.Y))
        self.s1 = 1 / (1 + self.Y / self.X + self.X / self.R)
        self.s2 = 1 - self.s0 - self.s1

        self.A = self.X * self.s0
        self.Q = self.A / self.X

        self.update_theoretical_characteristics_signal.emit(self.s0, self.s1, self.s2, self.A, self.Q)

    def update_intensities(self, X, Y, R):
        was_running = self.IS_RUNNING
        if was_running:
            self.stop()

        self.X = X
        self.Y = Y
        self.R = R
        self.update_theoretical_characteristics()

        self.request_stream.update_intensity(self.X)
        self.service_event.update_intensity(self.Y)
        self.break_stream.update_intensities(self.X, self.R)

        self.requests = 0
        self.finished = 0
        self.rejected_on_break_down = 0
        self.rejected_on_request = 0
        self.rejected_on_service = 0
        self.break_downs = 0

        self.idle_time = 0
        self.service_time = 0
        self.broken_time = 0

        if was_running:
            self.start()

    def break_down(self, repaired: bool):
        if repaired:
            self.is_channel_blocked = False
            self.time_watcher.set_state('idle')
            print('Repair')
            return

        # break down
        self.service_event.stop()
        self.wait()
        self.time_watcher.set_state('broken')

        if not self.service_event.isFinished():
            self.rejected_on_break_down += 1

        self.is_channel_blocked = True
        self.break_downs += 1
        print('Break down')

    def new_request(self):
        self.requests += 1

        if self.is_channel_blocked:
            self.rejected_on_request += 1
            print('New request: rejected')
            return

        print('New request: accepted')
        self.time_watcher.set_state('service')
        self.is_channel_blocked = True
        self.service_event.start()

    def request_finished(self):
        print('Request: finished')
        self.time_watcher.set_state('idle')
        self.finished += 1
        self.is_channel_blocked = False

    def run(self):
        print('Run')
        self.IS_RUNNING = True
        self.start_timer_signal.emit(self.timer_update_interval_secs)
        self.request_stream.start()
        self.time_watcher.start()

    def stop(self):
        self.IS_RUNNING = False
        self.request_stream.stop()
        self.service_event.stop()
        self.break_stream.stop()
        self.time_watcher.stop()
        self.stop_timer_signal.emit()
        self.wait()

        if self.is_channel_blocked and not self.service_event.isFinished():
            self.rejected_on_service += 1

        self.is_channel_blocked = False