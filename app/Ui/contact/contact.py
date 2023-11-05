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

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import app.Ui.MyComponents.Button_Contact as MyLabel
from .contactInfo import ContactInfo
from .contactUi import *
from ... import person
from ...DataBase import data

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
        self.showContact()

    def showContact(self):
        """
        显示联系人
        :return:
        """
        print('show')
        if self.show_flag:
            return
        self.show_flag = True
        rconversations = data.get_rconversation()
        max_hight = max(len(rconversations) * 80, 680)
        # 设置滚动区域的高度
        self.scrollAreaWidgetContents.setGeometry(
            QtCore.QRect(0, 0, 300, max_hight))

        for i in range(len(rconversations)):
            rconversation = rconversations[i]
            username = rconversation[1]
            # 创建联系人按钮对象
            # 将实例化对象添加到self.contacts储存起来
            # pushButton_2 = Contact(self.scrollAreaWidgetContents, i, rconversation)
            pushButton_2 = MyLabel.ContactUi(self.scrollAreaWidgetContents, i, rconversation)
            pushButton_2.setGeometry(QtCore.QRect(0, 80 * i, 300, 80))
            pushButton_2.setLayoutDirection(QtCore.Qt.LeftToRight)
            pushButton_2.clicked.connect(pushButton_2.show_msg)
            pushButton_2.usernameSingal.connect(self.Contact)
            self.contacts[username] = pushButton_2
            self.contactInfo[username] = ContactInfo(username, self.Me)
            self.stackedWidget.addWidget(self.contactInfo[username])

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
