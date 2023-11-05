from PyQt5.QtWidgets import *

from app.person import Contact
from .userinfoUi import Ui_Frame


class UserinfoController(QWidget, Ui_Frame):
    def __init__(self, contact: Contact, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.l_remark.setText(contact.conRemark)
        self.l_avatar.setPixmap(contact.avatar)
        self.l_nickname.setText(f'昵称：{contact.nickname}')
        self.l_username.setText(f'微信号：{contact.alias}')
        self.lineEdit.setText(contact.conRemark)
        self.progressBar.setVisible(False)
