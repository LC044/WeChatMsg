# -*- coding: utf-8 -*-
"""
@File    : myinfo.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/23 11:45
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .myinfoUi import *
from ....DB import data


class InfoControl(QWidget, Ui_Frame):
    backSignal = pyqtSignal(str)

    # createSignal = pyqtSignal(Group)
    def __init__(self, parent=None, Me=None):
        super(InfoControl, self).__init__(parent)
        self.setupUi(self)
        self.Me = Me
        self.initUi()
        self.btn_update.clicked.connect(self.update_)

    def initUi(self):
        self.ltips.setText('')
        self.info = data.get_myinfo(self.Me.username)
        nickname = self.info[1]
        gender = self.info[2]
        city = self.info[4]
        province = self.info[5]
        tel = self.info[6]
        email = self.info[7]
        signsture = self.info[8]
        pixmap = QPixmap(self.Me.my_avatar).scaled(80, 80)  # 按指定路径找到图片
        self.l_avatar.setPixmap(pixmap)  # 在label上显示图片
        self.l_username.setText(f'账号：{self.Me.username}')
        if gender=='男':
            self.radioButton.setChecked(True)
        elif gender=='女':
            self.radioButton_2.setChecked(True)
        self.line_nickname.setText(nickname)
        self.line_city.setText(city)
        self.line_tel.setText(tel)
        self.line_province.setText(province)
        self.line_email.setText(email)
        self.line_signsture.setText(signsture)
    def update_(self):
        """更新信息"""
        nickname = self.line_nickname.text()
        if self.radioButton.isChecked():
            gender = self.radioButton.text()
        else:
            gender = '女'
        city = self.line_city.text()
        province = self.line_province.text()
        tel = self.line_tel.text()
        email = self.line_email.text()
        signsture = self.line_signsture.text()
        userinfo = [
            nickname,gender,city,province,tel,email,signsture,self.Me.username
        ]
        data.update_userinfo(userinfo)
        self.ltips.setText('修改成功')
