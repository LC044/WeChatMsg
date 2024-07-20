import json
import os.path
from urllib.parse import urljoin

import requests
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QWidget, QMessageBox

from app.components.QCursorGif import QCursorGif
from app.config import SERVER_API_URL
from app.decrypt.get_bias_addr import BiasAddr
from .getBiasAddrUi import Ui_Form

# 样式表常量
STYLESHEET = """
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
    """
    获取和上传微信偏移地址的主控件类。
    """
    biasAddrSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(GetBiasAddrControl, self).__init__(parent)
        self.thread = None
        self.setStyleSheet(STYLESHEET)
        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        """
        初始化UI组件并连接信号。
        """
        self.initCursor([':/icons/icons/Cursors/%d.png' % i for i in range(8)], self)
        self.setCursorTimeout(100)
        self.btn_get_bias_addr.clicked.connect(self.get_bias_addr)
        self.commandLinkButton.clicked.connect(self.show_info)
        self.checkBox_send_error_log.clicked.connect(self.set_error_log)

    def set_error_log(self):
        """
        根据复选框状态更新错误日志标签。
        """
        if self.checkBox_send_error_log.isChecked():
            self.label_error_log.setText('开')
        else:
            self.label_error_log.setText('关')

    def show_info(self):
        """
        显示关于数据收集的信息框。
        """
        QMessageBox.information(self, "收集版本信息",
                                "为了适配更多版本，需要收集微信的版本信息，该操作不会上传包括手机号、微信号、昵称等在内的任何信息\n示例数据：\n\"3.9.9.27\": [68065304, 0, 68065112, 0, 68066576]"
                                )

    def upload(self, version_data):
        """
        上传版本数据到服务器。

        参数:
            version_data (dict): 包含偏移地址信息的字典。
        """
        url = urljoin(SERVER_API_URL, 'wxBiasAddr')
        try:
            response = requests.post(url, json={'bias_dict': version_data})
            response.raise_for_status()
            print('版本信息上传成功')
        except requests.RequestException as e:
            print(f'版本信息上传失败: {e}')

    def get_bias_addr(self):
        """
        根据用户输入获取偏移地址，并启动后台线程。
        """
        # 从用户输入框获取微信账号、手机号和昵称
        account = self.lineEdit_wx_alias.text()
        mobile = self.lineEdit_tel.text()
        name = self.lineEdit_wx_name.text()
    
        # 检查是否所有输入框都已填写，若有未填写的则弹出错误提示框
        if not all([account, mobile, name]):
            QMessageBox.critical(self, "错误", "请把所有信息填写完整")
            return
    
        # 初始化密钥和数据库路径，密钥目前未使用因此设为None，数据库路径设为"test"
        key = None
        db_path = "test"
    
        # 启动忙碌指示（例如光标变成加载状态）
        self.startBusy()
    
        # 创建一个后台线程实例，并传递用户输入的数据
        self.thread = MyThread(account, mobile, name, key, db_path)
    
        # 连接线程的信号到主窗口的处理方法，以便线程完成后更新UI
        self.thread.signal.connect(self.set_bias_addr)
    
        # 启动线程
        self.thread.start()

    def set_bias_addr(self, data):
        """
        设置偏移地址并选择性上传。

        参数:
            data (dict): 包含偏移地址信息的字典。
        """
        if self.checkBox_send_error_log.isChecked():
            self.upload(data)
        self.stopBusy()
        self.biasAddrSignal.emit(data)

class MyThread(QThread):
    """
    获取偏移地址的后台线程类。
    """
    signal = pyqtSignal(dict)

    def __init__(self, account, mobile, name, key, db_path):
        super(MyThread, self).__init__()
        self.account = account
        self.mobile = mobile
        self.name = name
        self.key = key
        self.db_path = db_path

    def run(self):
        """
        运行线程以获取偏移地址。
        """
        bias_addr = BiasAddr(self.account, self.mobile, self.name, self.key, self.db_path)
        data = bias_addr.run(logging_path=True)
        self.signal.emit(data)
