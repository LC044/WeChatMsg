# -*- coding: utf-8 -*-
"""
@File    : mainview.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : 主窗口
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from app import person
from app.DataBase import *
from app.Ui import mainwindow
from app.Ui.Icon import Icon
from app.Ui.chat import chat
from app.Ui.contact import contact


class MainWinController(QMainWindow, mainwindow.Ui_MainWindow):
    exitSignal = pyqtSignal()

    # username = ''
    def __init__(self, username, parent=None):
        super(MainWinController, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(Icon.MainWindow_Icon)
        self.Me = person.Me(data.get_myinfo())
        self.setAttribute(Qt.WA_AttributeCount)

        self.chatView = chat.ChatController(self.Me, parent=None)
        self.lay = QHBoxLayout()
        self.page_chat.setLayout(self.lay)
        self.lay.addWidget(self.chatView)

        self.contactView = contact.ContactController(self.Me, parent=None)
        self.lay0 = QHBoxLayout()
        self.page_contact.setLayout(self.lay0)
        self.lay0.addWidget(self.contactView)

        self.btn_chat.clicked.connect(self.chat_view)  # 聊天按钮
        self.btn_contact.clicked.connect(self.contact_view)
        # self.btn_myinfo.clicked.connect(self.myInfo)
        self.btn_about.clicked.connect(self.about)
        self.now_btn = self.btn_chat
        self.btn_about.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn_about.customContextMenuRequested.connect(self.create_rightmenu)  # 连接到菜单显示函数
        self.last_btn = None
        self.lastView = None
        self.show_avatar()
        self.init_ui()
        # 创建右键菜单函数

    def init_ui(self):
        self.menubar.setStyleSheet("background-color: rgb(240, 240, 240);")

    def create_rightmenu(self):
        # 菜单对象
        self.groupBox_menu = QMenu(self)

        self.actionA = QAction(QIcon('image/保存.png'), u'保存数据',
                               self)  # self.actionA = self.contextMenu.addAction(QIcon("images/0.png"),u'|  动作A')
        self.actionA.setShortcut('Ctrl+S')  # 设置快捷键
        self.groupBox_menu.addAction(self.actionA)  # 把动作A选项添加到菜单

        self.actionB = QAction(QIcon('image/删除.png'), u'删除数据', self)
        self.groupBox_menu.addAction(self.actionB)

        # self.actionA.triggered.connect(self.button)  # 将动作A触发时连接到槽函数 button
        # self.actionB.triggered.connect(self.button_2)

        self.groupBox_menu.popup(QCursor.pos())  # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，

    def show_avatar(self):
        avatar = self.Me.avatar
        pixmap = QPixmap(avatar).scaled(60, 60)  # 按指定路径找到图片
        self.myavatar.setPixmap(pixmap)  # 在label上显示图片

    def chat_view(self):
        """
        聊天窗口
        """
        self.now_btn = self.btn_chat
        self.now_btn.setStyleSheet(
            "QPushButton {background-color: rgb(198,198,198);}")
        if self.last_btn and self.last_btn != self.now_btn:
            self.last_btn.setStyleSheet("QPushButton {background-color: rgb(240,240,240);}"
                                        "QPushButton:hover{background-color: rgb(209,209,209);}\n")
        self.last_btn = self.btn_chat
        self.stackedWidget.setCurrentIndex(0)
        self.chatView.showChat()

    def contact_view(self):
        """
        联系人窗口
        """
        self.now_btn = self.btn_contact
        self.now_btn.setStyleSheet(
            "QPushButton {background-color: rgb(198,198,198);}")
        if self.last_btn and self.last_btn != self.now_btn:
            self.last_btn.setStyleSheet("QPushButton {background-color: rgb(240,240,240);}"
                                        "QPushButton:hover{background-color: rgb(209,209,209);}\n")
        self.last_btn = self.btn_contact
        self.stackedWidget.setCurrentIndex(1)

    def myInfo(self):
        """
        显示我的个人信息
        """
        self.now_btn = self.btn_myinfo
        self.now_btn.setStyleSheet(
            "QPushButton {background-color: rgb(198,198,198);}")
        if self.last_btn and self.last_btn != self.now_btn:
            self.last_btn.setStyleSheet("QPushButton {background-color: rgb(240,240,240);}"
                                        "QPushButton:hover{background-color: rgb(209,209,209);}\n")
        self.last_btn = self.now_btn

    def about(self):
        """
        关于
        """
        QMessageBox.about(self, "关于",
                          "关于作者\n姓名：周帅康\n邮箱：lc863854@mail.nwpu.edu.cn"
                          )
