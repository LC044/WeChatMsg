# -*- coding: utf-8 -*-
"""
@File    : addContact.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/17 14:26
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
from .addContactUi import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ....DB import data
import time


class addControl(QWidget, Ui_Dialog):
    backSignal = pyqtSignal(str)
    contactSignal = pyqtSignal(tuple)
    def __init__(self, username,parent=None):
        super(addControl, self).__init__(parent)
        self.setupUi(self)
        self.tips.setVisible(False)
        self.time.setVisible(False)
        self.setWindowTitle('添加联系人')
        self.setWindowIcon(QIcon('./data/icon.png'))
        self.Username = username
        # self.register_2.clicked.connect(self.login_)
        self.back.clicked.connect(self.btnEnterClicked)
        self.search.clicked.connect(self.search_user)
        self.add_contact.clicked.connect(self.add_contact_)
        self.avatar = None

    def search_user(self):
        username = self.username.text()
        nickname = self.nickname.text()
        print(username,nickname)
        if data.searchUser(username):
            imgpath = data.get_avator(username)
            print(imgpath)
            pixmap = QPixmap(imgpath).scaled(60, 60)  # 按指定路径找到图片
            self.avatar_img.setPixmap(pixmap)  # 在label上显示图片
        else:
            self.error.setText('用户不存在')

    def add_contact_(self):
        username = self.username.text()
        nickname = self.nickname.text()
        flag = data.add_contact(self.Username,username, nickname)
        if flag:
            self.error.setText('添加成功')
            self.contactSignal.emit(flag)
            self.thread = MyThread()  # 创建一个线程
            self.thread.sec_changed_signal.connect(self._update)  # 线程发过来的信号挂接到槽：update
            self.thread.start()
        else:
            QMessageBox.critical(self, "错误", "用户不存在")


    def _update(self, sec):
        self.time.setProperty("value", float(sec))
        # self.time.setDigitCount(sec)
        # self.time.s
        if sec == 0:
            self.btnEnterClicked()

    def btnEnterClicked(self):
        print("退出添加联系人界面")
        # 中间可以添加处理逻辑
        self.backSignal.emit("back")
        self.close()

    def btnExitClicked(self):
        print("Exit clicked")
        self.close()


class MyThread(QThread):
    sec_changed_signal = pyqtSignal(int)  # 信号类型：int

    def __init__(self, sec=1000, parent=None):
        super().__init__(parent)
        self.sec = 2  # 默认1000秒

    def run(self):
        for i in range(self.sec, -1, -1):
            self.sec_changed_signal.emit(i)  # 发射信号
            time.sleep(1)
