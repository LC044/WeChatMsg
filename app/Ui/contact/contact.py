# -*- coding: utf-8 -*-
"""
@File    : contact.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
from typing import Dict

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import app.components.Button_Contact as MyLabel
from app import person
from app.DataBase import data
from app.Ui.contact.contactInfo import ContactInfo
from app.Ui.contact.contactUi import Ui_Dialog

EMOTION = 1
ANALYSIS = 2


class StackedWidget():
    def __init__(self):
        pass


class ContactController(QWidget, Ui_Dialog):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''

    def __init__(self, Me: person.Me, parent=None):
        super(ContactController, self).__init__(parent)
        self.chatroomFlag = None
        self.ta_avatar = None
        self.setupUi(self)
        self.Me = Me
        self.contacts: Dict[str, MyLabel.ContactUi] = {}
        self.contactInfo: Dict[str, ContactInfo] = {}
        self.show_flag = False
        self.last_talkerId = None
        self.now_talkerId = None
        # self.showContact()
        self.show_thread = ShowContactThread()
        self.show_thread.showSingal.connect(self.showContact)
        self.show_thread.heightSingal.connect(self.setScreenAreaHeight)
        self.show_thread.start()

    def showContact(self, data_):
        """
        data:Tuple[rconversation,index:int]
        显示联系人
        :return:
        """
        rconversation, i = data_
        username = rconversation[1]
        # print(username)
        pushButton_2 = MyLabel.ContactUi(self.scrollAreaWidgetContents, i, rconversation)
        pushButton_2.setGeometry(QtCore.QRect(0, 80 * i, 300, 80))
        pushButton_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        pushButton_2.clicked.connect(pushButton_2.show_msg)
        pushButton_2.usernameSingal.connect(self.Contact)
        self.contacts[username] = pushButton_2
        self.contactInfo[username] = ContactInfo(username, self.Me)
        self.stackedWidget.addWidget(self.contactInfo[username])

    def setScreenAreaHeight(self, height: int):
        self.scrollAreaWidgetContents.setGeometry(
            QtCore.QRect(0, 0, 300, height))

    def Contact(self, talkerId):
        """
        聊天界面 点击联系人头像时候显示聊天数据
        :param talkerId:
        :return:
        """
        self.now_talkerId = talkerId
        # 把当前按钮设置为灰色
        if self.last_talkerId and self.last_talkerId != talkerId:
            print('对方账号：', self.last_talkerId)
            self.contacts[self.last_talkerId].setStyleSheet(
                "QPushButton {background-color: rgb(220,220,220);}"
                "QPushButton:hover{background-color: rgb(208,208,208);}\n"
            )
        self.last_talkerId = talkerId
        self.contacts[talkerId].setStyleSheet(
            "QPushButton {background-color: rgb(198,198,198);}"
            "QPushButton:hover{background-color: rgb(209,209,209);}\n"
        )
        self.stackedWidget.setCurrentWidget(self.contactInfo[talkerId])

        if '@chatroom' in talkerId:
            self.chatroomFlag = True
        else:
            self.chatroomFlag = False


class ShowContactThread(QThread):
    showSingal = pyqtSignal(tuple)
    heightSingal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self) -> None:
        rconversations = data.get_rconversation()
        max_height = max(len(rconversations) * 80, 680)
        # 设置滚动区域的高度
        self.heightSingal.emit(max_height)
        for i in range(len(rconversations)):
            self.showSingal.emit((rconversations[i], i))
