from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from app.DataBase import msg
from app.components.bubble_message import BubbleMessage, ScrollBar, ScrollArea, ScrollAreaContent, ChatWidget
from app.person import MePC


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
        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.chat_window = ChatWidget()
        self.vBoxLayout.addWidget(self.chat_window)
        return

        self.scrollArea = ScrollArea()
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollBar = ScrollBar()
        self.scrollArea.setVerticalScrollBar(scrollBar)

        self.scrollAreaWidgetContents = ScrollAreaContent()
        self.scrollAreaWidgetContents.setMinimumSize(200, 400)
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
        # self.spacerItem = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.scroolAreaLayout.addItem(self.spacerItem)
        self.setLayout(self.vBoxLayout)
        self.chat_window.set_scroll_bar_last()

    def show_chat(self, message):
        try:
            type_ = message[2]
            # print(type_, type(type_))
            is_send = message[4]
            avatar = MePC().avatar if is_send else self.contact.avatar
            if type_ == 1:
                str_content = message[7]
                bubble_message = BubbleMessage(
                    str_content,
                    avatar,
                    type_,
                    is_send
                )
                # print(str_content)
                # self.scroolAreaLayout.addWidget(bubble_message)
                self.chat_window.add_message_item(bubble_message)
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
