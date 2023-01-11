# -*- coding: utf-8 -*-
"""
@File    : CreateGroup.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/20 22:55
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
from .create_groupUi import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ....DB import data
import time


class CreateGroupView(QWidget, Ui_Frame):
    backSignal = pyqtSignal(str)
    gidSignal = pyqtSignal(int)
    def __init__(self, username, parent=None):
        super(CreateGroupView, self).__init__(parent)
        self.setupUi(self)
        self.tips.setVisible(False)
        self.setWindowTitle('创建群聊')
        self.setWindowIcon(QIcon('./data/icon.png'))
        self.username = username
        # self.register_2.clicked.connect(self.login_)
        self.back.clicked.connect(self.btnEnterClicked)
        self.back.clicked.connect(self.btnEnterClicked)
        self.btn_set_gAvatar.clicked.connect(self.up_avatar)
        self.btn_create.clicked.connect(self.create_group)
        self.avatar = None

    def up_avatar(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open file', r'..', "Image files (*.png;*.jpg)")
        if path:
            try:
                pixmap = QPixmap(path).scaled(80, 80)  # 按指定路径找到图片
                self.avatar_img.setPixmap(pixmap)  # 在label上显示图片
                self.avatar = path
            except:
                self.error.setText('头像不存在')

    def create_group(self):
        # self.close()
        if not self.avatar:
            self.error.setText('请上传头像')
            return False
        name = self.group_name.text()
        intro = self.group_intro.toPlainText()
        # print(intro,self.username)
        flag = data.create_group(
            g_name=name,
            g_admin=self.username,
            g_intro=intro
        )
        # print('123456')
        # print(flag)
        if not flag:
            self.error.setText('创建失败')
            # print('yonghu已经存在')
        else:
            self.error.setText('创建成功')
            self.error.setStyleSheet("color:black")
            avatar = data.get_avator(str(flag))
            # new_path = '/'.join(avatar.split('/')[:-1])+'/'
            # print(avatar)
            if '.' in avatar[-10:]:
                avatar = '.'.join(avatar.split('.')[:-1])
            # print(avatar)
            data.mycopyfile(self.avatar, avatar + '.png')
            self.tips.setVisible(True)
            self.thread = MyThread()  # 创建一个线程
            self.thread.sec_changed_signal.connect(self._update)  # 线程发过来的信号挂接到槽：update
            self.thread.start()
        self.gidSignal.emit(int(flag))

    def _update(self, sec):
        # self.time.setProperty("value", float(sec))
        # self.time.setDigitCount(sec)
        # self.time.s
        if sec == 0:
            self.btnEnterClicked()

    def btnEnterClicked(self):
        print("退出创建群聊界面")
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
