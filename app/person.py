import app.DataBase.data as data


class Person:
    def __init__(self, wxid: str):
        self.wxid = wxid
        self.username = data.get_conRemark(wxid)
        self.avatar_path = data.get_avator(wxid)
