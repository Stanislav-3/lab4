from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QThread
from queueing_system import QueueingSystem
from progressbar_thread import ProgressBarThread
from PyQt5.QtCore import *
import time
import sys


class Test(QThread):
    signal = pyqtSignal()

    def __init__(self, system, output, parent=None):
        super(Test, self).__init__(parent=parent)
        self.queueing_system = system
        self.output = output

    def run(self) -> None:
        for i in range(1000):
            print(i)
            self.queueing_system.start()
            time.sleep(0.01)
            self.queueing_system.stop()
            self.queueing_system.wait()
            if self.queueing_system.requests != self.queueing_system.rejected_on_request \
                                                + self.queueing_system.rejected_on_service \
                                                + self.queueing_system.finished:
                self.output.setText(f'i: {i}\n' +
                                    f'Requests: {self.queueing_system.requests}\n'
                                    f'Rejected_on_request: {self.queueing_system.rejected_on_request}\n'
                                    f'Rejected_on_service: {self.queueing_system.rejected_on_service}\n'
                                    f'Finished: {self.queueing_system.finished}\n'
                                    f'Break downs: {self.queueing_system.break_downs}\n\n'
                                    )
                return

        # self.output.setText(f'i: {i}\n' +
        #                     f'Requests: {self.queueing_system.requests}\n'
        #                     f'Rejected_on_request: {self.queueing_system.rejected_on_request}\n'
        #                     f'Rejected_on_service: {self.queueing_system.rejected_on_service}\n'
        #                     f'Finished: {self.queueing_system.finished}\n'
        #                     f'Break downs: {self.queueing_system.break_downs}\n\n'
        #                     )
        self.output.setText(self.output.text() + 'Done')
        self.stop()

    def stop(self):
        self.quit()


class Window(QMainWindow):
    set_repair_progressbar_value_signal = pyqtSignal(int)
    set_service_progressbar_value_signal = pyqtSignal(int)

    intensity_updated_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Queueing system
        self.X = 10.
        self.Y = 150.
        self.B = 10.
        self.R = 100.
        self.queueing_system = QueueingSystem(self.X, self.Y, self.B, self.R)
        self.output_precision = 5

        # QMainWindow
        desktop_rect = QApplication.desktop().screenGeometry()
        self.width = 1200
        self.height = 500
        self.left = round((desktop_rect.width() - self.width) / 2)
        self.top = round((desktop_rect.height() - self.height) / 2)

        self.setWindowTitle("Queueing system")
        self.setGeometry(self.left, self.top, self.width, self.height)

        # QWidget properties
        self.buttons_width = 100
        self.buttons_height = 30

        # Buttons
        self.start_button = QPushButton('Start', self)
        self.stop_button = QPushButton('Stop', self)
        self.test_button = QPushButton('Test', self)
        self.run_button = QPushButton('Run', self)
        self.output = QLabel('Text Label', self)

        # Inputs
        self.prev_text = None

        self.x_splitter = QSplitter(self)
        self.x_splitter.setOrientation(Qt.Horizontal)
        self.x_label = QLabel(self.x_splitter)
        self.x_lineEdit = QLineEdit(self.x_splitter)

        self.y_splitter = QSplitter(self)
        self.y_splitter.setOrientation(Qt.Horizontal)
        self.y_label = QLabel(self.y_splitter)
        self.y_lineEdit = QLineEdit(self.y_splitter)

        self.b_splitter = QSplitter(self)
        self.b_splitter.setOrientation(Qt.Horizontal)
        self.b_label = QLabel(self.b_splitter)
        self.b_lineEdit = QLineEdit(self.b_splitter)

        self.r_splitter = QSplitter(self)
        self.r_splitter.setOrientation(Qt.Horizontal)
        self.r_label = QLabel(self.r_splitter)
        self.r_lineEdit = QLineEdit(self.r_splitter)

        # Outputs
        self.state_label = QLabel(self)

        # Empirical S0, S1, S2 box
        self.s_empirical_layoutWidget = QWidget(self)
        self.s_empirical_gridLayout = QGridLayout(self.s_empirical_layoutWidget)

        self.s0_empirical_lineEdit = QLineEdit(self.s_empirical_layoutWidget)
        self.s1_empirical_lineEdit = QLineEdit(self.s_empirical_layoutWidget)
        self.s2_empirical_lineEdit = QLineEdit(self.s_empirical_layoutWidget)

        self.s0_empirical_lineEdit.setReadOnly(True)
        self.s1_empirical_lineEdit.setReadOnly(True)
        self.s2_empirical_lineEdit.setReadOnly(True)

        self.s0_empirical_label = QLabel(self.s_empirical_layoutWidget)
        self.s1_empirical_label = QLabel(self.s_empirical_layoutWidget)
        self.s2_empirical_label = QLabel(self.s_empirical_layoutWidget)

        # S0, S1, S2 box
        self.s_layoutWidget = QWidget(self)
        self.s_gridLayout = QGridLayout(self.s_layoutWidget)

        self.s0_lineEdit = QLineEdit(self.s_layoutWidget)
        self.s1_lineEdit = QLineEdit(self.s_layoutWidget)
        self.s2_lineEdit = QLineEdit(self.s_layoutWidget)

        self.s0_lineEdit.setReadOnly(True)
        self.s1_lineEdit.setReadOnly(True)
        self.s2_lineEdit.setReadOnly(True)

        self.s0_label = QLabel(self.s_layoutWidget)
        self.s1_label = QLabel(self.s_layoutWidget)
        self.s2_label = QLabel(self.s_layoutWidget)

        # Empirical A, Q box
        self.AQ_empirical_layoutWidget = QWidget(self)
        self.AQ_empirical_gridLayout = QGridLayout(self.AQ_empirical_layoutWidget)

        self.A_empirical_lineEdit = QLineEdit(self.AQ_empirical_layoutWidget)
        self.Q_empirical_lineEdit = QLineEdit(self.AQ_empirical_layoutWidget)

        self.A_empirical_lineEdit.setReadOnly(True)
        self.Q_empirical_lineEdit.setReadOnly(True)

        self.A_empirical_label = QLabel(self.AQ_empirical_layoutWidget)
        self.Q_empirical_label = QLabel(self.AQ_empirical_layoutWidget)

        # A, Q box
        self.AQ_layoutWidget = QWidget(self)
        self.AQ_gridLayout = QGridLayout(self.AQ_layoutWidget)

        self.A_lineEdit = QLineEdit(self.AQ_layoutWidget)
        self.Q_lineEdit = QLineEdit(self.AQ_layoutWidget)

        self.A_lineEdit.setReadOnly(True)
        self.Q_lineEdit.setReadOnly(True)

        self.A_label = QLabel(self.AQ_layoutWidget)
        self.Q_label = QLabel(self.AQ_layoutWidget)

        # Progress bar
        self.service_progressBar = QProgressBar(self)
        self.repair_progressBar = QProgressBar(self)

        # Signals
        self.start_button.clicked.connect(self.startButtonClicked)
        self.stop_button.clicked.connect(self.stopButtonClicked)
        self.test_button.clicked.connect(self.testButtonClicked)

        self.x_lineEdit.editingFinished.connect(lambda: self.process_input(self.x_lineEdit.text(), self.X, 'x'))
        self.y_lineEdit.editingFinished.connect(lambda: self.process_input(self.y_lineEdit.text(), self.Y, 'y'))
        self.b_lineEdit.editingFinished.connect(lambda: self.process_input(self.b_lineEdit.text(), self.B, 'b'))
        self.r_lineEdit.editingFinished.connect(lambda: self.process_input(self.r_lineEdit.text(), self.R, 'r'))

        self.set_service_progressbar_value_signal.connect(lambda secs: self.service_progressBar.setValue(secs))
        self.set_repair_progressbar_value_signal.connect(lambda secs: self.repair_progressBar.setValue(secs))

        self.run_button.clicked.connect(self.run_button_clicked)

        self.current_progressbar_thread = None
        self.repair_progressbar_thread = ProgressBarThread(self.set_repair_progressbar_value_signal)
        self.service_progressbar_thread = ProgressBarThread(self.set_service_progressbar_value_signal)

        # progress bar
        # self.queueing_system.break_down_signal.connect(self.run_repair_progressbar)
        # self.queueing_system.service_event.start_break_down_timer_signal.connect(self.run_service_progressbar)
        #
        # self.queueing_system.service_event.stop_break_down_timer_signal.connect(lambda: self._stop_service_progress_bar('stop timer signal'))
        # # self.queueing_system.break_down_signal.connect(lambda: self._stop_service_progress_bar('bread_down signal'))
        #
        # self.queueing_system.update_timer_signal.connect(self._update_output_empirical_characteristics)

        self.queueing_system.update_theoretical_characteristics_signal.connect(self._update_output_theoretical_characteristics)
        self.queueing_system.update_empirical_characteristics_signal.connect(self._update_output_empirical_characteristics)

        self.queueing_system.update_state_signal.connect(lambda state: self.state_label.setText(str(state)))

        self.state = None
        def _assign_state(state):
            self.state = str(state)
        self.queueing_system.update_state_signal.connect(lambda state: _assign_state(state))


        self.intensity_updated_signal.connect(self._intensity_updated)

        # Test
        self.test_my = Test(self.queueing_system, self.output, self)

        # Update characteristics
        self.queueing_system.update_theoretical_characteristics()

        # Show
        self.changeGeometry()
        self.changeTexts()
        self.show()

    def _update_output_theoretical_characteristics(self, s0: float, s1: float, s2: float, A: float, Q: float):
        self.s0_lineEdit.setText(str(round(s0, self.output_precision)))
        self.s1_lineEdit.setText(str(round(s1, self.output_precision)))
        self.s2_lineEdit.setText(str(round(s2, self.output_precision)))
        self.A_lineEdit.setText(str(round(A, self.output_precision)))
        self.Q_lineEdit.setText(str(round(Q, self.output_precision)))

    def _update_output_empirical_characteristics(self, s0: float, s1: float, s2: float, A: float, Q: float):
        self.s0_empirical_lineEdit.setText(str(round(s0, self.output_precision)))
        self.s1_empirical_lineEdit.setText(str(round(s1, self.output_precision)))
        self.s2_empirical_lineEdit.setText(str(round(s2, self.output_precision)))
        self.A_empirical_lineEdit.setText(str(round(A, self.output_precision)))
        self.Q_empirical_lineEdit.setText(str(round(Q, self.output_precision)))

    def _intensity_updated(self):
        self.queueing_system.update_intensities(self.X, self.Y, self.B, self.R)

        self.s0_empirical_lineEdit.setText("")
        self.s1_empirical_lineEdit.setText("")
        self.s2_empirical_lineEdit.setText("")
        self.A_empirical_lineEdit.setText("")
        self.Q_empirical_lineEdit.setText("")

    # TODO: REMOVE WITH BUTTON
    def run_button_clicked(self):
        self.repair_progressbar_thread.set_secs(1)
        self.repair_progressbar_thread.start()

    def _stop_service_progress_bar(self, text=None):
        # print('#'*25 + f'Stop service progressbar bar: {text}')
        self.service_progressbar_thread.stop()
        self.set_service_progressbar_value_signal.emit(0)

    def run_repair_progressbar(self, secs):
        # print('#'*25 + 'Run repair progressbar')
        # self.current_progressbar_thread = self.repair_progressbar_thread
        self.service_progressbar_thread.stop()

        self.repair_progressbar_thread.set_secs(secs)
        self.repair_progressbar_thread.start()

    def run_service_progressbar(self, secs):
        # print('#'*25 + 'Run service progressbar')
        # if self.state != 'idle' or self.state != 'service':
        #     print('STATE', self.state)
        #     return

        if self.repair_progressbar_thread.isRunning():
            # print('*' * 40 + 'TRIED TO RUN SERVICE PROGRESS BAR WHEN REPAIR PROGRESSBAR WAS RUNNING')
            return

        self.service_progressbar_thread.set_secs(secs)
        self.service_progressbar_thread.start()

    def changeGeometry(self):
        # Buttons
        self.start_button.setGeometry(int(10 + 0 * self.buttons_width), 10, self.buttons_width, self.buttons_height)
        self.stop_button.setGeometry(int(10 + 1 * self.buttons_width), 10, self.buttons_width, self.buttons_height)
        self.test_button.setGeometry(int(10 + 2 * self.buttons_width), 10, self.buttons_width, self.buttons_height)
        self.run_button.setGeometry(int(10 + 3 * self.buttons_width), 10, self.buttons_width, self.buttons_height)

        # Output
        self.state_label.setGeometry(QRect(430, 100, 100, 100))
        self.state_label.setText('state')
        self.output.setGeometry(850, 20 + self.buttons_height, self.width - 10, self.height - 20 - self.buttons_height)

        # Outputs
        # Empirical S0, S1, S2 box
        self.s_empirical_layoutWidget.setGeometry(QRect(630, 320, 150, 85))
        self.s_empirical_gridLayout.setContentsMargins(0, 0, 0, 0)

        self.s_empirical_gridLayout.addWidget(self.s0_empirical_label, 0, 0, 1, 1)
        self.s_empirical_gridLayout.addWidget(self.s1_empirical_label, 1, 0, 1, 1)
        self.s_empirical_gridLayout.addWidget(self.s2_empirical_label, 2, 0, 1, 1)

        self.s_empirical_gridLayout.addWidget(self.s0_empirical_lineEdit, 0, 1, 1, 1)
        self.s_empirical_gridLayout.addWidget(self.s1_empirical_lineEdit, 1, 1, 1, 1)
        self.s_empirical_gridLayout.addWidget(self.s2_empirical_lineEdit, 2, 1, 1, 1)

        # S0, S1, S2 box
        self.s_layoutWidget.setGeometry(QRect(400, 320, 150, 85))
        self.s_gridLayout.setContentsMargins(0, 0, 0, 0)

        self.s_gridLayout.addWidget(self.s0_label, 0, 0, 1, 1)
        self.s_gridLayout.addWidget(self.s1_label, 1, 0, 1, 1)
        self.s_gridLayout.addWidget(self.s2_label, 2, 0, 1, 1)

        self.s_gridLayout.addWidget(self.s0_lineEdit, 0, 1, 1, 1)
        self.s_gridLayout.addWidget(self.s1_lineEdit, 1, 1, 1, 1)
        self.s_gridLayout.addWidget(self.s2_lineEdit, 2, 1, 1, 1)

        # Empirical A, Q box
        self.AQ_empirical_layoutWidget.setGeometry(QRect(200, 340, 141, 51))
        self.AQ_empirical_gridLayout.setContentsMargins(0, 0, 0, 0)

        self.AQ_empirical_gridLayout.addWidget(self.A_empirical_label, 0, 0, 1, 1)
        self.AQ_empirical_gridLayout.addWidget(self.Q_empirical_label, 1, 0, 1, 1)
        self.AQ_empirical_gridLayout.addWidget(self.A_empirical_lineEdit, 0, 1, 1, 1)
        self.AQ_empirical_gridLayout.addWidget(self.Q_empirical_lineEdit, 1, 1, 1, 1)

        # A, Q box
        self.AQ_layoutWidget.setGeometry(QRect(20, 340, 141, 51))
        self.AQ_gridLayout.setContentsMargins(0, 0, 0, 0)

        self.AQ_gridLayout.addWidget(self.A_label, 0, 0, 1, 1)
        self.AQ_gridLayout.addWidget(self.Q_label, 1, 0, 1, 1)
        self.AQ_gridLayout.addWidget(self.A_lineEdit, 0, 1, 1, 1)
        self.AQ_gridLayout.addWidget(self.Q_lineEdit, 1, 1, 1, 1)

        # Inputs
        self.x_splitter.setGeometry(QRect(40, 110, 138, 21))
        self.y_splitter.setGeometry(QRect(420, 80, 138, 21))
        self.b_splitter.setGeometry(QRect(200, 190, 138, 21))
        self.r_splitter.setGeometry(QRect(420, 190, 138, 21))

        # Progress bar
        self.service_progressBar.setGeometry(QRect(430, 60, 118, 23))
        self.service_progressBar.setRange(0, 100)

        self.repair_progressBar.setGeometry(QRect(430, 210, 118, 23))
        self.repair_progressBar.setRange(0, 100)

    def changeTexts(self):
        # Inputs
        self.x_label.setText('X:')
        self.x_lineEdit.setText(str(self.X))

        self.y_label.setText('Y:')
        self.y_lineEdit.setText(str(self.Y))

        self.b_label.setText('B:')
        self.b_lineEdit.setText(str(self.B))

        self.r_label.setText('R:')
        self.r_lineEdit.setText(str(self.R))

        # Outputs
        self.s0_empirical_label.setText("s0*")
        self.s1_empirical_label.setText("s1*")
        self.s2_empirical_label.setText("s2*")

        self.s0_label.setText("s0")
        self.s1_label.setText("s1")
        self.s2_label.setText("s2")

        self.A_empirical_label.setText("A*")
        self.Q_empirical_label.setText("Q*")

        self.A_label.setText("A")
        self.Q_label.setText("Q")

    def startButtonClicked(self):
        self.output.setText('Start')
        self.queueing_system.start()

    def stopButtonClicked(self):
        self.queueing_system.stop()
        self.service_progressbar_thread.stop()
        self.repair_progressbar_thread.stop()

        good = self.queueing_system.finished \
            + self.queueing_system.rejected_on_break_down \
            + self.queueing_system.rejected_on_service \
            + self.queueing_system.rejected_on_request \
            == self.queueing_system.requests

        self.output.setText(f'X: {self.queueing_system.X}, Y: {self.queueing_system.Y}, R: {self.queueing_system.R}\n'
                            f'\nRequests: {self.queueing_system.requests}\n'
                            f'Rejected_on_request: {self.queueing_system.rejected_on_request}\n'
                            f'Rejected_on_break_down: {self.queueing_system.rejected_on_break_down}\n'
                            f'Rejected_on_service: {self.queueing_system.rejected_on_service}\n'
                            f'Finished: {self.queueing_system.finished}\n'
                            f'Break downs: {self.queueing_system.break_downs}\n'
                            f'\nGood?: {good} ')

    def testButtonClicked(self):
        self.output.clear()
        self.test_my.start()

    def process_input(self, text: str, prev_number: int, _type: str):
        def inner():
            # number = None

            try:
                number = float(text)
            except ValueError as e:
                QMessageBox(QMessageBox.Critical, "", str(e), parent=self).show()
                return prev_number, False

            max_number = 10**8
            if number < 0 or number > max_number:
                QMessageBox(QMessageBox.Critical, "", f"number should be in [0, {max_number}]", parent=self).show()
                return prev_number, False

            if number == prev_number:
                return prev_number, False

            return number, True

        if self.prev_text == text:
            return
        self.prev_text = text

        if _type == 'x':
            self.X, is_updated = inner()
            self.x_lineEdit.setText(str(self.X))
        elif _type == 'y':
            self.Y, is_updated = inner()
            self.y_lineEdit.setText(str(self.Y))
        elif _type == 'b':
            self.B, is_updated = inner()
            self.b_lineEdit.setText(str(self.B))
        elif _type == 'r':
            self.R, is_updated = inner()
            self.r_lineEdit.setText(str(self.R))
        else:
            raise ValueError("Unexpected _type argument")

        if is_updated:
            self.intensity_updated_signal.emit()


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
