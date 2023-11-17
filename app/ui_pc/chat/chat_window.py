from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox, QAction, QLineEdit

from app.DataBase import micro_msg, misc
from app.components import ContactQListWidgetItem
from app.person import ContactPC
from .chatUi import Ui_Form
from .chat_info import ChatInfo
from ..Icon import Icon

# 美化样式表
Stylesheet = """

/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
    border:none;
    background-color:rgb(240,240,240)
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
    background: rgb(204, 204, 204);
    border-bottom: 2px solid rgb(9, 187, 7);
    border-left:none;
    color: black;
    font-weight: bold;
}
/*鼠标悬停颜色*/
HistoryPanel::item:hover {
    background: rgb(52, 52, 52);
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
        self.init_ui()
        self.show_chats()

    def init_ui(self):

        search_action = QAction(self.lineEdit)
        search_action.setIcon(Icon.Search_Icon)
        self.lineEdit.addAction(search_action, QLineEdit.LeadingPosition)
        self.listWidget.clear()
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)

    def show_chats(self):
        print('chat0')
        if self.ok_flag:
            return
        micro_msg.init_database()
        if not micro_msg.is_database_exist():
            QMessageBox.critical(self, "错误", "数据库不存在\n请先解密数据库")
            return
        self.show_thread = ShowContactThread()
        self.show_thread.showSingal.connect(self.show_chat)
        self.show_thread.load_finish_signal.connect(self.stop_loading)
        self.show_thread.start()
        self.ok_flag = True

    def show_chat(self, contact):
        contact_item = ContactQListWidgetItem(contact.nickName, contact.smallHeadImgUrl, contact.smallHeadImgBLOG)
        self.listWidget.addItem(contact_item)
        self.listWidget.setItemWidget(contact_item, contact_item.widget)
        chat_info_window = ChatInfo(contact)
        self.stackedWidget.addWidget(chat_info_window)

    def setCurrentIndex(self, row):
        print(row)
        self.stackedWidget.setCurrentIndex(row)

    def stop_loading(self, a0):
        # self.label.setVisible(False)
        self.load_finish_signal.emit(True)


class ShowContactThread(QThread):
    showSingal = pyqtSignal(ContactPC)
    load_finish_signal = pyqtSignal(bool)

    # heightSingal = pyqtSignal(int)
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        contact_info_lists = micro_msg.get_contact()
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
            contact = ContactPC(contact_info)
            contact.smallHeadImgBLOG = misc.get_avatar_buffer(contact.wxid)
            contact.set_avatar(contact.smallHeadImgBLOG)
            self.showSingal.emit(contact)
            # pprint(contact.__dict__)
        self.load_finish_signal.emit(True)
