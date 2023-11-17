from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QHBoxLayout

from app.DataBase import msg
from app.components.bubble_message import BubbleMessage, ScrollBar, ScrollArea, ScrollAreaContent


class ChatInfo(QWidget):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.contact = contact

        self.init_ui()
        self.show_chats()

    def init_ui(self):
        self.label_reamrk = QLabel(self.contact.remark)

        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(self.label_reamrk)

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setSpacing(0)
        # self.vBoxLayout.addLayout(self.hBoxLayout)

        self.scrollArea = ScrollArea()
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollBar = ScrollBar()
        self.scrollArea.setVerticalScrollBar(scrollBar)

        self.scrollAreaWidgetContents = ScrollAreaContent()
        self.scrollAreaWidgetContents.setMinimumSize(200, 10000)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.vBoxLayout.addWidget(self.scrollArea)
        self.scroolAreaLayout = QVBoxLayout()
        self.scroolAreaLayout.setSpacing(0)
        self.scrollAreaWidgetContents.setLayout(self.scroolAreaLayout)

    def show_chats(self):
        self.show_chat_thread = ShowChatThread(self.contact)
        self.show_chat_thread.showSingal.connect(self.show_chat)
        self.show_chat_thread.finishSingal.connect(self.show_finish)
        self.show_chat_thread.start()

    def show_finish(self, ok):
        self.spacerItem = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scroolAreaLayout.addItem(self.spacerItem)
        self.setLayout(self.vBoxLayout)

    def show_chat(self, message):
        try:
            type_ = message[2]
            # print(type_, type(type_))
            if type_ == 1:
                str_content = message[7]
                is_send = message[4]
                bubble_message = BubbleMessage(
                    str_content,
                    self.contact.avatar,
                    type_,
                    is_send
                )
                # print(str_content)
                self.scroolAreaLayout.addWidget(bubble_message)
        except:
            print(message)


class ShowChatThread(QThread):
    showSingal = pyqtSignal(tuple)
    finishSingal = pyqtSignal(int)

    # heightSingal = pyqtSignal(int)
    def __init__(self, contact):
        super().__init__()
        self.wxid = contact.wxid

    def run(self) -> None:
        messages = msg.get_message_by_num(self.wxid, 0)
        for message in messages:
            self.showSingal.emit(message)
        self.finishSingal.emit(1)
