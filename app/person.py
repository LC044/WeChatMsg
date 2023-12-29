import os.path
import re
from typing import Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from app.ui.Icon import Icon


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
        self.smallHeadImgUrl = ''

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
        else:
            os.makedirs('./data/avatar', exist_ok=True)
            save_path = os.path.join(f'data/avatar/', self.wxid + '.png')
        self.avatar_path = save_path
        self.avatar.save(save_path)
        print('保存头像', save_path)


class ContactPC:
    def __init__(self, contact_info: Dict):
        self.wxid = contact_info.get('UserName')
        self.remark = contact_info.get('Remark')
        # Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl,bigHeadImgUrl
        self.alias = contact_info.get('Alias')
        self.nickName = contact_info.get('NickName')
        if not self.remark:
            self.remark = self.nickName
        self.remark = re.sub(r'[\/:*?"<>|\s]', '_', self.remark)
        self.smallHeadImgUrl = contact_info.get('smallHeadImgUrl')
        self.smallHeadImgBLOG = b''
        self.avatar = QPixmap()
        self.avatar_path = Icon.Default_avatar_path
        self.is_chatroom = self.wxid.__contains__('@chatroom')

    def set_avatar(self, img_bytes):
        if not img_bytes:
            self.avatar.load(Icon.Default_avatar_path)
            return
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')
        self.avatar.scaled(60, 60, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def save_avatar(self, path=None):
        if not self.avatar:
            return
        if path:
            save_path = path
        else:
            os.makedirs('./data/avatar', exist_ok=True)
            save_path = os.path.join(f'data/avatar/', self.wxid + '.png')
        self.avatar_path = save_path
        self.avatar.save(save_path)
        print('保存头像', save_path)

class ContactDefault:
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
    
    def set_avatar(self, img_bytes):
        if not img_bytes:
            self.avatar.load(Icon.Default_avatar_path)
            return
        if img_bytes[:4] == b'\x89PNG':
            self.avatar.loadFromData(img_bytes, format='PNG')
        else:
            self.avatar.loadFromData(img_bytes, format='jfif')
        self.avatar.scaled(60, 60, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def save_avatar(self, path=None):
        if not self.avatar:
            return
        if path:
            save_path = path
        else:
            os.makedirs('./data/avatar', exist_ok=True)
            save_path = os.path.join(f'data/avatar/', self.wxid + '.png')
        self.avatar_path = save_path
        self.avatar.save(save_path)
        print('保存头像', save_path)


if __name__ == '__main__':
    p1 = MePC()
    p2 = MePC()
    print(p1 == p2)
