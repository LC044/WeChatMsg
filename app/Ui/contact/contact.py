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
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import app.Ui.MyComponents.Contact as MyLabel
from .analysis import analysis
from .contactInfo import ContactInfo
from .contactUi import *
from .emotion import emotion
from .report import report
from .userinfo import userinfoUi
from ...DataBase import data, output

EMOTION = 1
ANALYSIS = 2


class StackedWidget():
    def __init__(self):
        pass


class ContactController(QWidget, Ui_Dialog):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''

    def __init__(self, Me, parent=None):
        super(ContactController, self).__init__(parent)
        self.emotionView = None
        self.analysisView = None
        self.chatroomFlag = None
        self.ta_avatar = None
        self.setupUi(self)
        self.setWindowTitle('WeChat')
        self.setWindowIcon(QIcon('./app/data/icons/logo.svg'))
        # self.setStyleSheet('''QWidget{background-color:rgb(255, 255, 255);}''')
        self.initui()
        self.Me = Me
        self.Thread = ChatMsg(self.Me.wxid, None)
        self.contacts: Dict[str, MyLabel.ContactUi] = {}
        self.contactInfo: Dict[str, ContactInfo] = {}
        self.last_btn = None
        self.chat_flag = True
        self.show_flag = False
        self.ta_username = None
        self.last_pos = 0
        self.last_msg_time = 0  # 上次信息的时间
        self.last_talkerId = None
        self.now_talkerId = None
        self.last_analysis = None
        self.now_analysis = None
        self.view_emotion = {}
        self.view_analysis = {}
        self.showContact()

        # self.now_btn = self.userinfo
        self.now_btn = None
        self.last_btn = None

    def initui(self):
        return
        self.lay0 = QVBoxLayout()
        self.stackedWidget.setStyleSheet('''QWidget{background-color:rgb(255, 255, 255);}''')
        self.frame = QtWidgets.QFrame()
        self.frame.setObjectName("frame")
        self.userinfo = userinfoUi.Ui_Frame()  # 联系人信息界面
        self.userinfo.setupUi(self.frame)
        self.userinfo.progressBar.setVisible(False)
        self.stackedWidget.addWidget(self.frame)
        # self.lay0.addWidget(self.frame)

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
            self.contactInfo[username] = ContactInfo(username)
            self.stackedWidget.addWidget(self.contactInfo[username])

    def Contact(self, talkerId):
        """
        聊天界面 点击联系人头像时候显示聊天数据
        :param talkerId:
        :return:
        """
        self.now_talkerId = talkerId
        # self.frame.setVisible(True)
        # self.setViewVisible(self.now_talkerId)
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
        # # 设置联系人的基本信息
        # conRemark = self.contacts[talkerId].contact.conRemark
        # nickname = self.contacts[talkerId].contact.nickname
        # alias = self.contacts[talkerId].contact.alias
        #
        # self.label_remark.setText(conRemark)
        # self.ta_username = talkerId
        # if '@chatroom' in talkerId:
        #     self.chatroomFlag = True
        # else:
        #     self.chatroomFlag = False
        # self.userinfo.l_remark.setText(conRemark)
        # pixmap = self.contacts[talkerId].contact.avatar
        # self.userinfo.l_avatar.setPixmap(pixmap)
        # self.userinfo.l_nickname.setText(f'昵称：{nickname}')
        # self.userinfo.l_username.setText(f'微信号：{alias}')
        # self.userinfo.lineEdit.setText(conRemark)

    def output(self):
        """
        导出聊天记录
        :return:
        """
        self.setViewVisible(self.now_talkerId)

        if self.sender() == self.toDocxAct:
            self.outputThread = output.Output(self.Me, self.now_talkerId)
            self.outputThread.progressSignal.connect(self.output_progress)
            self.outputThread.rangeSignal.connect(self.set_progressBar_range)
            self.outputThread.okSignal.connect(self.hide_progress_bar)
            self.outputThread.start()
        elif self.sender() == self.toCSVAct:
            print('开始导出csv')
            self.outputThread = output.Output(self.Me, self.now_talkerId, type_=output.Output.CSV)
            self.outputThread.progressSignal.connect(self.output_progress)
            self.outputThread.rangeSignal.connect(self.set_progressBar_range)
            self.outputThread.okSignal.connect(self.hide_progress_bar)
            self.outputThread.start()
            print('导出csv')
        elif self.sender() == self.toHtmlAct:
            print('功能暂未实现')
            QMessageBox.warning(self,
                                "别急别急",
                                "马上就实现该功能"
                                )

    def hide_progress_bar(self, int):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Information)
        reply.setWindowTitle('OK')
        reply.setText(f"导出聊天记录成功\n在.\\data\\目录下")
        reply.addButton("确认", QMessageBox.AcceptRole)
        reply.addButton("取消", QMessageBox.RejectRole)
        api = reply.exec_()
        self.userinfo.progressBar.setVisible(False)

    def set_progressBar_range(self, value):
        self.userinfo.progressBar.setVisible(True)
        self.userinfo.progressBar.setRange(0, value)

    def output_progress(self, value):
        self.userinfo.progressBar.setProperty('value', value)

    def analysis(self):
        """
        聊天分析
        :return:
        """
        self.frame.setVisible(False)  # 将userinfo界面设置为不可见
        # 判断talkerId是否已经分析过了
        # 是：则清空其他界面，直接显示该界面
        # 否：清空其他界面，创建用户界面并显示
        if 'room' in self.now_talkerId:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return
        if self.now_talkerId in self.view_analysis:
            self.setViewVisible(self.now_talkerId, mod=ANALYSIS)
            return True
        else:
            self.setViewVisible(self.now_talkerId)
        self.view_analysis[self.now_talkerId] = analysis.AnalysisController(self.now_talkerId)
        # self.lay0.addWidget(self.view_analysis[self.now_talkerId])
        self.last_analysis = self.now_talkerId
        self.stackedWidget.addWidget(self.view_analysis[self.now_talkerId])
        self.setViewVisible(self.now_talkerId, mod=ANALYSIS)

    def emotionale_Analysis(self):
        print('情感分析', data.get_conRemark(self.now_talkerId))
        self.frame.setVisible(False)  # 将userinfo界面设置为不可见
        # 判断talkerId是否已经分析过了
        # 是：则清空其他界面，直接显示该界面
        # 否：清空其他界面，创建用户界面并显示
        if self.now_talkerId in self.view_emotion:
            self.setViewVisible(self.now_talkerId, mod=EMOTION)
            return True
        else:
            self.setViewVisible(self.now_talkerId)
        self.view_emotion[self.now_talkerId] = emotion.EmotionController(self.ta_username)
        # self.lay0.addWidget(self.view_emotion[self.now_talkerId])
        self.last_analysis = self.now_talkerId
        self.stackedWidget.addWidget(self.view_emotion[self.now_talkerId])
        self.setViewVisible(self.now_talkerId, mod=EMOTION)
        pass

    def annual_report(self):
        QMessageBox.warning(
            self,
            "提示",
            "敬请期待"
        )
        return
        self.report = report.ReportController(123)
        self.report.show()

    def showUserinfo(self):
        pass
        # self.analysisView = analysis.AnalysisController(self.now_talkerId)
        # # self.lay0 = QHBoxLayout()
        # # self.widget.setLayout(self.lay0)
        # self.lay0.addWidget(self.analysisView)

    def setViewVisible(self, wxid: str, mod=None):
        """
        设置当前可见窗口
        """
        match mod:
            case None:
                self.stackedWidget.setCurrentWidget(self.frame)
            case 1:
                if not self.last_analysis:
                    return False
                self.stackedWidget.setCurrentWidget(self.view_emotion[self.now_talkerId])
            case 2:
                if not self.last_analysis:
                    return False
                self.stackedWidget.setCurrentWidget(self.view_analysis[self.now_talkerId])

    def back(self):
        """
        将userinfo界面设置为可见，其他界面设置为不可见
        """
        self.frame.setVisible(True)
        self.setViewVisible(self.now_talkerId)


class ChatMsg(QThread):
    """
    发送信息线程
    """
    isSend_signal = pyqtSignal(tuple)
    okSignal = pyqtSignal(int)

    def __init__(self, my_u, ta_u, parent=None):
        super().__init__(parent)
        self.sec = 2  # 默认1000秒
        self.my_u = my_u
        self.ta_u = ta_u
        self.my_avatar = data.get_avator(my_u)
        self.msg_id = 0

    def run(self):
        self.ta_avatar = data.get_avator(self.ta_u)
        messages = data.get_message(self.ta_u, self.msg_id)
        # messages.reverse()
        for message in messages:
            self.isSend_signal.emit(message)
        self.msg_id += 1
        self.okSignal.emit(1)
