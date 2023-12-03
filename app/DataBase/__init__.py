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
# from . import data
# from . import output
from .misc import Misc
from .msg import Msg
from .msg import MsgType
misc_db = Misc()
msg_db = Msg()
micro_msg_db = MicroMsg()
hard_link_db = HardLink()
__all__ = ["data", 'output', 'misc_db', 'micro_msg_db', 'msg_db', 'hard_link_db','MsgType']
