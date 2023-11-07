import os.path

from PyQt5.QtGui import QPixmap

from app.DataBase import data


# from app.Ui.Icon import Icon


class Person:
    def __init__(self, wxid: str):
        self.wxid = wxid
        self.conRemark = data.get_conRemark(wxid)
        self.nickname, self.alias = data.get_nickname(wxid)
        self.avatar_path = data.get_avator(wxid)
        if os.path.exists(self.avatar_path):
            self.avatar = QPixmap(self.avatar_path).scaled(60, 60)
        else:
            self.avatar_path = './app/data/icons/default_avatar.svg'
            # self.avatar_path = Icon.Default_avatar_path
            self.avatar = QPixmap(self.avatar_path).scaled(60, 60)


class Me(Person):
    def __init__(self, wxid: str):
        super(Me, self).__init__(wxid)
        self.city = None
        self.province = None


class Contact(Person):
    def __init__(self, wxid: str):
        super(Contact, self).__init__(wxid)


class Group(Person):
    def __init__(self, wxid: str):
        super(Group, self).__init__(wxid)
