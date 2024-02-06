import shutil

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QMessageBox, QAction, QLineEdit

from app.DataBase import micro_msg_db, misc_db, msg_db, close_db
from app.components import ContactQListWidgetItem, ScrollBar
from app.person import Contact, Me
from app.ui.Icon import Icon
from app.util import search
from .ai_chat import AIChat
from .chatUi import Ui_Form
from .chat_info import ChatInfo

# 美化样式表
Stylesheet = """

/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
    border:none;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 250px;
    max-width: 250px;
    min-height: 80px;
    max-height: 1200px;
    color: black;
    border:none;
}
QListWidget::item{
    height:60px;
    width:250px;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    background: rgb(230, 235, 240);
    border-left:none;
    color: black;
    font-weight: bold;
}
"""


class ChatWindow(QWidget, Ui_Form):
    load_finish_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.show_thread = None
        self.setupUi(self)
        self.ok_flag = False
        self.setStyleSheet(Stylesheet)
        self.contacts = [[], []]
        self.init_ui()
        self.show_chats()
        self.visited = set()
        self.now_index = 0

    def init_ui(self):
        search_action = QAction(self.lineEdit)
        search_action.setIcon(Icon.Search_Icon)
        self.lineEdit.addAction(search_action, QLineEdit.LeadingPosition)
        self.lineEdit.returnPressed.connect(self.search_contact)
        self.listWidget.clear()
        self.listWidget.setVerticalScrollBar(ScrollBar())
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)
        pixmap = QPixmap(Icon.Default_avatar_path).scaled(45, 45)
        contact_item = ContactQListWidgetItem('AI小助手', '', pixmap)
        self.listWidget.addItem(contact_item)
        self.listWidget.setItemWidget(contact_item, contact_item.widget)
        chat_info_window = AIChat(Me())
        self.stackedWidget.addWidget(chat_info_window)

    def show_chats(self):
        # return
        if self.ok_flag:
            return
        msg_db.init_database()
        micro_msg_db.init_database()
        if not msg_db.open_flag:
            QMessageBox.critical(self, "错误", "数据库不存在\n请先解密数据库")
            self.show_thread = ShowThread()
            self.show_thread.load_finish_signal.connect(self.load_finish_signal)
            self.show_thread.start()
            return
        self.show_thread = ShowContactThread()
        self.show_thread.showSingal.connect(self.show_chat)
        self.show_thread.load_finish_signal.connect(self.stop_loading)
        self.show_thread.start()
        self.ok_flag = True

    def search_contact(self):
        content = self.lineEdit.text()
        if not content:
            return
        index = self.search_contact_index(content)
        self.select_contact_by_index(index)

    def search_contact_index(self, content: str) -> int:
        return search.search_by_content(content, self.contacts)

    def select_contact_by_index(self, index):
        self.stackedWidget.setCurrentIndex(index)
        self.listWidget.setCurrentRow(index)

    def show_chat(self, contact):
        # return
        self.contacts[0].append(contact.remark)
        self.contacts[1].append(contact.nickName)
        contact_item = ContactQListWidgetItem(contact.remark, contact.smallHeadImgUrl, contact.smallHeadImgBLOG)
        self.listWidget.addItem(contact_item)
        self.listWidget.setItemWidget(contact_item, contact_item.widget)
        chat_info_window = ChatInfo(contact)
        self.stackedWidget.addWidget(chat_info_window)

    def setCurrentIndex(self, row):
        # print(row)
        item = self.listWidget.item(self.now_index)
        item.dis_select()
        self.stackedWidget.setCurrentIndex(row)
        item = self.listWidget.item(row)
        item.select()
        self.now_index = row
        if row not in self.visited:
            chat_info_window = self.stackedWidget.currentWidget()
            chat_info_window.update_history_messages()
            self.visited.add(row)

    def stop_loading(self, a0):
        # self.label.setVisible(False)
        self.load_finish_signal.emit(True)


class ShowContactThread(QThread):
    showSingal = pyqtSignal(Contact)
    load_finish_signal = pyqtSignal(bool)

    # heightSingal = pyqtSignal(int)
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        contact_info_lists = micro_msg_db.get_contact()
        if not contact_info_lists:
            self.load_finish_signal.emit(True)
            # QMessageBox.critical(None, "错误", "数据库错误，请重启电脑后重试")
            close_db()
            try:
                shutil.rmtree('./app/Database/Msg')
            except:
                pass
            return
        for contact_info_list in contact_info_lists:
            # UserName, Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl,bigHeadImgUrl
            contact_info = {
                'UserName': contact_info_list[0],
                'Alias': contact_info_list[1],
                'Type': contact_info_list[2],
                'Remark': contact_info_list[3],
                'NickName': contact_info_list[4],
                'smallHeadImgUrl': contact_info_list[7]
            }
            contact = Contact(contact_info)
            contact.smallHeadImgBLOG = misc_db.get_avatar_buffer(contact.wxid)
            contact.set_avatar(contact.smallHeadImgBLOG)
            self.showSingal.emit(contact)
            # pprint(contact.__dict__)
        self.load_finish_signal.emit(True)


class ShowThread(QThread):
    showSingal = pyqtSignal(Contact)
    load_finish_signal = pyqtSignal(bool)

    # heightSingal = pyqtSignal(int)
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        QThread.sleep(1)
        self.load_finish_signal.emit(True)
