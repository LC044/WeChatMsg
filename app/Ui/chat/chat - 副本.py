# -*- coding: utf-8 -*-
"""
@File    : mainview.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 15:07
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
import os.path
import socket  # 导入socket模块
import datetime
import json
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .chatUi import *
from ...DataBase import data


class ChatController(QWidget, Ui_Dialog):
    exitSignal = pyqtSignal()

    # username = ''

    def __init__(self, Me, parent=None):
        super(ChatController, self).__init__(parent)
        self.ta_avatar = None
        self.setupUi(self)
        self.setWindowTitle('WeChat')
        self.setWindowIcon(QIcon('./app/data/icon.png'))
        self.initui()
        self.Me = Me
        self.Thread = ChatMsg(self.Me.username, None)
        self.Thread.isSend_signal.connect(self.showMsg)
        self.Thread.okSignal.connect(self.setScrollBarPos)
        self.contacts = {}
        self.last_btn = None
        self.chat_flag = True
        # self.showChat()
        self.message.verticalScrollBar().valueChanged.connect(self.textbrower_verticalScrollBar)
        self.show_flag = False
        self.ta_username = None
        self.last_pos = 0
        self.last_msg_time = 0  # 上次信息的时间
        self.last_talkerId = None
        self.now_talkerId = None
        self.showChat()

    def initui(self):
        self.textEdit = myTextEdit(self.frame)
        self.textEdit.setGeometry(QtCore.QRect(9, 580, 821, 141))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.textEdit.setFont(font)
        self.textEdit.setTabStopWidth(80)
        self.textEdit.setCursorWidth(1)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.sendSignal.connect(self.sendMsg)
        self.btn_sendMsg = QtWidgets.QPushButton(self.frame)
        self.btn_sendMsg.setGeometry(QtCore.QRect(680, 670, 121, 51))
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.btn_sendMsg.setFont(font)
        self.btn_sendMsg.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.btn_sendMsg.setMouseTracking(False)
        self.btn_sendMsg.setAutoFillBackground(False)
        self.btn_sendMsg.setStyleSheet("QPushButton {background-color: #f0f0f0;\n"
                                       "padding: 10px;\n"
                                       "color:rgb(5,180,104);}\n"
                                       "QPushButton:hover{background-color: rgb(198,198,198)}\n"
                                       )
        self.btn_sendMsg.setIconSize(QtCore.QSize(40, 40))
        self.btn_sendMsg.setCheckable(False)
        self.btn_sendMsg.setAutoDefault(True)
        self.btn_sendMsg.setObjectName("btn_sendMsg")
        _translate = QtCore.QCoreApplication.translate
        self.btn_sendMsg.setText(_translate("Dialog", "发送"))
        self.btn_sendMsg.setToolTip('按Enter键发送，按Ctrl+Enter键换行')

    def showChat(self):
        """
        显示聊天界面
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
            pushButton_2.usernameSingal.connect(self.Chat)
            self.contacts[username] = pushButton_2

    def Chat(self, talkerId):
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
        self.label_remark.setText(conRemark)
        self.message.clear()
        self.message.append(talkerId)
        self.ta_username = talkerId
        self.ta_avatar = data.get_avator(talkerId)
        self.textEdit.setFocus()
        self.Thread.ta_u = talkerId
        self.Thread.msg_id = 0
        self.Thread.start()
        # 创建新的线程用于显示聊天记录

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("closed")
        self.exitSignal.emit()
        self.close()

    def textbrower_verticalScrollBar(self, pos):
        """
        滚动条到0之后自动更新聊天记录
        :param pos:
        :return:
        """
        # print(pos)
        if pos > 0:
            return
        self.last_pos = self.message.verticalScrollBar().maximum()
        self.Thread.start()

    def setScrollBarPos(self, pos):
        """
        将滚动条位置设置为上次看到的地方
        :param pos:
        :return:
        """
        pos = self.message.verticalScrollBar().maximum() - self.last_pos

        print(pos)
        self.message.verticalScrollBar().setValue(pos)

    def sendMsg(self, msg):
        pass

    def check_time(self, msg_time):
        """
        判断两次聊天时间是否大于五分钟
        超过五分钟就显示时间
        :param msg_time:
        :return:
        """
        dt = msg_time - self.last_msg_time
        # print(msg_time)
        if dt // 1000 >= 300:
            s_l = time.localtime(msg_time / 1000)
            ts = time.strftime("%Y-%m-%d %H:%M", s_l)
            html = '''
            <table align="center" style="vertical-align: middle;">
        	<tbody>
        		<tr>
        			<td>%s</td>
        		</tr> 
        	</tbody>
        </table>''' % (ts)
            # print(html)
            self.last_msg_time = msg_time
            self.message.insertHtml(html)

    def showMsg(self, message):
        """
        显示聊天消息
        :param message:
        :return:
        """
        msgId = message[0]
        # print(msgId, type(msgId))
        self.message.moveCursor(self.message.textCursor().Start)
        ta_username = message[7]
        msgType = str(message[2])
        isSend = message[4]
        content = message[8]
        imgPath = message[9]
        msg_time = message[6]
        self.check_time(msg_time)

        if msgType == '1':
            self.show_text(isSend, content)
        elif msgType == '3':
            self.show_img(isSend,imgPath)
        # self.message.moveCursor(self.message.textCursor().End)

    def show_img(self, isSend, imgPath):
        'THUMBNAIL_DIRPATH://th_29cd0f0ca87652943be9ede365aabeaa'
        imgPath = imgPath.split('th_')[1]
        imgPath = f'./app/data/image2/{imgPath[0:2]}/{imgPath[2:4]}/th_{imgPath}'
        html = '''
        <td style="border: 1px #000000 solid"><img align="right" src="%s"/></td>
        ''' % imgPath
        style = 'vertical-align: top'
        if isSend:
            self.right(html,style=style)
        else:
            self.left(html,style=style)

    def show_text(self, isSend, content):

        if isSend:
            html = '''<td>%s :</td>''' % (content)
            self.right(html)
        else:
            html = '''<td>: %s</td>''' % (content)
            self.left(html)

    def right(self, content,style='vertical-align: middle'):
        html = '''
            <div>
            <table align="right" style="%s;">
        	<tbody>
        		<tr>
        			%s
        			<td style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
        			<td width="15"></td>
        		</tr>
        	</tbody>
        </table>
        </div>
        ''' % (style,content, self.Me.my_avatar)
        # print('总的HTML')
        # print(html)
        self.message.insertHtml(html)

    def left(self, content,style = 'vertical-align: middle'):
        html = '''
        <div>
           <table align="left" style="%s;">
            <tbody>
                <tr>
                    <td width="15"></td>
                    <td style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
                    %s
                </tr>
            </tbody>
        </table>
        </div>
        ''' % (style,self.ta_avatar, content)
        self.message.insertHtml(html)

    def destroy_me(self):
        """注销账户"""
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


class myTextEdit(QtWidgets.QTextEdit):  # 继承 原本组件
    sendSignal = pyqtSignal(str)

    def __init__(self, parent):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.parent = parent
        _translate = QtCore.QCoreApplication.translate
        self.setHtml(_translate("Dialog",
                                "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                "p, li { white-space: pre-wrap; }\n"
                                "</style></head><body style=\" font-family:\'SimSun\'; font-size:15pt; font-weight:400; font-style:normal;\">\n"
                                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))

    def keyPressEvent(self, event):
        QtWidgets.QTextEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Return:  # 如果是Enter 按钮
            modifiers = event.modifiers()
            if modifiers == Qt.ControlModifier:
                print('success press ctrl+enter key', self.toPlainText())
                self.append('\0')
                return
            self.sendSignal.emit(self.toPlainText())
            print('success press enter key', self.toPlainText())

        # if modifiers == (Qt.ControlModifier) and event.key() == Qt.Key_Return:
        #     self.sendSignal.emit(self.toPlainText())
        #     print('success press enter key', self.toPlainText())
