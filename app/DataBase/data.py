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


def get_nickname(username):
    sql = 'select nickname,alias from rcontact where username=?'
    cursor.execute(sql, [username])
    result = cursor.fetchone()
    return result


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


def search_send_message(start_time, end_time):
    start_time = '2022-1-1 00:00:00'
    end_time = '2023-1-1 00:00:00'
    start = time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
    end = time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
    sql = '''
        select count(*) from message
        where  createTime >? and createTime < ? and isSend=0 and talker like '%wxid%';
    '''
    cursor.execute(sql,[start*1000 , end*1000])
    return cursor.fetchone()


def clearImagePath(imgpath):
    path = imgpath.split('/')
    newPath = '/'.join(path[:-1]) + '/' + path[-1][3:] + '.jpg'
    if os.path.exists(newPath):
        return newPath
    newPath = '/'.join(path[:-1]) + '/' + path[-1][3:] + '.png'
    if os.path.exists(newPath):
        return newPath
    newPath = '/'.join(path[:-1]) + '/' + path[-1] + 'hd'
    if os.path.exists(newPath):
        return newPath
    return imgpath


def get_all_message(wxid):
    sql = '''
        select * from message
        where talker = ?
        order by msgId 
        '''
    cursor.execute(sql, [wxid])
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
        download_emoji(newPath, result[0])
    return newPath


def download_emoji(imgPath, url):
    resp = requests.get(url)
    with open(imgPath, 'wb') as f:
        f.write(resp.content)
    return imgPath


def get_chatroom_displayname(chatroom, username):
    sql = 'select memberlist,displayname from chatroom where chatroomname =?'
    cursor.execute(sql, [chatroom])
    result = cursor.fetchone()
    wxids = result[0].split(';')
    names = result[1].split('、')
    id = wxids.index(username)
    print(result[0])
    print(wxids)
    for i in wxids:
        print(get_conRemark(i))
    return names[id]


def get_contacts():
    sql = '''
        select * from rcontact
        where type=3 or type = 333
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


if __name__ == '__main__':
    # rconversation = get_rconversation()
    # for i in rconversation:
    #     print(i)
    # contacts = get_all_message('wxid_vqave8lcp49r22')
    # for contact in contacts:
    #     print(contact)
    # [(177325,)] (73546,) (103770,)
    print(search_send_message(1,1))
