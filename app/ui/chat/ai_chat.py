import sys
import time
import traceback

from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication, QTextBrowser

from app.ui.Icon import Icon

try:
    from .chatInfoUi import Ui_Form
except:
    from chatInfoUi import Ui_Form
from app.DataBase import msg_db, hard_link_db
from app.components.bubble_message import BubbleMessage, ChatWidget, Notice
from app.person import Me, Contact, ContactDefault


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
        self.now_message :Message= None
        self.setupUi(self)
        self.last_timestamp = 0
        self.last_str_time = ''
        self.last_pos = 0
        self.contact = contact
        self.init_ui()
        self.show_chats()
        self.pushButton.clicked.connect(self.send_msg)

    def init_ui(self):
        self.textEdit.installEventFilter(self)

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

    def show_chats(self):
        # return
        self.show_chat_thread = AIChatThread()
        self.show_chat_thread.msgSignal.connect(self.chat)

    def update_history_messages(self):
        print('开始发送信息')
        message1 = Message(False)
        msg = '您好！我是MemoTrace小助手，您可以问我一些问题。'
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

    def run(self) -> None:
        for s in self.msg:
            self.msgSignal.emit(s)
            time.sleep(0.02)
        self.finishSingal.emit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    contact = ContactDefault('1')
    dialog = AIChat(contact)
    dialog.show()
    sys.exit(app.exec_())
