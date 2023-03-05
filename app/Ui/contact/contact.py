# -*- coding: utf-8 -*-
"""
@File    : contact.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .contactUi import *
from ...DataBase import data, output
from .userinfo import userinfoUi
from .analysis import analysis


class ContactController(QWidget, Ui_Dialog):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''

    def __init__(self, Me, parent=None):
        super(ContactController, self).__init__(parent)
        self.chatroomFlag = None
        self.ta_avatar = None
        self.setupUi(self)
        self.setWindowTitle('WeChat')
        self.setWindowIcon(QIcon('./app/data/icon.png'))
        self.initui()
        self.Me = Me
        self.Thread = ChatMsg(self.Me.username, None)
        self.contacts = {}
        self.last_btn = None
        self.chat_flag = True
        self.show_flag = False
        self.ta_username = None
        self.last_pos = 0
        self.last_msg_time = 0  # 上次信息的时间
        self.last_talkerId = None
        self.now_talkerId = None
        self.showContact()
        self.userinfo = userinfoUi.Ui_Frame()  # 联系人信息界面
        self.userinfo.setupUi(self.frame)
        self.userinfo.btn_outbut.clicked.connect(self.output)
        self.userinfo.progressBar.setVisible(False)
        self.userinfo.btn_analysis.clicked.connect(self.analysis)

    def initui(self):
        self.qurl = QUrl('baidu.com')
        # self.urlSignal.connect(self.hyperlink)
        # self.message.setOpenLinks(False)
        # self.message.setOpenExternalLinks(False)

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
        self.scrollAreaWidgetContents.setGeometry(
            QtCore.QRect(0, 0, 300, max_hight))
        for i in range(len(rconversations)):
            rconversation = rconversations[i]
            username = rconversation[1]
            # print('联系人：', i, rconversation)
            pushButton_2 = Contact(self.scrollAreaWidgetContents, i, rconversation)
            pushButton_2.setGeometry(QtCore.QRect(0, 80 * i, 300, 80))
            pushButton_2.setLayoutDirection(QtCore.Qt.LeftToRight)
            pushButton_2.clicked.connect(pushButton_2.show_msg)
            pushButton_2.usernameSingal.connect(self.Contact)
            self.contacts[username] = pushButton_2

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
                "QPushButton {background-color: rgb(253,253,253);}"
                "QPushButton:hover{background-color: rgb(209,209,209);}\n"
            )
        self.last_talkerId = talkerId
        self.contacts[talkerId].setStyleSheet(
            "QPushButton {background-color: rgb(198,198,198);}"
            "QPushButton:hover{background-color: rgb(209,209,209);}\n"
        )
        conRemark = data.get_conRemark(talkerId)
        nickname, alias = data.get_nickname(talkerId)
        self.label_remark.setText(conRemark)
        self.ta_username = talkerId
        if '@chatroom' in talkerId:
            self.chatroomFlag = True
        else:
            self.chatroomFlag = False
        self.ta_avatar = data.get_avator(talkerId)
        self.userinfo.l_remark.setText(conRemark)
        pixmap = QPixmap(self.ta_avatar).scaled(60, 60)  # 按指定路径找到图片
        self.userinfo.l_avatar.setPixmap(pixmap)
        self.userinfo.l_nickname.setText(f'昵称：{nickname}')
        self.userinfo.l_username.setText(f'微信号：{alias}')
        self.userinfo.lineEdit.setText(conRemark)

    def output(self):
        """
        导出聊天记录
        :return:
        """
        self.outputThread = output.Output(self.Me, self.now_talkerId)
        self.outputThread.progressSignal.connect(self.output_progress)
        self.outputThread.rangeSignal.connect(self.set_progressBar_range)
        self.outputThread.okSignal.connect(self.hide_progress_bar)
        self.outputThread.start()

    def hide_progress_bar(self, int):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Information)
        reply.setWindowTitle('OK')
        reply.setText("导出聊天记录成功")
        reply.addButton("确认", QMessageBox.AcceptRole)
        reply.addButton("取消", QMessageBox.RejectRole)
        # reply.addButton("忽略", QMessageBox.DestructiveRole)
        print(reply)
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
        self.analysisView = analysis.AnalysisController(self.now_talkerId)
        self.analysisView.show()
        pass


class Contact(QtWidgets.QPushButton):
    """
    联系人类，继承自pyqt的按钮，里面封装了联系人头像等标签
    """
    usernameSingal = pyqtSignal(str)

    def __init__(self, Ui, id=None, contact=None):
        super(Contact, self).__init__(Ui)
        self.layoutWidget = QtWidgets.QWidget(Ui)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout1 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout1.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout1.setContentsMargins(10, 10, 10, 10)
        self.gridLayout1.setSpacing(10)
        self.gridLayout1.setObjectName("gridLayout1")
        self.label_time = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_time.setFont(font)
        self.label_time.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_time.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_time.setObjectName("label_time")
        self.gridLayout1.addWidget(self.label_time, 0, 2, 1, 1)
        self.label_remark = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Adobe 黑体 Std R")
        font.setPointSize(10)
        self.label_remark.setFont(font)
        self.label_remark.setObjectName("label_remark")
        self.gridLayout1.addWidget(self.label_remark, 0, 1, 1, 1)
        self.label_msg = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_msg.setFont(font)
        self.label_msg.setObjectName("label_msg")
        self.gridLayout1.addWidget(self.label_msg, 1, 1, 1, 2)
        self.label_avatar = QtWidgets.QLabel(self.layoutWidget)
        self.label_avatar.setMinimumSize(QtCore.QSize(60, 60))
        self.label_avatar.setMaximumSize(QtCore.QSize(60, 60))
        self.label_avatar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_avatar.setAutoFillBackground(False)
        self.label_avatar.setStyleSheet("background-color: #ffffff;")
        self.label_avatar.setInputMethodHints(QtCore.Qt.ImhNone)
        self.label_avatar.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_avatar.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_avatar.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_avatar.setObjectName("label_avatar")
        self.gridLayout1.addWidget(self.label_avatar, 0, 0, 2, 1)
        self.gridLayout1.setColumnStretch(0, 1)
        self.gridLayout1.setColumnStretch(1, 6)
        self.gridLayout1.setRowStretch(0, 5)
        self.gridLayout1.setRowStretch(1, 3)
        self.setLayout(self.gridLayout1)
        self.setStyleSheet(
            "QPushButton {background-color: rgb(253,253,253);}"
            "QPushButton:hover{background-color: rgb(209,209,209);}\n"
        )
        self.msgCount = contact[0]
        self.username = contact[1]
        self.conversationTime = contact[6]
        self.msgType = contact[7]
        self.digest = contact[8]
        hasTrunc = contact[10]
        attrflag = contact[11]
        if hasTrunc == 0:
            if attrflag == 0:
                self.digest = '[动画表情]'
            elif attrflag == 67108864:
                try:
                    remark = data.get_conRemark(contact[9])
                    msg = self.digest.split(':')[1].strip('\n').strip()
                    self.digest = f'{remark}:{msg}'
                except Exception as e:
                    # print(self.digest)
                    # print(e)
                    pass
            else:
                pass
        self.show_info(id)

    def show_info(self, id):
        avatar = data.get_avator(self.username)
        # print(avatar)
        remark = data.get_conRemark(self.username)
        time = datetime.datetime.now().strftime("%m-%d %H:%M")
        msg = '还没说话'
        pixmap = QPixmap(avatar).scaled(60, 60)  # 按指定路径找到图片
        self.label_avatar.setPixmap(pixmap)  # 在label上显示图片
        self.label_remark.setText(remark)
        self.label_msg.setText(self.digest)
        self.label_time.setText(data.timestamp2str(self.conversationTime)[2:])

    def show_msg(self):
        self.usernameSingal.emit(self.username)


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
