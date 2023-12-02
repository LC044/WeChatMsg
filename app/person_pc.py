from typing import Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from app.ui_pc.Icon import Icon


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class MePC:
    def __init__(self):
        self.avatar = QPixmap(Icon.Default_avatar_path)
        self.avatar_path = ':/icons/icons/default_avatar.svg'
        self.wxid = ''
        self.wx_dir = ''
        self.name = ''
        self.mobile = ''

    def set_avatar(self, img_bytes):
        if not img_bytes:
            self.avatar.load(Icon.Default_avatar_path)
            return
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')


class ContactPC:
    def __init__(self, contact_info: Dict):
        self.wxid = contact_info.get('UserName')
        self.remark = contact_info.get('Remark')
        # Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl,bigHeadImgUrl
        self.alias = contact_info.get('Alias')
        self.nickName = contact_info.get('NickName')
        if not self.remark:
            self.remark = self.nickName
        self.smallHeadImgUrl = contact_info.get('smallHeadImgUrl')
        self.smallHeadImgBLOG = b''
        self.avatar = QPixmap()
        self.avatar_path = Icon.Default_avatar_path

    def set_avatar(self, img_bytes):
        if not img_bytes:
            self.avatar.load(Icon.Default_avatar_path)
            return
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')
        self.avatar.scaled(60, 60, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


if __name__ == '__main__':
    p1 = MePC()
    p2 = MePC()
    print(p1 == p2)
