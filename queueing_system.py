# import time
# import scipy
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
from my_threads import SimplestStream, SimplestEvent, BreakDownEvent


class QueueingSystem(QThread):
    # Signals
    new_request_signal = pyqtSignal()
    request_finished_signal = pyqtSignal()
    break_down_signal = pyqtSignal(float)
    repair_signal = pyqtSignal()

    # Additional signals
    # service_started_signal = pyqtSignal(float)

    def __init__(self, X, Y, R, random_state=None) -> None:
        # Super class init
        super(QueueingSystem, self).__init__()
        self.initial_start = True

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

    def update_intensities(self, X, Y, R):
        self.X = X
        self.Y = Y
        self.R = R

        self.stop()

        self.request_stream.update_intensity(self.X)
        self.service_event.update_intensity(self.Y)
        self.break_stream.update_intensities(self.X, self.R)

        self.start()

    def break_down(self, repaired: bool):
        if repaired:
            self.is_channel_blocked = False
            print('Repair')
            return

        # break down
        self.service_event.stop()
        self.wait()

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
        self.is_channel_blocked = True
        self.service_event.start()

    def request_finished(self):
        print('Request: finished')
        self.finished += 1
        self.is_channel_blocked = False

    def run(self):
        print('Run')
        self.request_stream.start()

    def stop(self):
        self.request_stream.stop()
        self.service_event.stop()
        self.break_stream.stop()
        self.wait()

        if self.is_channel_blocked and not self.service_event.isFinished():
            self.rejected_on_service += 1

        self.is_channel_blocked = False

    # def start(self, priority: 'QThread.Priority' = QThread.InheritPriority) -> None:
    #     if self.initial_start:
    #         self.initial_start = False
    #         super(QueueingSystem, self).start(priority)
    #     else:
    #         self.run()

