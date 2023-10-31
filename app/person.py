from PyQt5.QtGui import QPixmap

import app.DataBase.data as data


class Person:
    def __init__(self, wxid: str):
        self.wxid = wxid
        self.conRemark = data.get_conRemark(wxid)
        self.nickname, self.alias = data.get_nickname(wxid)
        self.avatar_path = data.get_avator(wxid)
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
