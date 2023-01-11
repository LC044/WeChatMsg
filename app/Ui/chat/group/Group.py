# -*- coding: utf-8 -*-
"""
@File    : Group.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/20 20:26
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
import datetime
import json

from .GroupUi import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ....DB import data
import time
# from .chat import MainWinController
from .create_groupUi import Ui_Frame
from .CreateGroup import CreateGroupView
from .addGroup import Ui_Frame as Add_GroupUi


class GroupControl(QWidget, Ui_Form):
    backSignal = pyqtSignal(str)
    addSignal = pyqtSignal(int)

    # createSignal = pyqtSignal(Group)

    def __init__(self, parent=None, Me=None):
        super(GroupControl, self).__init__(parent)
        self.groups = None
        self.setupUi(self)
        self.Me = Me
        self.btn_create_group.clicked.connect(self.create_group_view)
        self.btn_add_group.clicked.connect(self.addGroupUi)
        self.btn_sendMsg.clicked.connect(self.sendMsg)  # 发送信息按钮
        self.btn_del_group.clicked.connect(self.delete_group)
        self.toolButton.clicked.connect(self.about)
        self.frame_ag = QtWidgets.QFrame(self.frame)
        self.frame_ag.setGeometry(QtCore.QRect(0, 0, 800, 720))
        self.frame_ag.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_ag.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_ag.setObjectName("frame_cg")
        self.frame_ag.setVisible(False)
        self.addSignal.connect(self.new_groupUi)
        # print(self.username)
        self.groups = {}
        self.last_gid = None
        self.now_gid = None
        self.group_users = None
        self.last_msg_time = datetime.datetime(2022, 12, 19, 15, 4)  # 上次信息的时间
        self.initUi()

    def initUi(self):

        groups = data.get_groups(self.Me.username)
        self.groups_num = len(groups)
        print('群组：', groups)
        max_hight = max(self.groups_num * 80, 680)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 300, max_hight))
        for i in range(len(groups)):
            group = groups[i]
            # print(contact)
            g_id = group[0]
            print('群聊信息：', group)
            pushButton_2 = OneGroup(self.scrollAreaWidgetContents, group)
            pushButton_2.setGeometry(QtCore.QRect(0, 80 * i, 300, 80))
            pushButton_2.setLayoutDirection(QtCore.Qt.LeftToRight)
            pushButton_2.clicked.connect(pushButton_2.show_msg)
            pushButton_2.gidSingal.connect(self.chat)
            self.groups[g_id] = pushButton_2

    def chat(self, g_id):
        # self.frame_ag.setVisible(False)
        print('当前聊天群号：', g_id)
        self.frame_msg.setVisible(True)
        self.frame_ag.setVisible(False)
        self.now_gid = g_id
        self.group_users = data.get_group_users(g_id)
        # 将当前群的界面设置为灰色
        # if self.last_gid and self.last_gid != g_id:
        #     self.groups[self.last_gid].setStyleSheet("background-color : rgb(253,253,253)")
        # self.last_gid = g_id
        # self.groups[g_id].setStyleSheet("background-color : rgb(198,198,198)")
        g_name = self.groups[g_id].g_name
        self.l_g_name.setText(f'{g_name}({g_id})')
        self.message.clear()
        self.message.append(str(g_id))
        # 创建新的线程用于显示聊天记录
        self.Thread = ChatMsg(self.Me.username, g_id, self.Me.socket)
        self.Thread.isSend_signal.connect(self.showMsg)
        self.Thread.recvSignal.connect(self.showMsg)
        self.Thread.sendSignal.connect(self.showMsg)
        self.Thread.start()
        pass

    def sendMsg(self, msg):
        """
        发送信息
        :param msg:信息内容
        :return:
        """
        msg = self.textEdit.toPlainText()
        message = self.Thread.send_msg(msg)
        if message:
            print(msg, '发送成功')
            # self.showMsg(message)
        else:
            print(msg, '发送失败')
        self.textEdit.clear()

    def create_group_view(self):
        """建群界面"""
        self.frame_msg.setVisible(False)
        self.frame_ag.setVisible(False)
        # self.frame_ag.setVisible(True)
        # print(self.Me.__dict__)
        self.create_view = CreateGroupView(username=self.Me.username)
        self.create_view.gidSignal.connect(self.new_groupUi)
        self.create_view.show()

    def addGroupBack(self):
        """加群界面"""
        self.frame_msg.setVisible(True)
        self.frame_ag.setVisible(False)
        # self.CG_Ui = None

    def delete_group(self):
        """退群"""
        a = QMessageBox.question(self, '警告', '你确定要退群吗?', QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.No)  # "退出"代表的是弹出框的标题,"你确认退出.."表示弹出框的内容
        if a == QMessageBox.Yes:
            data.delete_group(self.Me.username, self.now_gid)
            self.frame_msg.setVisible(False)
            self.last_gid = None
            self.groups_num -= 1
            self.l_g_name.setText('已退群')
            self.groups[self.now_gid].setVisible(False)
            self.groups.pop(self.now_gid)
        else:
            return

    def show(self):
        self.message.append('2020303457')

    def addGroupUi(self):
        """加群的界面"""
        self.frame_msg.setVisible(False)
        self.CG_Ui = Add_GroupUi()
        self.CG_Ui.setupUi(self.frame_ag)
        self.CG_Ui.back.clicked.connect(self.addGroupBack)
        self.CG_Ui.btn_add.clicked.connect(self.addGroup)
        self.CG_Ui.btn_search.clicked.connect(self.searchGroup)
        self.frame_ag.setVisible(True)
        self.CG_Ui.tips.setVisible(False)
        self.CG_Ui.time.setVisible(False)
        pass

    def searchGroup(self):
        """搜索群聊"""
        gid = self.CG_Ui.line_g_id.text()
        if not gid:
            self.CG_Ui.error.setText('请输入群号')
            return False
        nickname = self.CG_Ui.line_nickname.text()
        group = data.search_group(gid)
        if not group:
            self.CG_Ui.error.setText('未找到群聊')
            return False
        avatar = data.get_avator(gid)
        pixmap = QPixmap(avatar).scaled(60, 60)  # 按指定路径找到图片
        self.CG_Ui.avatar_img.setPixmap(pixmap)  # 在label上显示图片
        return group

    def addGroup(self):
        """添加群聊"""
        gid = self.CG_Ui.line_g_id.text()
        gid = int(gid)
        nickname = self.CG_Ui.line_nickname.text()
        flag = data.add_group(self.Me.username, gid, nickname)
        if not flag:
            self.CG_Ui.error.setText('群聊不存在')
            return False
        avatar = data.get_avator(gid)
        pixmap = QPixmap(avatar).scaled(60, 60)  # 按指定路径找到图片
        self.CG_Ui.avatar_img.setPixmap(pixmap)  # 在label上显示图片
        self.CG_Ui.error.setText('加群成功')
        # self.addSignal.emit(gid)
        self.new_groupUi(gid)

    def new_groupUi(self, gid):
        nickname = ''
        group = data.search_group(gid)
        if not group:
            return False
        g_name = group[1]
        self.groups_num += 1
        max_hight = max(self.groups_num * 80, 680)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 300, max_hight))
        group = [
            gid, g_name, nickname, 3, 1
        ]
        # g_id = group[0]
        print('群聊信息：', group)
        pushButton_2 = OneGroup(self.scrollAreaWidgetContents, group)
        pushButton_2.setGeometry(QtCore.QRect(0, 80 * self.groups_num - 80, 300, 80))
        pushButton_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        pushButton_2.clicked.connect(pushButton_2.show_msg)
        pushButton_2.gidSingal.connect(self.chat)
        # pushButton_2.setVisible(True)
        print('加群成功', gid)
        print(pushButton_2.g_id)
        self.groups[gid] = pushButton_2
        pushButton_2.setVisible(True)
        print(self.groups)
        print(self.now_gid, self.last_gid)

    def showMsg(self, message):
        """
        显示聊天消息
        :param message:
        :return:
        """
        # print(message)
        gid = message[1]
        if self.now_gid is None or gid != self.now_gid:
            return
        # self.now_gid = gid
        talker = message[5]
        isSend = message[6]
        content = message[3]
        msg_time = message[4]
        # print(message)
        # print(msg_time, type(msg_time))
        self.check_time(msg_time)
        if isSend == 1 and talker == self.Me.username:
            # 自己发的信息在右边显示
            self.right(content, talker)
        else:
            # 收到的信息在左边显示
            self.left(content, talker)
        self.message.moveCursor(self.message.textCursor().End)

    def about(self):
        group = data.search_group(self.now_gid)
        QMessageBox.about(
            self,
            "关于",
            f"关于本群\n群名：{group[1]}\n群号：{self.now_gid}"
        )

    def check_time(self, msg_time):
        """
        判断两次聊天时间是否大于五分钟
        超过五分钟就显示时间
        :param msg_time:
        :return:
        """
        dt = msg_time - self.last_msg_time
        # print(msg_time)
        if dt.seconds >= 300:
            html = '''
            <table align="center" style="vertical-align: middle;">
        	<tbody>
        		<tr>
        			<td>%s</td>
        		</tr> 
        	</tbody>
        </table>''' % (msg_time.strftime("%Y-%m-%d %H:%M"))
            # print(html)
            self.last_msg_time = msg_time
            self.message.insertHtml(html)

    def right(self, content, taklekId):
        html = '''
            <div>
            <table align="right" style="vertical-align: middle;">
        	<tbody>
        		<tr>
        			<td>%s :</td>
        			<td style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
        			<td width="15"></td>
        		</tr>
        	</tbody>
        </table>
        </div>
        ''' % (content, self.Me.my_avatar)
        self.message.insertHtml(html)

    def left(self, content, taklekId):
        avatar = data.get_avator(taklekId)
        html = '''
        <div>
                   <table align="left" style="vertical-align: middle;">
                	<tbody>
                		<tr>
                		    <td width="15"></td>
                			<td style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
                			<td>: %s</td>
                		</tr>
                	</tbody>
                </table>
                </div>
                ''' % (avatar, content)
        self.message.insertHtml(html)


class OneGroup(QtWidgets.QPushButton):
    """
        联系人类，继承自pyqt的按钮，里面封装了联系人头像等标签
    """
    gidSingal = pyqtSignal(int)

    def __init__(self, Ui, contact=None):
        super(OneGroup, self).__init__(Ui)
        self.layoutWidget = QtWidgets.QWidget(Ui)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout1 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout1.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout1.setContentsMargins(10, 10, 10, 10)
        self.gridLayout1.setHorizontalSpacing(20)
        self.gridLayout1.setVerticalSpacing(10)
        self.gridLayout1.setObjectName("gridLayout1")
        self.time0_1 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.time0_1.setFont(font)
        self.time0_1.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.time0_1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.time0_1.setObjectName("time0_1")
        self.gridLayout1.addWidget(self.time0_1, 0, 2, 1, 1)
        self.remark1 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.remark1.setFont(font)
        self.remark1.setObjectName("remark1")
        self.gridLayout1.addWidget(self.remark1, 0, 1, 1, 1)
        self.msg1 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.msg1.setFont(font)
        self.msg1.setObjectName("msg1")
        self.gridLayout1.addWidget(self.msg1, 1, 1, 1, 2)
        self.image1 = QtWidgets.QLabel(self.layoutWidget)
        self.image1.setMinimumSize(QtCore.QSize(60, 60))
        self.image1.setMaximumSize(QtCore.QSize(60, 60))
        self.image1.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.image1.setAutoFillBackground(False)
        self.image1.setStyleSheet("background-color: #ffffff;")
        self.image1.setInputMethodHints(QtCore.Qt.ImhNone)
        self.image1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.image1.setFrameShadow(QtWidgets.QFrame.Plain)
        self.image1.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.image1.setObjectName("image1")
        self.gridLayout1.addWidget(self.image1, 0, 0, 2, 1)
        self.gridLayout1.setColumnStretch(0, 1)
        self.gridLayout1.setColumnStretch(1, 6)
        self.gridLayout1.setRowStretch(0, 5)
        self.gridLayout1.setRowStretch(1, 3)
        self.setLayout(self.gridLayout1)
        if contact:
            self.g_id = contact[0]
            self.g_name = contact[1]
            self.nickname = contact[2]
            self.type = contact[3]
            self.addTime = contact[4]
            self.show_info(id)

    def show_info(self, id):
        if 1:
            # try:
            avatar = data.get_avator(self.g_id)
            remark = id
            time = datetime.datetime.now().strftime("%m-%d %H:%M")
            msg = '还没说话'
            pixmap = QPixmap(avatar).scaled(60, 60)  # 按指定路径找到图片
            self.image1.setPixmap(pixmap)  # 在label上显示图片
            self.remark1.setText(self.g_name)
            self.time0_1.setText(time)

    def show_msg(self):
        print('点击的群号', self.g_id)
        self.gidSingal.emit(self.g_id)
        pass


class ChatMsg(QThread):
    """
    发送信息线程
    """
    isSend_signal = pyqtSignal(tuple)
    recvSignal = pyqtSignal(tuple)
    sendSignal = pyqtSignal(tuple)

    def __init__(self, my_u, g_id, socket, parent=None):
        super().__init__(parent)
        self.sec = 2  # 默认1000秒
        self.my_u = my_u
        self.g_id = g_id
        self.group_users = data.get_group_users(g_id)
        self.my_avatar = data.get_avator(my_u)
        self.socket = socket

    def send_msg(self, msg):
        # 给群里所有在线的用户发送信息
        for group_user in self.group_users:
            username = group_user[0]
            if username == self.my_u:
                continue
            ta_port = group_user[4]
            nickname = group_user[3]
            self.ta_addr = ('localhost', ta_port)
            if ta_port == -1:
                print(f'{nickname}不在线')
                continue
            send_data = {
                'type': 'G',
                'gid': self.g_id,
                'username': self.my_u,
                'content': msg
            }
            print(f'{nickname}在线,{msg} 发送成功')
            self.socket.sendto(json.dumps(send_data).encode('utf-8'), self.ta_addr)
        message = data.send_group_msg(
            gid=self.g_id,
            msg=msg,
            talker=self.my_u,
            IsSend=1,
            _type=3
        )
        self.sendSignal.emit(message)
        return message

    def run(self):
        # return
        messages = data.get_group_message(self.g_id)
        # print(messages)
        for message in messages:
            self.isSend_signal.emit(message)
        # self.recv_msg()
