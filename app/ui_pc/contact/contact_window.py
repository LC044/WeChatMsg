from PyQt5.QtWidgets import QWidget, QMessageBox

from app.DataBase import micro_msg, misc
from app.components import ContactQListWidgetItem
from app.person import ContactPC
from .contactUi import Ui_Form

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


class ContactWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setStyleSheet(Stylesheet)
        self.init_ui()
        self.show_contacts()

    def init_ui(self):
        self.listWidget.clear()
        self.listWidget.currentRowChanged.connect(self.setCurrentIndex)
        self.listWidget.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)

    def show_contacts(self):
        if not micro_msg.is_database_exist():
            QMessageBox.critical(self, "错误", "数据库不存在\n请先解密数据库")
            return
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
            # pprint(contact.__dict__)
            contact_item = ContactQListWidgetItem(contact.nickName, contact.smallHeadImgUrl, contact.smallHeadImgBLOG)
            self.listWidget.addItem(contact_item)
            self.listWidget.setItemWidget(contact_item, contact_item.widget)

    def setCurrentIndex(self, row):
        print(row)
        self.stackedWidget.setCurrentIndex(row)
