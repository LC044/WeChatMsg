"""
定义各种联系人
"""

import os.path
import re
from typing import Dict
from PyQt5.QtGui import QPixmap
from app.ui.Icon import Icon


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


class Person:
    def __init__(self):
        self.avatar_path = None
        self.avatar = None
        self.avatar_path_qt = Icon.Default_avatar_path

    def set_avatar(self, img_bytes):
        if not img_bytes:
            self.avatar.load(Icon.Default_avatar_path)
            return
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')

    def save_avatar(self, path=None):
        if not self.avatar:
            return
        if path:
            save_path = path
            if os.path.exists(save_path):
                self.avatar_path = save_path
                return save_path
        else:
            os.makedirs('./data/avatar', exist_ok=True)
            save_path = os.path.join(f'data/avatar/', self.wxid + '.png')
        self.avatar_path = save_path
        if not os.path.exists(save_path):
            self.avatar.save(save_path)
            print('保存头像', save_path)


@singleton
class Me(Person):
    def __init__(self):
        self.avatar = QPixmap(Icon.Default_avatar_path)
        self.avatar_path = ':/icons/icons/default_avatar.svg'
        self.wxid = ''
        self.wx_dir = ''
        self.name = ''
        self.mobile = ''
        self.smallHeadImgUrl = ''
        self.nickName = self.name
        self.remark = self.nickName


class Contact(Person):
    def __init__(self, contact_info: Dict):
        self.wxid = contact_info.get('UserName')
        self.remark = contact_info.get('Remark')
        # Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl,bigHeadImgUrl
        self.alias = contact_info.get('Alias')
        self.nickName = contact_info.get('NickName')
        if not self.remark:
            self.remark = self.nickName
        self.remark = re.sub(r'[\\/:*?"<>|\s\.]', '_', self.remark)
        self.smallHeadImgUrl = contact_info.get('smallHeadImgUrl')
        self.smallHeadImgBLOG = b''
        self.avatar = QPixmap()
        self.avatar_path = Icon.Default_avatar_path
        self.is_chatroom = self.wxid.__contains__('@chatroom')
        self.detail = contact_info.get('detail')
        self.label_name = contact_info.get('label_name')  # 联系人的标签分类

        """
        detail存储了联系人的详细信息，是个字典
        {
            'region': tuple[国家,省份,市], # 地区三元组
            'signature': str, # 个性签名
            'telephone': str, # 电话号码，自己写的备注才会显示
            'gender': int, # 性别 0：未知，1：男，2：女
        }
        """


class ContactDefault(Person):
    def __init__(self, wxid=""):
        self.avatar = QPixmap(Icon.Default_avatar_path)
        self.avatar_path = ':/icons/icons/default_avatar.svg'
        self.wxid = wxid
        self.remark = wxid
        self.alias = wxid
        self.nickName = wxid
        self.smallHeadImgUrl = ""
        self.smallHeadImgBLOG = b''
        self.is_chatroom = False


class Contacts:
    def __init__(self):
        self.contacts: Dict[str:Contact] = {}

    def add(self, wxid, contact: Contact):
        if wxid not in contact:
            self.contacts[wxid] = contact

    def get(self, wxid: str) -> Contact:
        return self.contacts.get(wxid)

    def remove(self, wxid: str):
        return self.contacts.pop(wxid)

    def save_avatar(self, avatar_dir: str = './data/avatar/'):
        for wxid, contact in self.contacts.items():
            avatar_path = os.path.join(avatar_dir, wxid + '.png')
            if os.path.exists(avatar_path):
                continue
            contact.save_avatar(avatar_path)


if __name__ == '__main__':
    p1 = Me()
    p2 = Me()
    print(p1 == p2)
