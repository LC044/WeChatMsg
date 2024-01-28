import json
import os.path

import requests
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget, QMessageBox

from app.components.QCursorGif import QCursorGif
from app.decrypt.get_bias_addr import BiasAddr
from .getBiasAddrUi import Ui_Form

Stylesheet = """
QPushButton{
    background-color: rgb(250,252,253);
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
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
    border:none;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 400px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
    color: black;
    border:none;
}
QListWidget::item{
    min-width: 80px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    border-left:none;
    color: black;
    font-weight: bold;
}
QCheckBox::indicator {
    background: rgb(251, 251, 251);
    Width:60px;
    Height:60px;
    border-radius: 10px;
}
QCheckBox::indicator:unchecked{
    Width:60px;
    Height:60px;
    image: url(:/icons/icons/按钮_关闭.svg);
}
QCheckBox::indicator:checked{
    Width:60px;
    Height:60px;
    image: url(:/icons/icons/按钮_开启.svg);
}

"""


class GetBiasAddrControl(QWidget, Ui_Form, QCursorGif):
    biasAddrSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(GetBiasAddrControl, self).__init__(parent)
        self.thread = None
        self.setStyleSheet(Stylesheet)
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.initCursor([':/icons/icons/Cursors/%d.png' %
                         i for i in range(8)], self)
        self.setCursorTimeout(100)
        self.btn_get_bias_addr.clicked.connect(self.get_bias_addr)
        self.commandLinkButton.clicked.connect(self.show_info)
        self.checkBox_send_error_log.clicked.connect(self.set_error_log)

    def set_error_log(self):
        if self.checkBox_send_error_log.isChecked():
            self.label_error_log.setText('开')
        else:
            self.label_error_log.setText('关')

    def show_info(self):
        QMessageBox.information(self, "收集版本信息",
                                "为了适配更多版本，需要收集微信的版本信息，该操作不会上传包括手机号、微信号、昵称等在内的任何信息\n示例数据：\n\"3.9.9.27\": [68065304, 0, 68065112, 0, 68066576]"
                                )

    def upload(self, version_data):
        url = "http://api.lc044.love/wxBiasAddr"
        try:
            requests.post(url, json=version_data)
            print('版本信息上传成功')
        except:
            pass

    def get_bias_addr(self):

        account = self.lineEdit_wx_alias.text()
        mobile = self.lineEdit_tel.text()
        name = self.lineEdit_wx_name.text()
        if not all([account, mobile, name]):
            QMessageBox.critical(self, "错误",
                                 "请把所有信息填写完整")
            return
        key = None
        db_path = "test"
        self.startBusy()
        self.thread = MyThread(account, mobile, name, key, db_path)
        self.thread.signal.connect(self.set_bias_addr)
        self.thread.start()

    def set_bias_addr(self, data):
        if self.checkBox_send_error_log.isChecked():
            self.upload(data)
        self.stopBusy()
        self.biasAddrSignal.emit(data)


class MyThread(QThread):
    signal = pyqtSignal(dict)

    def __init__(self, account, mobile, name, key, db_path):
        super(MyThread, self).__init__()
        self.account = account
        self.mobile = mobile
        self.name = name
        self.key = key
        self.db_path = db_path

    def run(self):
        bias_addr = BiasAddr(self.account, self.mobile, self.name, self.key, self.db_path)
        data = bias_addr.run(logging_path=True)
        self.signal.emit(data)
