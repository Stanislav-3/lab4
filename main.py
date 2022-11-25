from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QThread
from queueing_system import QueueingSystem
from my_threads import ProgressBarThread
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
    repair_progressbar_value_signal = pyqtSignal(int)
    service_progressbar_value_signal = pyqtSignal(int)

    intensity_updated = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Queueing system
        self.X = 12
        self.Y = 123
        self.R = 12
        self.queueing_system = QueueingSystem(self.X, self.Y, self.R, random_state=42)

        # QMainWindow
        self.top = 15000
        self.left = 150
        self.width = 1200
        self.height = 500

        self.setWindowTitle("Queueing system")
        self.setGeometry(self.top, self.left, self.width, self.height)

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

        self.r_splitter = QSplitter(self)
        self.r_splitter.setOrientation(Qt.Horizontal)
        self.r_label = QLabel(self.r_splitter)
        self.r_lineEdit = QLineEdit(self.r_splitter)

        # Outputs
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
        self.r_lineEdit.editingFinished.connect(lambda: self.process_input(self.r_lineEdit.text(), self.R, 'r'))

        self.repair_progressbar_value_signal.connect(lambda value: self.repair_progressBar.setValue(value))
        self.service_progressbar_value_signal.connect(lambda value: self.service_progressBar.setValue(value))
        self.run_button.clicked.connect(self.run_button_clicked)

        self.repair_progressbar_thread = ProgressBarThread(self.repair_progressbar_value_signal)
        self.service_progressbar_thread = ProgressBarThread(self.service_progressbar_value_signal)

        self.queueing_system.break_down_signal.connect(self.run_repair_progressbar)
        self.queueing_system.service_event.start_timer_signal.connect(self.run_service_progressbar)

        self.intensity_updated.connect(self._intensity_updated)

        # Test
        self.test_my = Test(self.queueing_system, self.output, self)

        # Show
        self.changeGeometry()
        self.changeTexts()
        self.show()

    # TODO: UPDATE CHARACTERISTICS & CLEAR PREVIOUS
    def _intensity_updated(self):
        self.queueing_system.update_intensities(self.X, self.Y, self.R)

    def run_button_clicked(self):
        self.repair_progressbar_thread.set_secs(1)
        self.repair_progressbar_thread.start()

    def run_repair_progressbar(self, secs):
        self.repair_progressbar_thread.set_secs(secs)
        self.repair_progressbar_thread.start()

        self.service_progressbar_thread.stop()

    def run_service_progressbar(self, secs):
        self.service_progressbar_thread.set_secs(secs)

        self.service_progressbar_thread.start()

    def changeGeometry(self):
        # Buttons
        self.start_button.setGeometry(int(10 + 0 * self.buttons_width), 10, self.buttons_width, self.buttons_height)
        self.stop_button.setGeometry(int(10 + 1 * self.buttons_width), 10, self.buttons_width, self.buttons_height)
        self.test_button.setGeometry(int(10 + 2 * self.buttons_width), 10, self.buttons_width, self.buttons_height)
        self.run_button.setGeometry(int(10 + 3 * self.buttons_width), 10, self.buttons_width, self.buttons_height)

        # Output
        self.output.setGeometry(10, 20 + self.buttons_height, self.width - 10, self.height - 20 - self.buttons_height)

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

    def process_input(self, text: str, prev_int: int, _type: str):
        def inner():
            number = None

            try:
                number = float(text)
            except ValueError as e:
                QMessageBox(QMessageBox.Critical, "", str(e), parent=self).show()
                return prev_int

            max_number = 10**5
            if number < 0 or number > max_number:
                QMessageBox(QMessageBox.Critical, "", f"number should be in [0, {max_number}]", parent=self).show()
                return prev_int

            return number

        if self.prev_text == text:
            return
        self.prev_text = text

        if _type == 'x':
            self.X = inner()
            self.x_lineEdit.setText(str(self.X))
        elif _type == 'y':
            self.Y = inner()
            self.y_lineEdit.setText(str(self.Y))
        elif _type == 'r':
            self.R = inner()
            self.r_lineEdit.setText(str(self.R))

        self.intensity_updated.emit()


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
