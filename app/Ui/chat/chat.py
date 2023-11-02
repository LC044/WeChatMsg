# -*- coding: utf-8 -*-
"""
@File    : chat.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 17:07
@IDE     : Pycharm
@Version : Python3.10
@comment : 聊天窗口
"""
import time
from typing import Dict

import xmltodict
from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from app.Ui.MyComponents.Contact import ContactUi
from app.person import Me
from .chatUi import *
from ...DataBase import data
from ...ImageBox.ui import MainDemo


class ChatController(QWidget, Ui_Form):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''

    def __init__(self, me: Me, parent=None):
        super(ChatController, self).__init__(parent)
        self.chatroomFlag = None
        self.ta_avatar = None
        self.setupUi(self)
        self.message = self.message_2
        self.frame = self.frame_2
        self.scrollAreaWidgetContents = self.scrollAreaWidgetContents_2
        self.label_remark = self.label_remark_2
        self.textEdit = self.textEdit_2
        self.setWindowTitle('WeChat')
        self.setWindowIcon(QIcon('./app/data/icon.png'))
        self.initui()
        self.Me = me

        self.Thread = ChatMsg(self.Me.wxid, None)
        self.Thread.isSend_signal.connect(self.showMsg)
        self.Thread.okSignal.connect(self.setScrollBarPos)

        self.contacts: Dict[str, ContactUi] = {}
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
        self.qurl = QUrl('baidu.com')
        # self.urlSignal.connect(self.hyperlink)
        self.message.setOpenLinks(False)
        self.message.setOpenExternalLinks(False)
        # self.message.anchorClicked(self.hyperlink())
        self.message.anchorClicked.connect(self.hyperlink)
        # self.btn_sendMsg = QtWidgets.QPushButton(self.textEdit)
        # self.btn_sendMsg.setGeometry(QtCore.QRect(1, 1, 121, 51))
        # font = QtGui.QFont()
        # font.setFamily("黑体")
        # font.setPointSize(15)
        # font.setBold(False)
        # font.setWeight(50)
        # self.btn_sendMsg.setFont(font)
        # self.btn_sendMsg.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        # self.btn_sendMsg.setMouseTracking(False)
        # self.btn_sendMsg.setAutoFillBackground(False)
        # self.btn_sendMsg.setStyleSheet("QPushButton {background-color: #f0f0f0;\n"
        #                                "padding: 10px;\n"
        #                                "color:rgb(5,180,104);}\n"
        #                                "QPushButton:hover{background-color: rgb(198,198,198)}\n"
        #                                )
        # self.btn_sendMsg.setIconSize(QtCore.QSize(40, 40))
        # self.btn_sendMsg.setCheckable(False)
        # self.btn_sendMsg.setAutoDefault(True)
        # self.btn_sendMsg.setObjectName("btn_sendMsg")
        # _translate = QtCore.QCoreApplication.translate
        # self.btn_sendMsg.setText(_translate("Dialog", "发送"))
        self.btn_sendMsg_2.setToolTip('按Enter键发送，按Ctrl+Enter键换行')

    def showChat(self):
        """
        显示联系人界面
        :return:
        """
        if self.show_flag:
            return
        self.show_flag = True
        rconversations = data.get_rconversation()
        # max_hight = max(len(rconversations) * 80, 680)
        max_hight = max(len(rconversations) * 80, self.size().height())

        self.scrollAreaWidgetContents.setGeometry(
            QtCore.QRect(0, 0, 300, max_hight))
        for i in range(len(rconversations)):
            rconversation = rconversations[i]
            username = rconversation[1]
            # print('联系人：', i, rconversation)
            pushButton_2 = ContactUi(self.scrollAreaWidgetContents, i, rconversation)
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
                "QPushButton {background-color: rgb(220,220,220);}"
                "QPushButton:hover{background-color: rgb(208,208,208);}\n"
            )
        self.last_talkerId = talkerId
        self.contacts[talkerId].setStyleSheet(
            "QPushButton {background-color: rgb(198,198,198);}"
            "QPushButton:hover{background-color: rgb(209,209,209);}\n"
        )
        conRemark = self.contacts[talkerId].contact.conRemark
        self.label_remark.setText(conRemark)
        self.message.clear()
        self.message.append(talkerId)
        self.ta_username = talkerId
        if '@chatroom' in talkerId:
            self.chatroomFlag = True
        else:
            self.chatroomFlag = False
        self.ta_avatar = self.contacts[talkerId].contact.avatar_path
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

    def check_time(self, msg_time):
        """
        判断两次聊天时间是否大于五分钟
        超过五分钟就显示时间
        :param msg_time:
        :return:
        """
        dt = msg_time - self.last_msg_time
        # print(msg_time)
        if abs(dt // 1000) >= 300:
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
            # return
            self.show_text(isSend, content)
        elif msgType == '3':
            # return
            self.show_img(isSend, imgPath, content)
        elif msgType == '47':
            # return
            self.show_emoji(isSend, imgPath, content)
        elif msgType == '268445456':
            self.show_recall_information(content)
        elif msgType == '922746929':
            self.pat_a_pat(content)
        # self.message.moveCursor(self.message.textCursor().End)

    def pat_a_pat(self, content):
        try:
            pat_data = xmltodict.parse(content)
            pat_data = pat_data['msg']['appmsg']['patMsg']['records']['record']
            fromUser = pat_data['fromUser']
            pattedUser = pat_data['pattedUser']
            template = pat_data['template']
            template = ''.join(template.split('${pattedusername@textstatusicon}'))
            template = ''.join(template.split('${fromusername@textstatusicon}'))
            template = template.replace(f'${{{fromUser}}}', data.get_conRemark(fromUser))
            template = template.replace(f'${{{pattedUser}}}', data.get_conRemark(pattedUser))
            print(template)
        except Exception as e:
            print(e)
            template = '糟糕！出错了。'

        html = '''
            <table align="center" style="vertical-align: middle;">
            <tbody>
                <tr>
                    <td>%s</td>
                </tr> 
            </tbody>
        </table>''' % template
        self.message.insertHtml(html)

    def show_recall_information(self, content):
        html = '''
                <table align="center" style="vertical-align: middle;">
                <tbody>
                    <tr>
                        <td>%s</td>
                    </tr> 
                </tbody>
            </table>''' % content
        self.message.insertHtml(html)

    def show_emoji(self, isSend, imagePath, content):
        imgPath = data.get_emoji(imagePath)
        print('emoji:', imgPath)
        if not imgPath:
            return False
        image = Image.open(imgPath)
        imagePixmap = image.size  # 宽高像素
        # 设置最大宽度
        if imagePixmap[0] < 150:
            size = ""
        else:
            size = '''height="150" width="150"'''
        html = '''
                <td style="border: 1px #000000 solid;"  height="150">
                <img src="{0}" {1} >
                </td>
                '''.format(imgPath, size)
        style = 'vertical-align: top'
        if isSend:
            self.right(html, style=style)
        else:
            if self.chatroomFlag:
                username = content.split(':')[0]
                self.chatroom_left(html, username=username, style=style)
            self.left(html, style=style)

    def show_img(self, isSend, imgPath, content):
        'THUMBNAIL_DIRPATH://th_29cd0f0ca87652943be9ede365aabeaa'
        # imgPath = imgPath.split('th_')[1]
        imgPath = data.get_imgPath(imgPath)
        imgPath = f'./app/data/image2/{imgPath[0:2]}/{imgPath[2:4]}/{imgPath}'
        html = '''
         <td style="border: 1px #000000 solid;"  height="150">
            <a href="%s" target="_blank" height="150">
                <img herf= "baidu.com" align="right" src="%s" style="max-height:100%%" height="200">
            </a>
        </td>
        ''' % (imgPath, imgPath)
        style = 'vertical-align: top'
        if isSend:
            self.right(html, style=style)
        else:
            if self.chatroomFlag:
                username = content.split(':')[0]
                self.chatroom_left(html, username=username, style=style)
            else:
                self.left(html, style=style)

    def show_text(self, isSend, content):
        if isSend:
            html = '''
            <td style="background-color: #9EEA6A;border-radius: 40px;">&nbsp;%s&nbsp;</td>       
            ''' % content
            self.right(html)
        else:
            if self.chatroomFlag:
                # print(content)
                'wxid_mv4jjhc0w0w521:'
                username = content.split(':')[0]
                msg = ''.join(content.split(':')[1:])
                # avatar = data.get_avator(username)
                html = '''
                    <td  max-width = 300 style="background-color: #fff;border-radius: 4px;">
                    %s
                    </td>
                    ''' % (msg)
                # self.left(html, avatar=avatar)
                self.chatroom_left(html, username=username)
            else:
                html = '''
                <td max-width = 300 style="background-color: #fff;border-radius: 4px;">&nbsp;%s&nbsp;</td>
                ''' % (content)
                self.left(html)

    def hyperlink(self, url: QUrl):
        """
        超链接，点击之后放大显示图片
        :param url:
        :return:
        """
        path = data.clearImagePath(url.path())
        print(url.path(), path)
        self.imagebox = MainDemo()
        self.imagebox.show()
        self.imagebox.box.set_image(path)

    def right(self, content, style='vertical-align: middle'):
        html = '''
            <div>
            <table align="right" style="%s;">
        	<tbody>
        		<tr>
        			%s
        			<td>：</td>
        			<td style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
        			<td width="15"></td>
        		</tr>
        	</tbody>
        </table>
        </div>
        ''' % (style, content, self.Me.avatar_path)
        # print('总的HTML')
        # print(html)
        self.message.insertHtml(html)

    def left(self, content, avatar=None, style='vertical-align: middle'):
        if not avatar:
            avatar = self.ta_avatar
        if self.chatroomFlag == 5:
            try:
                username, msg = content.split('\n')
                avatar = data.get_avator(username)
                html = '''
                        <div>
                           <table align="left" style="%s;">
                            <tbody>
                                <tr>
                                    <td width="15"></td>
                                    <td rowspan="2" style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
                                    <td>：</td>
                                    <td>：</td>
                                </tr>
                                <tr>
                                    <td width="15"></td>
                                    <td>：</td>
                                    %s
                                </tr>
                            </tbody>
                        </table>
                        </div>
                        ''' % (style, avatar, msg)
            except:
                return
        else:
            html = '''
            <div>
               <table align="left" style="%s;">
                <tbody>
                    <tr>
                        <td width="15"></td>
                        <td style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
                        <td>：</td>
                        %s
                    </tr>
                </tbody>
            </table>
            </div>
            ''' % (style, avatar, content)
        self.message.insertHtml(html)

    def chatroom_left(self, content, username, style='vertical-align: middle'):
        # if username:
        avatar = data.get_avator(username)
        # conRemark = data.get_conRemark(username)
        conRemark = data.get_conRemark(username)
        html = '''
                <div>
                   <table align="left" style="%s;">
                    <tbody>
                        <tr>
                            <td width="15"></td>
                            <td rowspan="2" style="border: 1px #000000 solid"><img align="right" src="%s" width="45" height="45"/></td>
                            <td></td>
                            <td>%s</td>
                        </tr>
                        <tr>
                            <td width="15"></td>
                            <td>：</td>
                            %s
                        </tr>
                    </tbody>
                </table>
                </div>
                ''' % (style, avatar, conRemark, content)
        self.message.insertHtml(html)

    def destroy_me(self):
        """注销账户"""
        pass


class ChatMsg(QThread):
    """
    多线程显示信息
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
                                "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" "
                                "\"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                "p, li { white-space: pre-wrap; }\n"
                                "</style></head><body style=\" font-family:\'SimSun\'; font-size:15pt; "
                                "font-weight:400; font-style:normal;\">\n"
                                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; "
                                "margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br "
                                "/></p></body></html>"))

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
