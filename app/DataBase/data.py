# -*- coding: utf-8 -*-
"""
@File    : data.py
@Author  : Shuaikang Zhou
@Time    : 2023/1/5 0:11
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
import hashlib
import os
import sqlite3
import time

import requests

DB = None
cursor = None


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    if os.path.exists(path):
        return False
    os.makedirs(path)
    return True


mkdir(os.path.abspath('.') + '/app/data/emoji')
if os.path.exists('./app/DataBase/Msg.db'):
    DB = sqlite3.connect("./app/DataBase/Msg.db", check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()
if os.path.exists('./Msg.db'):
    DB = sqlite3.connect("./Msg.db")
    # '''创建游标'''
    cursor = DB.cursor()


class Me:
    """个人信息"""

    def __init__(self, username):
        self.username = username  # 自己的用户名
        self.my_avatar = get_avator(self.username)  # 自己的头像地址
        self.city = None
        self.province = None


def decrypt(db, key):
    if not key:
        print('缺少数据库密钥')
        return False
    if not db:
        print('没有数据库文件')
    if os.path.exists('./app/DataBase/Msg.db'):
        print('/app/DataBase/Msg.db  已经存在')
        return True
    cmd = '/sqlcipher-3.0.1/bin/sqlcipher-shell32.exe'
    print(os.path.abspath('.'))
    param = f"""
    PRAGMA key = '{key}';
    PRAGMA cipher_migrate;
    ATTACH DATABASE './app/DataBase/Msg.db' AS Msg KEY '';
    SELECT sqlcipher_export('Msg');
    DETACH DATABASE Msg;
        """
    with open('./app/DataBase/config.txt', 'w') as f:
        f.write(param)
    p = os.system(f"{os.path.abspath('.')}{cmd} {db} < ./app/DataBase/config.txt")
    global DB
    global cursor
    DB = sqlite3.connect("./app/DataBase/Msg.db")
    # '''创建游标'''
    cursor = DB.cursor()


def get_myinfo():
    sql = 'select * from userinfo where id=2'
    cursor.execute(sql)
    result = cursor.fetchone()
    me = Me(result[2])
    return me


def get_contacts():
    sql = 'select * from rcontact'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_rconversation():
    sql = '''
        select msgCount,username,unReadCount,chatmode,status,isSend,conversationTime,msgType,digest,digestUser,hasTrunc,attrflag
        from rconversation 
        where chatmode=1 or chatmode=0 and (msgType='1' or msgType='3' or msgType='47') 
        order by msgCount desc
    '''
    '''order by conversationTime desc'''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def timestamp2str(timestamp):
    # t2 = 1586102400
    s_l = time.localtime(timestamp / 1000)
    ts = time.strftime("%Y/%m/%d", s_l)
    # print(ts)
    return ts


def get_conRemark(username):
    sql = 'select conRemark,nickname from rcontact where username=?'
    cursor.execute(sql, [username])
    result = cursor.fetchone()
    if result[0]:
        return result[0]
    else:
        return result[1]


def avatar_md5(wxid):
    m = hashlib.md5()
    # 参数必须是byte类型，否则报Unicode-objects must be encoded before hashing错误
    m.update(bytes(wxid.encode('utf-8')))
    return m.hexdigest()


def get_avator(wxid):
    if wxid == None:
        return
    wxid = str(wxid)
    avatar = avatar_md5(wxid)
    avatar_path = r"./app/data/avatar/"
    path = avatar_path + avatar[:2] + '/' + avatar[2:4]
    for root, dirs, files in os.walk(path):
        for file in files:
            if avatar in file:
                avatar = file
                break
    return f'''{path}/{avatar}'''
    # return f'''{path}/user_{avatar}.png'''


def get_message(wxid, num):
    sql = '''
    select * from message
    where talker = ?
    order by msgId desc
    limit ?,100
    '''
    cursor.execute(sql, [wxid, num * 100])
    return cursor.fetchall()


def get_emoji(imgPath):
    newPath = f"{os.path.abspath('.')}/app/data/emoji/{imgPath}"
    if os.path.exists(newPath):
        return newPath
    else:
        sql = '''
        select cdnUrl
        from EmojiInfo 
        where md5=?
        '''
        cursor.execute(sql, [imgPath])
        result = cursor.fetchone()
        download_emoji(newPath,result[0])
    return newPath


def download_emoji(imgPath, url):
    resp = requests.get(url)
    with open(imgPath, 'wb') as f:
        f.write(resp.content)
    return imgPath


if __name__ == '__main__':
    # rconversation = get_rconversation()
    # for i in rconversation:
    #     print(i)
    timestamp2str(1632219794000)
    conremark = get_conRemark('wxid_q3ozn70pweud22')
    print(conremark)
    print(get_avator('wxid_q3ozn70pweud22'))
    me = get_myinfo()
    print(me.__dict__)
    # r = get_message('wxid_78ka0n92rzzj22', 0)
    # r.reverse()
    # for i in r:
    #     print(i)
    # print(len(r), type(r))
    print(get_emoji('f5f8a6116e177937ca9795c47f10113d'))
