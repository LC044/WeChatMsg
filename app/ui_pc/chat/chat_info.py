from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy

from app.DataBase import msg
from app.components.bubble_message import BubbleMessage, ScrollBar, ScrollArea, ScrollAreaContent
from .chatInfoUi import Ui_Form


class ChatInfo(QWidget, Ui_Form):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.scrollArea = None
        self.setupUi(self)
        self.contact = contact
        self.init_ui()
        self.show_chats()

    def init_ui(self):

        self.label_reamrk.setText(self.contact.remark)
        self.scrollArea = ScrollArea()

        self.verticalLayout_2.addWidget(self.scrollArea, 1)

        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollBar = ScrollBar()
        self.scrollArea.setVerticalScrollBar(scrollBar)

        self.scrollAreaWidgetContents = ScrollAreaContent()
        self.scrollAreaWidgetContents.setMinimumSize(200, 100)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.scroolAreaLayout = QVBoxLayout()
        self.scrollAreaWidgetContents.setLayout(self.scroolAreaLayout)

    def show_chats(self):
        self.show_chat_thread = ShowChatThread(self.contact)
        self.show_chat_thread.showSingal.connect(self.show_chat)
        self.show_chat_thread.finishSingal.connect(self.show_finish)
        self.show_chat_thread.start()

    def show_finish(self, ok):
        self.spacerItem = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scroolAreaLayout.addItem(self.spacerItem)

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
