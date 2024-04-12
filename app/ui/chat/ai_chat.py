import json
import sys
import time
import traceback
from urllib.parse import urljoin

import requests
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication, QTextBrowser, QMessageBox

from app import config
from app.config import SERVER_API_URL
from app.log import logger
from app.ui.Icon import Icon

try:
    from .chatInfoUi import Ui_Form
except:
    from chatInfoUi import Ui_Form
from app.components.bubble_message import BubbleMessage
from app.person import Me, ContactDefault


class Message(QWidget):
    def __init__(self, is_send=False, text='', parent=None):
        super().__init__(parent)
        self.avatar = QLabel(self)

        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setText(text)

        layout = QHBoxLayout(self)
        if is_send:
            pixmap = Me().avatar.scaled(45, 45)
            self.textBrowser.setLayoutDirection(Qt.RightToLeft)
            self.textBrowser.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.avatar.setPixmap(pixmap)
            layout.addWidget(self.textBrowser)
            layout.addWidget(self.avatar)
        else:
            pixmap = QPixmap(Icon.Default_avatar_path).scaled(45, 45)
            self.avatar.setPixmap(pixmap)
            layout.addWidget(self.avatar)
            layout.addWidget(self.textBrowser)
        # self.textBrowser.setFixedHeight(int(self.textBrowser.document().size().height()))
        self.textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.avatar.setFixedSize(QSize(60, 60))

    def append(self, text: str):
        self.textBrowser.insertPlainText(text)
        self.textBrowser.setFixedHeight(int(self.textBrowser.document().size().height()))


class AIChat(QWidget, Ui_Form):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.now_message: Message = None
        self.setupUi(self)
        self.last_timestamp = 0
        self.last_str_time = ''
        self.last_pos = 0
        self.contact = contact
        self.init_ui()
        self.show_chats()
        self.pushButton.clicked.connect(self.send_msg)
        self.toolButton.clicked.connect(self.tool)
        self.btn_clear.clicked.connect(self.clear_dialog)
        self.btn_clear.setIcon(Icon.Clear_Icon)

    def init_ui(self):
        self.textEdit.installEventFilter(self)

    def tool(self):
        QMessageBox.information(self, "温馨提示", "暂未接入聊天数据，您可进行基础的AI对话，后续更新敬请期待")

    def chat(self, text):
        self.now_message.append(text)
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())

    def send_msg(self):
        msg = self.textEdit.toPlainText().strip()
        self.textEdit.setText('')
        if not msg:
            return
        print(msg)
        bubble_message = BubbleMessage(
            msg,
            Me().avatar,
            1,
            True,
        )
        self.verticalLayout_message.addWidget(bubble_message)
        message1 = Message(False)
        self.verticalLayout_message.addWidget(message1)
        self.show_chat_thread.msg = msg
        self.now_message = message1
        self.show_chat_thread.start()
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())

    def clear_dialog(self):
        self.show_chat_thread.history = []
        while self.verticalLayout_message.count():
            item = self.verticalLayout_message.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                del item

    def show_chats(self):
        # return
        self.show_chat_thread = AIChatThread()
        self.show_chat_thread.msgSignal.connect(self.chat)

    def update_history_messages(self):
        print('开始发送信息')
        message1 = Message(False)
        msg = '你好！'
        self.verticalLayout_message.addWidget(message1)
        self.show_chat_thread.msg = msg
        self.now_message = message1
        self.show_chat_thread.start()

    def add_message(self, message):
        print('message', message)
        # self.textBrowser.append(message)
        self.textBrowser.insertPlainText(message)
        self.textBrowser.setFixedHeight(int(self.textBrowser.document().size().height()))

    def eventFilter(self, obj, event):
        if obj == self.textEdit and event.type() == event.KeyPress:
            key = event.key()
            if key == 16777220:  # 回车键的键值
                self.send_msg()
                self.textEdit.setText('')
                return True
        return super().eventFilter(obj, event)


class AIChatThread(QThread):
    msgSignal = pyqtSignal(str)
    showSingal = pyqtSignal(tuple)
    finishSingal = pyqtSignal(int)
    msg_id = 0

    # heightSingal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.msg = ''
        self.history = []

    def run(self) -> None:
        url = urljoin(SERVER_API_URL, 'chat')
        data = {
            'username': Me().wxid,
            'token': Me().token,
            'version': config.version,
            'messages': [
                *self.history,
                {
                    'role': 'user',
                    "content": self.msg
                }
            ]
        }
        message = '''
        幼儿园三班一共有35人，上个月34人满勤。\n其中1月15日，小明同学感冒了，他的妈妈给他请了一天的病假。
        '''
        try:
            # for s in message:
            #     self.msgSignal.emit(s)
            #     time.sleep(0.05)
            # return
            resp = requests.post(url, json=data, stream=True)
            message = {
                'role': 'user',
                'content': self.msg
            }
            resp_message = {
                'role': 'assistant',
                'content': ''
            }
            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if line:
                        trunk = line.decode('utf-8')
                        try:
                            data = json.loads(trunk.strip('data: '))
                            answer = data.get('answer')
                            print(answer)
                            if isinstance(answer, str):
                                resp_message['content'] += answer
                                self.msgSignal.emit(answer)
                        except:
                            print(trunk)
                            resp_message['content'] += trunk
                            self.msgSignal.emit(trunk)
            else:
                print(resp.text)
                error = resp.json().get('error')
                logger.error(f'ai请求错误:{error}')
                self.msgSignal.emit(error)
            self.history.append(message)
            self.history.append(resp_message)
        except Exception as e:
            error = str(e)
            logger.error(f'ai请求错误:{error}{traceback.format_exc()}')
            self.msgSignal.emit(error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    contact = ContactDefault('1')
    dialog = AIChat(contact)
    dialog.show()
    sys.exit(app.exec_())
