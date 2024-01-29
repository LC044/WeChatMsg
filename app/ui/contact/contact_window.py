from typing import List

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox, QAction, QLineEdit, QLabel

from app.DataBase import micro_msg_db, misc_db, close_db
from app.components import ContactQListWidgetItem, ScrollBar
from app.person import Contact
from app.ui.Icon import Icon
from .contactInfo import ContactInfo
from .contactUi import Ui_Form
from ...DataBase.hard_link import decodeExtraBuf
from ...util import search

# 美化样式表
Stylesheet = """
QPushButton{
    background-color: transparent;
}
QPushButton:hover { 
    background-color: lightgray;
}
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
/*鼠标悬停颜色*/
HistoryPanel::item:hover {
    background: rgb(52, 52, 52);
}
"""


class ContactWindow(QWidget, Ui_Form):
    load_finish_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.now_index = 0
        self.show_thread = None
        self.setupUi(self)
        self.ok_flag = False
        self.setStyleSheet(Stylesheet)
        self.init_ui()
        self.contacts = [[], []]
        self.contacts_list:List[Contact] = []
        self.show_contacts()
        self.contact_info_window = None

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

    def show_contacts(self):
        """
        创建一个子线程来获取联系人并通过信号传递联系人信息
        @return:
        """
        # return
        if self.ok_flag:
            return
        micro_msg_db.init_database()
        if not micro_msg_db.open_flag:
            QMessageBox.critical(self, "错误", "数据库不存在\n请先解密数据库")
            self.show_thread = ShowThread()
            self.show_thread.showSingal.connect(self.show_contact)
            self.show_thread.load_finish_signal.connect(self.load_finish_signal)
            self.show_thread.start()
            return

        self.show_thread = ShowContactThread()
        self.show_thread.showSingal.connect(self.show_contact)
        self.show_thread.load_finish_signal.connect(self.load_finish_signal)
        self.show_thread.start()
        self.ok_flag = True

    def search_contact(self):
        """
        搜索联系人
        @return:
        """
        keyword = self.lineEdit.text()
        if keyword:
            index = search.search_by_content(keyword, self.contacts)
            self.listWidget.setCurrentRow(index)
            self.stackedWidget.setCurrentIndex(index)

    def show_contact(self, contact: Contact):
        """
        显示联系人
        @param contact:联系人对象
        @return:
        """
        # return
        self.contacts[0].append(contact.remark)
        self.contacts[1].append(contact.nickName)
        contact_item = ContactQListWidgetItem(contact.remark, contact.smallHeadImgUrl, contact.smallHeadImgBLOG)
        self.listWidget.addItem(contact_item)
        self.listWidget.setItemWidget(contact_item, contact_item.widget)
        self.contacts_list.append(contact)
        if self.contact_info_window is None:
            self.contact_info_window = ContactInfo(contact)
            self.stackedWidget.addWidget(self.contact_info_window)

    def setCurrentIndex(self, row):
        # print(row)
        item = self.listWidget.item(self.now_index)
        item.dis_select()
        self.stackedWidget.setCurrentIndex(row)
        item = self.listWidget.item(row)
        item.select()
        self.now_index = row
        # self.stackedWidget.setCurrentIndex(row)
        self.contact_info_window.set_contact(self.contacts_list[row])


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
            import shutil
            try:
                shutil.rmtree('./app/Database/Msg')
            except:
                pass
            return
        for contact_info_list in contact_info_lists:
            # UserName, Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl,bigHeadImgUrl,ExtraBuf
            detail = decodeExtraBuf(contact_info_list[9])
            contact_info = {
                'UserName': contact_info_list[0],
                'Alias': contact_info_list[1],
                'Type': contact_info_list[2],
                'Remark': contact_info_list[3],
                'NickName': contact_info_list[4],
                'smallHeadImgUrl': contact_info_list[7],
                'detail': detail,
                'label_name': contact_info_list[10],
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
