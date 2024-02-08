import time

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel

from app.ui.Icon import Icon

from .home_windowUi import Ui_Dialog
from ...person import Me


class HomeWindow(QWidget, Ui_Dialog):
    load_finish_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.init_ui()
        self.load_finish_signal.emit(True)
        self.btn_report.clicked.connect(self.report)

    def init_ui(self):
        pass

    def report(self):
        time_range = ['2023-01-01 00:00:00', '2024-02-10 00:00:00']
        self.report_thread = ReportThread(Me(), time_range)
        self.report_thread.start()
        QDesktopServices.openUrl(QUrl(f"http://127.0.0.1:21314/"))


class ReportThread(QThread):
    okSignal = pyqtSignal(bool)

    def __init__(self, contact, time_range=None):
        super().__init__()
        self.contact = contact
        self.time_range = time_range

    def run(self):
        from app.web_ui import web
        web.contact = self.contact
        web.time_range = self.time_range
        web.run(port='21314')
        self.okSignal.emit(True)
