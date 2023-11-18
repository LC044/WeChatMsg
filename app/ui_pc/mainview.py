# -*- coding: utf-8 -*-
"""
@File    : mainview.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : 主窗口
"""
import json
from random import randint

from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

from app import config
from app.DataBase import msg, misc
from app.Ui.Icon import Icon
from . import mainwindow
from .chat import ChatWindow
from .contact import ContactWindow
from .tool import ToolWindow
from ..person import MePC

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
        self.resize(QSize(800, 600))
        # self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.action_desc.triggered.connect(self.about)
        self.load_data()
        self.init_ui()
        self.load_num = 0

    def load_data(self):
        with open('./app/data/info.json', 'r', encoding='utf-8') as f:
            dic = json.loads(f.read())
            wxid = dic.get('wxid')
            if wxid:
                me = MePC()
                self.set_my_info(wxid)

    def init_ui(self):
        # self.movie = QMovie("./app/data/loading.gif")
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, self.width(), self.height())
        # self.label.setMovie(self.movie)
        # self.movie.start()
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        tool_item = QListWidgetItem(Icon.MyInfo_Icon, '工具', self.listWidget)
        chat_item = QListWidgetItem(Icon.Chat_Icon, '聊天', self.listWidget)
        contact_item = QListWidgetItem(Icon.Contact_Icon, '好友', self.listWidget)
        myinfo_item = QListWidgetItem(Icon.MyInfo_Icon, '我的', self.listWidget)

        tool_window = ToolWindow()
        tool_window.get_info_signal.connect(self.set_my_info)
        tool_window.load_finish_signal.connect(self.loading)
        self.stackedWidget.addWidget(tool_window)
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)
        chat_window = ChatWindow()
        self.stackedWidget.addWidget(chat_window)
        contact_window = ContactWindow()
        self.stackedWidget.addWidget(contact_window)
        label = QLabel('我是页面')
        label.setAlignment(Qt.AlignCenter)
        # 设置label的背景颜色(这里随机)
        # 这里加了一个margin边距(方便区分QStackedWidget和QLabel的颜色)
        label.setStyleSheet('background: rgb(%d, %d, %d);margin: 50px;' % (
            randint(0, 255), randint(0, 255), randint(0, 255)))
        self.stackedWidget.addWidget(label)
        tool_window.load_finish_signal.connect(self.loading)
        contact_window.load_finish_signal.connect(self.loading)
        chat_window.load_finish_signal.connect(self.loading)
        # self.load_window_thread = LoadWindowThread(self.stackedWidget)
        # self.load_window_thread.okSignal.connect(self.stop_loading)
        # self.load_window_thread.start()

    def setCurrentIndex(self, row):
        self.stackedWidget.setCurrentIndex(row)
        if row == 2:
            self.stackedWidget.currentWidget().show_contacts()

    def setWindow(self, window):
        try:
            window.load_finish_signal.connect(self.loading)
        except:
            pass
        self.stackedWidget.addWidget(window)

    def set_my_info(self, wxid):
        self.avatar = QPixmap()
        img_bytes = misc.get_avatar_buffer(wxid)
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')
        self.avatar.scaled(60, 60)
        me = MePC()
        me.set_avatar(img_bytes)
        dic = {
            'wxid': wxid
        }
        with open('./app/data/info.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(dic))
        self.myavatar.setScaledContents(True)
        self.myavatar.setPixmap(self.avatar)

    def stop_loading(self, a0):
        self.label.setVisible(False)

    def loading(self, a0):
        self.load_num += 1
        # print('加载一个了')
        if self.load_num == 2:
            # print('ok了')
            self.label.setVisible(False)

    def about(self):
        """
        关于
        """
        QMessageBox.about(self, "关于",
                          f"版本：{config.version}\n"
                          f"QQ交流群:{config.contact}\n"
                          "地址：https://github.com/LC044/WeChatMsg\n"
                          f"新特性:\n{''.join(['*' + i for i in config.description])}"
                          )

    def close(self) -> bool:
        del self.listWidget
        del self.stackedWidget
        msg.close()
        self.contact_window.close()


class LoadWindowThread(QThread):
    windowSignal = pyqtSignal(QWidget)
    okSignal = pyqtSignal(bool)

    def __init__(self, stackedWidget):
        super().__init__()
        self.stackedWidget = stackedWidget

    def run(self):
        chat_window = ChatWindow()
        self.stackedWidget.addWidget(chat_window)
        contact_window = ContactWindow()
        self.stackedWidget.addWidget(contact_window)
        label = QLabel('我是页面')
        label.setAlignment(Qt.AlignCenter)
        # 设置label的背景颜色(这里随机)
        # 这里加了一个margin边距(方便区分QStackedWidget和QLabel的颜色)
        label.setStyleSheet('background: rgb(%d, %d, %d);margin: 50px;' % (
            randint(0, 255), randint(0, 255), randint(0, 255)))
        self.stackedWidget.addWidget(label)
        self.okSignal.emit(True)
