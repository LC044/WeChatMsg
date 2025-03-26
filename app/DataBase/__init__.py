# -*- coding: utf-8 -*-
"""
@File    : __init__.py.py
@Author  : Shuaikang Zhou
@Time    : 2023/1/5 0:10
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
from .hard_link import HardLink
from .micro_msg import MicroMsg
from .media_msg import MediaMsg
from .misc import Misc
from .msg import Msg
from .msg import MsgType
from .db_pool import db_pool, close_db_pool

misc_db = Misc()
msg_db = Msg()
micro_msg_db = MicroMsg()
hard_link_db = HardLink()
media_msg_db = MediaMsg()


def close_db():
    """关闭所有数据库连接"""
    misc_db.close()
    msg_db.close()
    micro_msg_db.close()
    hard_link_db.close()
    media_msg_db.close()
    # 关闭数据库连接池
    close_db_pool()


def init_db():
    """初始化所有数据库连接"""
    misc_db.init_database()
    msg_db.init_database()
    micro_msg_db.init_database()
    hard_link_db.init_database()
    media_msg_db.init_database()


__all__ = ['misc_db', 'micro_msg_db', 'msg_db', 'hard_link_db', 'MsgType', "media_msg_db", "close_db", "db_pool"]
