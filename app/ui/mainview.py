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
import os.path

from PyQt5.QtCore import pyqtSignal, QUrl, Qt, QThread, QSize
from PyQt5.QtGui import QPixmap, QFont, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QLabel, QListWidgetItem, QMessageBox

from app import config
from app.DataBase import msg_db, misc_db, micro_msg_db, hard_link_db
from app.ui.Icon import Icon
from . import mainwindow
from .chat import ChatWindow
from .contact import ContactWindow
from .tool.tool_window import ToolWindow
from ..DataBase.output_pc import Output
from ..person import MePC

# 美化样式表
Stylesheet = """

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
    exitSignal = pyqtSignal(bool)
    okSignal = pyqtSignal(bool)

    # username = ''
    def __init__(self, username, parent=None):
        super(MainWinController, self).__init__(parent)
        self.outputThread0 = None
        self.outputThread = None
        self.setupUi(self)
        self.setWindowIcon(Icon.MainWindow_Icon)
        self.setStyleSheet(Stylesheet)
        self.listWidget.clear()
        self.resize(QSize(800, 600))
        self.action_desc.triggered.connect(self.about)
        self.load_flag = False
        self.load_data()
        self.load_num = 0
        self.label = QLabel(self)
        self.label.setGeometry((self.width() - 300) // 2, (self.height() - 100) // 2, 300, 100)
        self.label.setPixmap(QPixmap(':/icons/icons/loading.svg'))

    def load_data(self, flag=True):
        if os.path.exists('./app/data/info.json'):
            with open('./app/data/info.json', 'r', encoding='utf-8') as f:
                dic = json.loads(f.read())
                wxid = dic.get('wxid')
                if wxid:
                    me = MePC()
                    me.wxid = dic.get('wxid')
                    me.name = dic.get('name')
                    me.mobile = dic.get('mobile')
                    me.wx_dir = dic.get('wx_dir')
                    self.set_my_info(wxid)
                    self.load_flag = True
        else:
            QMessageBox.information(
                self,
                '温馨提示',
                '点击 工具->获取信息 重启后可以显示本人头像哦'
            )

    def init_ui(self):
        self.menu_output.setIcon(Icon.Output)
        self.action_output_CSV.setIcon(Icon.ToCSV)
        self.action_output_CSV.triggered.connect(self.output)
        self.action_output_contacts.setIcon(Icon.Output)
        self.action_output_contacts.triggered.connect(self.output)
        self.action_desc.setIcon(Icon.Help_Icon)
        self.action_help_contact.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/5")))
        self.action_help_chat.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/5")))
        self.action_help_decrypt.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://blog.lc044.love/post/4")))
        self.listWidget.setVisible(False)
        self.stackedWidget.setVisible(False)
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        tool_item = QListWidgetItem(Icon.Tool_Icon, '工具', self.listWidget)
        chat_item = QListWidgetItem(Icon.Chat_Icon, '聊天', self.listWidget)
        contact_item = QListWidgetItem(Icon.Contact_Icon, '好友', self.listWidget)
        myinfo_item = QListWidgetItem(Icon.Home_Icon, '我的', self.listWidget)
        tool_window = ToolWindow()
        tool_window.get_info_signal.connect(self.set_my_info)
        tool_window.decrypt_success_signal.connect(self.decrypt_success)
        tool_window.load_finish_signal.connect(self.loading)
        self.stackedWidget.addWidget(tool_window)
        self.chat_window = ChatWindow()
        # chat_window = QWidget()
        self.stackedWidget.addWidget(self.chat_window)
        self.contact_window = ContactWindow()
        self.stackedWidget.addWidget(self.contact_window)
        label = QLabel('该功能暂不支持哦')
        label.setFont(QFont("微软雅黑", 50))
        label.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(label)
        tool_window.load_finish_signal.connect(self.loading)
        self.statusbar.showMessage('聊天窗口上划到顶部会加载新的聊天记录\n一次不行那就多来几次')
        self.contact_window.load_finish_signal.connect(self.loading)
        self.chat_window.load_finish_signal.connect(self.loading)

    def setCurrentIndex(self, row):
        self.stackedWidget.setCurrentIndex(row)
        if row == 2:
            self.stackedWidget.currentWidget().show_contacts()
        if row == 1:
            self.stackedWidget.currentWidget().show_chats()

    def setWindow(self, window):
        try:
            window.load_finish_signal.connect(self.loading)
        except:
            pass
        self.stackedWidget.addWidget(window)

    def set_my_info(self, wxid):
        self.avatar = QPixmap()
        try:
            img_bytes = misc_db.get_avatar_buffer(wxid)
        except AttributeError:
            return
        if not img_bytes:
            return
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')
        self.avatar.scaled(60, 60)
        me = MePC()
        me.set_avatar(img_bytes)
        self.myavatar.setScaledContents(True)
        self.myavatar.setPixmap(self.avatar)

    def stop_loading(self, a0):
        self.label.setVisible(False)

    def loading(self, a0):
        self.load_num += 1
        if self.load_num == 1:
            self.label.clear()
            self.label.hide()
            self.okSignal.emit(True)
            self.listWidget.setVisible(True)
            self.stackedWidget.setVisible(True)
            if self.load_flag:
                self.listWidget.setCurrentRow(1)
                self.stackedWidget.setCurrentIndex(1)
            else:
                self.listWidget.setCurrentRow(0)
                self.stackedWidget.setCurrentIndex(0)

    def output(self):
        if self.sender() == self.action_output_CSV:
            self.outputThread = Output(None, type_=Output.CSV_ALL)
            self.outputThread.okSignal.connect(
                lambda x: self.message('聊天记录导出成功'))
            self.outputThread.start()
        elif self.sender() == self.action_output_contacts:
            self.outputThread = Output(None, type_=Output.CONTACT_CSV)
            self.outputThread.okSignal.connect(
                lambda x: self.message('联系人导出成功'))
            self.outputThread.start()

    def message(self, msg):
        QMessageBox.about(self, "提醒", msg)

    def about(self):
        """
        关于
        """
        QMessageBox.about(self, "关于",
                          f'''版本：{config.version}<br>QQ交流群:{config.contact},加群要求请阅读文档<br>地址：<a href='https://github.com/LC044/WeChatMsg'>https://github.com/LC044/WeChatMsg</a><br>新特性:<br>{''.join(['' + i for i in config.description])}
                            '''
                          )

    def decrypt_success(self):
        QMessageBox.about(self, "解密成功", "请重新启动")
        self.close()

    def close(self) -> bool:
        super().close()
        misc_db.close()
        msg_db.close()
        micro_msg_db.close()
        hard_link_db.close()
        self.contact_window.close()
        self.exitSignal.emit(True)


class LoadWindowThread(QThread):
    okSignal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.num = 0

    def loading(self):
        self.num += 1
        print('加载一个了')
        if self.num == 2:
            self.okSignal.emit(True)

    def run(self):
        self.chat_window = ChatWindow()
        self.contact_window = ContactWindow()
        self.contact_window.load_finish_signal.connect(self.loading)
        self.chat_window.load_finish_signal.connect(self.loading)
        print('加载完成')
        self.okSignal.emit(True)
