from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

from app.person import Contact
from app.util.region_conversion import conversion_region_to_chinese
from .userinfoUi import Ui_Frame
from ...Icon import Icon


class UserinfoController(QWidget, Ui_Frame):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.l_remark.setText(contact.remark)
        self.l_avatar.setPixmap(contact.avatar)
        self.l_nickname.setText(f'昵称：{contact.nickName}')
        self.l_username.setText(f'微信号：{contact.alias}')
        self.lineEdit.setText(contact.remark)
        # self.l_region.setVisible(False)
        self.l_contact_label.setText(contact.label_name)
        if contact.detail:
            self.l_signature.setText(contact.detail.get('signature'))
            self.l_tel.setText(contact.detail.get('telephone'))
            region = contact.detail.get('region')
            area = conversion_region_to_chinese(region)
            self.l_region.setText(f'地区：{area}')
            gender_code = contact.detail.get('gender')
            gender = ''
            pixmap =QPixmap()
            if gender_code == 1:
                gender = '男'
                pixmap = QPixmap(Icon.Man_Icon_path)
            elif gender_code == 2:
                gender = '女'
                pixmap = QPixmap(Icon.Woman_Icon_path)
            self.l_gender.setPixmap(pixmap)
            # self.l_gender.setText()
    def set_contact(self,contact:Contact):
        self.l_remark.setText(contact.remark)
        self.l_avatar.setPixmap(contact.avatar)
        self.l_nickname.setText(f'昵称：{contact.nickName}')
        self.l_username.setText(f'微信号：{contact.alias}')
        self.lineEdit.setText(contact.remark)
        # self.l_region.setVisible(False)
        self.l_contact_label.setText(contact.label_name)
        if contact.detail:
            self.l_signature.setText(contact.detail.get('signature'))
            self.l_tel.setText(contact.detail.get('telephone'))
            region = contact.detail.get('region')
            area = conversion_region_to_chinese(region)
            self.l_region.setText(f'地区：{area}')
            gender_code = contact.detail.get('gender')
            gender = ''
            pixmap = QPixmap()
            if gender_code == 1:
                gender = '男'
                pixmap = QPixmap(Icon.Man_Icon_path)
            elif gender_code == 2:
                gender = '女'
                pixmap = QPixmap(Icon.Woman_Icon_path)
            self.l_gender.setPixmap(pixmap)
            # self.l_gender.setText()