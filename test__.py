# from queueing_system import QueueingSystem
import time
# import scipy
# from PyQt5.QtCore import QTimer, QThread, pyqtSignal
# from PyQt5.QtWidgets import *
# import sys
#
#
# X = 1000
# Y = 10
# R = 1 / 3
#
#
# class Test(QThread):
#     def __init__(self):
#         super(Test, self).__init__()
#
#     def run(self) -> None:
#         queueing_system = QueueingSystem(X, Y, R)
#         queueing_system.start()
#         time.sleep(1)
#         queueing_system.stop()
#         print(
#             f'Requests: {queueing_system.requests}\n'
#             f'Rejected: {queueing_system.rejected}\n'
#             f'Finished: {queueing_system.finished}\n'
#             f'Break downs: {queueing_system.break_downs}\n'
#         )

t = time.time()
time.sleep(1)

print(t, ' | ', time.time() - t)