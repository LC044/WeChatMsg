from PyQt5.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import QWidget, QMessageBox

from app.ui.Icon import Icon

from .home_windowUi import Ui_Dialog
from ...person import Me

Stylesheet = """
QPushButton{
    border-radius: 5px;
    padding: 8px;
    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
}
QPushButton:hover { 
    background-color: lightgray;
}
"""


class HomeWindow(QWidget, Ui_Dialog):
    load_finish_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.init_ui()
        self.setStyleSheet(Stylesheet)
        self.load_finish_signal.emit(True)
        self.btn_report.clicked.connect(self.report)
        self.btn_save.clicked.connect(self.save_info)

    def init_ui(self):
        self.label_wxid.setText(Me().wxid)
        self.lineEdit_name.setText(Me().name)
        self.lineEdit_phone.setText(Me().mobile)

    def save_info(self):
        if self.lineEdit_name.text():
            Me().name = self.lineEdit_name.text()
        else:
            QMessageBox.critical(self, "错误",
                                 "昵称不能为空")
            return
        if self.lineEdit_phone.text():
            Me().mobile = self.lineEdit_phone.text()
        else:
            QMessageBox.critical(self, "错误",
                                 "手机号不能为空")
            return
        Me().save_info()
        QMessageBox.information(self, "修改成功",
                                "个人信息修改成功")

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
