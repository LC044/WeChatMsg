import traceback

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from app.DataBase import msg_db, hard_link_db
from app.components.bubble_message import BubbleMessage, ChatWidget, Notice
from app.person import Me
from app.util import get_abs_path
from app.util.emoji import get_emoji


class ChatInfo(QWidget):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.last_timestamp = 0
        self.last_str_time = ''
        self.last_pos = 0
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
        self.chat_window.scrollArea.verticalScrollBar().valueChanged.connect(self.verticalScrollBar)
        self.vBoxLayout.addWidget(self.chat_window)
        self.setLayout(self.vBoxLayout)

    def show_chats(self):
        # Me().save_avatar()
        # self.contact.save_avatar()
        self.show_chat_thread = ShowChatThread(self.contact)
        self.show_chat_thread.showSingal.connect(self.add_message)
        self.show_chat_thread.finishSingal.connect(self.show_finish)
        # self.show_chat_thread.start()

    def show_finish(self, ok):
        self.setScrollBarPos()
        self.show_chat_thread.quit()

    def verticalScrollBar(self, pos):
        """
        滚动条到0之后自动更新聊天记录
        :param pos:
        :return:
        """
        # print(pos)
        if pos > 0:
            return

        # 记录当前滚动条最大值
        self.last_pos = self.chat_window.verticalScrollBar().maximum()
        self.update_history_messages()

    def update_history_messages(self):
        self.show_chat_thread.start()

    def setScrollBarPos(self):
        """
        将滚动条位置设置为上次看到的地方
        :param pos:
        :return:
        """
        self.chat_window.update()
        self.chat_window.show()
        pos = self.chat_window.verticalScrollBar().maximum() - self.last_pos
        self.chat_window.set_scroll_bar_value(pos)

    def is_5_min(self, timestamp):
        if abs(timestamp - self.last_timestamp) > 300:
            self.last_timestamp = timestamp
            return True
        return False

    def get_avatar_path(self, is_send, message, is_absolute_path=False) -> str:
        if self.contact.is_chatroom:
            avatar = message[13].smallHeadImgUrl
        else:
            avatar = Me().smallHeadImgUrl if is_send else self.contact.smallHeadImgUrl
        if is_absolute_path:
            if self.contact.is_chatroom:
                # message[13].save_avatar()
                avatar = message[13].avatar
            else:
                avatar = Me().avatar if is_send else self.contact.avatar
        return avatar

    def get_display_name(self, is_send, message) -> str:
        if self.contact.is_chatroom:
            if is_send:
                display_name = Me().name
            else:
                display_name = message[13].remark
        else:
            display_name = None
        return display_name

    def add_message(self, message):
        try:
            type_ = message[2]
            str_content = message[7]
            str_time = message[8]
            # print(type_, type(type_))
            is_send = message[4]
            avatar = self.get_avatar_path(is_send, message,True)
            display_name = self.get_display_name(is_send, message)
            timestamp = message[5]
            BytesExtra = message[10]
            if type_ == 1:
                if self.is_5_min(timestamp):
                    time_message = Notice(self.last_str_time)
                    self.last_str_time = str_time
                    self.chat_window.add_message_item(time_message, 0)
                bubble_message = BubbleMessage(
                    str_content,
                    avatar,
                    type_,
                    is_send,
                    display_name=display_name
                )
                self.chat_window.add_message_item(bubble_message, 0)
            elif type_ == 3:
                # return
                if self.is_5_min(timestamp):
                    time_message = Notice(self.last_str_time)
                    self.last_str_time = str_time
                    self.chat_window.add_message_item(time_message, 0)
                image_path = hard_link_db.get_image(content=str_content, bytesExtra=BytesExtra, up_dir=Me().wx_dir,thumb=False)
                image_path = get_abs_path(image_path)
                bubble_message = BubbleMessage(
                    image_path,
                    avatar,
                    type_,
                    is_send
                )
                self.chat_window.add_message_item(bubble_message, 0)
            elif type_ == 47:
                return
                if self.is_5_min(timestamp):
                    time_message = Notice(self.last_str_time)
                    self.last_str_time = str_time
                    self.chat_window.add_message_item(time_message, 0)
                image_path = get_emoji(str_content, thumb=True)
                bubble_message = BubbleMessage(
                    image_path,
                    avatar,
                    3,
                    is_send
                )
                self.chat_window.add_message_item(bubble_message, 0)
            elif type_ == 10000:
                str_content = str_content.lstrip('<revokemsg>').rstrip('</revokemsg>')
                message = Notice(str_content)
                self.chat_window.add_message_item(message, 0)
        except:
            print(message)
            traceback.print_exc()



class ShowChatThread(QThread):
    showSingal = pyqtSignal(tuple)
    finishSingal = pyqtSignal(int)
    msg_id = 0

    # heightSingal = pyqtSignal(int)
    def __init__(self, contact):
        super().__init__()
        self.last_message_id = 9999999999
        self.wxid = contact.wxid

    def run(self) -> None:
        messages = msg_db.get_message_by_num(self.wxid, self.last_message_id)
        if messages:
            self.last_message_id = messages[-1][0]
        for message in messages:
            self.showSingal.emit(message)
        self.msg_id += 1
        self.finishSingal.emit(1)
