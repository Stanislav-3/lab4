# import time
# import scipy
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
from queueing_system_streams import SimplestStream, SimplestEvent, BreakDownStream
from time_watcher import TimeWatcher
import time


class QueueingSystem(QThread):
    # signals
    new_request_signal = pyqtSignal()

    start_service_signal = pyqtSignal(float)
    stop_service_signal = pyqtSignal()
    finish_service_signal = pyqtSignal()

    start_repair_signal = pyqtSignal(float)
    finish_repair_signal = pyqtSignal()

    update_empirical_characteristics_signal = pyqtSignal(float, float, float, float, float)
    update_theoretical_characteristics_signal = pyqtSignal(float, float, float, float, float)

    update_state_signal = pyqtSignal(str)

    def __init__(self, X, Y, B, R) -> None:
        # Super class init
        super(QueueingSystem, self).__init__()
        self.IS_RUNNING = False

        # TODO: REMOVE
        self.start_time = None

        # Intensities
        self.X = X
        self.Y = Y
        self.R = R
        self.B = B

        # Statistics
        self.requests = 0
        self.finished = 0
        self.rejected = 0
        self.break_downs = 0

        self.state = None
        self.state_time = None
        self.idle_time = 0.
        self.service_time = 0.
        self.broken_time = 0.

        # temp statistics
        self.prev_new_request_time = None
        self.new_request_delta_time_sum = 0

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

        # Streams & events
        self.request_stream = SimplestStream(self.X, self.new_request_signal)
        self.service_event = SimplestEvent(self.Y, self.start_service_signal, self.stop_service_signal,
                                           self.finish_service_signal)
        self.break_stream = BreakDownStream(self.B, self.R, self.start_repair_signal, self.finish_repair_signal)

        # Signal connections
        self.new_request_signal.connect(self.new_request)
        self.finish_service_signal.connect(self.request_finished)
        self.stop_service_signal.connect(self.service_interrupted)

        self.start_repair_signal.connect(self.start_repair)
        self.finish_repair_signal.connect(self.finish_repair)

        # States
        self.is_channel_blocked = False

        self.timer_update_interval_secs = 0.1

        self.time_watcher = TimeWatcher(self.timer_update_interval_secs)
        self.time_watcher.update_time_signal.connect(self.update_time_and_characteristics)

        self.update_state_signal.connect(self.update_state)

    def update_state(self, state):
        if self.state == 'broken' and state == 'service':
            raise Exception('From broken switched to service!!!!!!!!')

        if state != 'idle' and state != 'service' and state != 'broken':
            raise Exception(f'Unknown state: {state}')

        # print(f'QUEUEING SYSTEM: update_state({state})')
        self.state = state
        self.time_watcher.set_state(self.state, self.state_time)

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

        actual_time = (time.time() - self.start_time)
        # print(f'Actual time: {actual_time}, TimeWatcher: {all_time}, delta: {actual_time - all_time}')

        A = self.finished / all_time
        Q = self.finished / actual_time
        # A = self.finished / (time.time() - self.start_time)
        # Q = A / self.X

        self.update_empirical_characteristics_signal.emit(s0, s1, s2, A, Q)

    def update_theoretical_characteristics(self):
        self.s0 = 1 / (1
                       + self.X / (self.Y + self.B)
                       + self.B / self.R
                       + self.B / self.R * (self.X / (self.Y + self.B)))
        self.s1 = 1 / (1
                       + (self.Y + self.B) / self.X
                       + self.B / self.R
                       + self.B / self.R * ((self.Y + self.B) / self.X))
        self.s2 = 1 - self.s0 - self.s1

        self.Q = self.s0
        self.A = self.X * self.Q

        self.update_theoretical_characteristics_signal.emit(self.s0, self.s1, self.s2, self.A, self.Q)

    def update_intensities(self, X, Y, B, R):
        was_running = self.IS_RUNNING

        if was_running:
            self.stop()
        #     todo: stop other streams too

        self.X = X
        self.Y = Y
        self.B = B
        self.R = R
        self.update_theoretical_characteristics()

        self.request_stream.update_intensity(self.X)
        self.service_event.update_intensity(self.Y)
        self.break_stream.update_intensities(self.B, self.R)

        self.requests = 0
        self.finished = 0
        self.break_downs = 0
        self.rejected = 0

        self.idle_time = 0
        self.service_time = 0
        self.broken_time = 0

        if was_running:
            self.start()

    def service_interrupted(self):
        self.rejected += 1

    def finish_repair(self):
        print('QUEUEING SYSTEM: Repaired')
        self.is_channel_blocked = False
        self.update_state_signal.emit('idle')

    def start_repair(self):
        print('QUEUEING SYSTEM: Broke down')
        self.is_channel_blocked = True
        self.service_event.stop()
        self.break_downs += 1

        self.update_state_signal.emit('broken')
        # self.wait()

    def new_request(self):
        self.state_time = time.time()
        self.requests += 1

        new_time = time.time()
        if self.prev_new_request_time:
            self.new_request_delta_time_sum += (new_time - self.prev_new_request_time)

        self.prev_new_request_time = new_time
        # print(f'Delta: {self.new_request_delta_time_sum / self.requests}')

        if self.is_channel_blocked:
            self.rejected += 1
            # print('QUEUEING SYSTEM: Request rejected')
            return

        print('QUEUEING SYSTEM: Request started to service')

        self.is_channel_blocked = True

        self.service_event.start()
        self.update_state_signal.emit('service')

    def request_finished(self):
        self.state_time = time.time()

        print('QUEUEING SYSTEM: Request finished')

        self.finished += 1
        self.is_channel_blocked = False

        self.update_state_signal.emit('idle')

    def run(self):
        self.IS_RUNNING = True
        self.state_time = time.time()

        self.request_stream.start()
        self.break_stream.start()

        self.start_time = time.time()

        self.update_state_signal.emit('idle')
        self.time_watcher.start()

    def stop(self):
        self.IS_RUNNING = False

        self.time_watcher.stop()
        self.request_stream.stop()
        self.service_event.stop()
        self.break_stream.stop()
        self.wait()

        self.is_channel_blocked = False
        self.update_state_signal.emit('idle')
