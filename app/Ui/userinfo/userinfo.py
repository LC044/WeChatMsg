# -*- coding: utf-8 -*-
"""
@File    : contact.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .userinfoUi import *
from ...DataBase import data


class MyinfoController(QWidget, Ui_Dialog):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''

    def __init__(self, Me, parent=None):
        super(MyinfoController, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('WeChat')
        self.setWindowIcon(QIcon('./app/data/icon.png'))
        self.Me = Me
        self.initui()

    def initui(self):
        self.myinfo = data.get_myInfo()
        avatar = self.Me.my_avatar
        pixmap = QPixmap(avatar).scaled(80, 80)  # 按指定路径找到图片
        self.label_avatar.setPixmap(pixmap)  # 在label上显示图片
        self.label_name.setText(self.myinfo['name'])
        self.label_wxid.setText('微信号：' + self.myinfo['username'])
        city = f"地区：{self.myinfo['province']}{self.myinfo['city']}"
        self.label_city.setText(city)
