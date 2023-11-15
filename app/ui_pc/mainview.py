# -*- coding: utf-8 -*-
"""
@File    : mainview.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : 主窗口
"""
from random import randint

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app import config
from app.Ui.Icon import Icon
from . import mainwindow
from .contact import ContactWindow
from .tool import ToolWindow

# 美化样式表
Stylesheet = """
QPushButton {
    background-color: rgb(240,240,240);
    border:none;
}
QPushButton:hover{
    background-color: rgb(209,209,209);
}
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 120px;
    max-width: 120px;
    color: black;
    background: white;
    border:none;
}
QListWidget::item{
    height:60;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    background: rgb(204, 204, 204);
    border-left: 4px solid rgb(9, 187, 7);
    color: black;
    font-weight: bold;
}
/*鼠标悬停颜色*/
HistoryPanel::item:hover {
    background: rgb(52, 52, 52);
}
"""


class MainWinController(QMainWindow, mainwindow.Ui_MainWindow):
    exitSignal = pyqtSignal()

    # username = ''
    def __init__(self, username, parent=None):
        super(MainWinController, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(Icon.MainWindow_Icon)
        self.setStyleSheet(Stylesheet)
        self.listWidget.clear()
        # self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.action_desc.triggered.connect(self.about)
        self.init_ui()

    def init_ui(self):
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        chat_item = QListWidgetItem(Icon.Chat_Icon, '聊天', self.listWidget)
        contact_item = QListWidgetItem(Icon.Contact_Icon, '好友', self.listWidget)
        myinfo_item = QListWidgetItem(Icon.MyInfo_Icon, '我的', self.listWidget)
        tool_item = QListWidgetItem(Icon.MyInfo_Icon, '工具', self.listWidget)

        tool_window = ToolWindow()
        label = QLabel('我是页面', self)
        label.setAlignment(Qt.AlignCenter)
        # 设置label的背景颜色(这里随机)
        # 这里加了一个margin边距(方便区分QStackedWidget和QLabel的颜色)
        label.setStyleSheet('background: rgb(%d, %d, %d);margin: 50px;' % (
            randint(0, 255), randint(0, 255), randint(0, 255)))
        self.stackedWidget.addWidget(label)
        self.contact_window = ContactWindow()
        self.stackedWidget.addWidget(self.contact_window)
        label = QLabel('我是页面', self)
        label.setAlignment(Qt.AlignCenter)
        # 设置label的背景颜色(这里随机)
        # 这里加了一个margin边距(方便区分QStackedWidget和QLabel的颜色)
        label.setStyleSheet('background: rgb(%d, %d, %d);margin: 50px;' % (
            randint(0, 255), randint(0, 255), randint(0, 255)))
        self.stackedWidget.addWidget(label)
        self.stackedWidget.addWidget(tool_window)
        self.listWidget.setCurrentRow(3)
        self.stackedWidget.setCurrentIndex(3)

    def setCurrentIndex(self, row):
        if row == 1:
            self.contact_window.show_contacts()
        self.stackedWidget.setCurrentIndex(row)

    def about(self):
        """
        关于
        """
        QMessageBox.about(self, "关于",
                          f"版本：{config.version}\n"
                          f"QQ交流群:{config.contact}\n"
                          "地址：https://github.com/LC044/WeChatMsg"
                          )
