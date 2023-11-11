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
import threading
import time

import requests

DB = None
cursor = None
lock = threading.Lock()
Type = {
    1: '文本内容',
    2: '位置信息',
    3: '图片及视频',
    34: '语音消息',
    42: '名片（公众号名片）',
    43: '图片及视频',
    47: '表情包',
    48: '定位信息',
    49: '小程序链接',
    10000: '撤回消息提醒',
    1048625: '照片',
    16777265: '链接',
    285212721: '文件',
    419430449: '微信转账',
    436207665: '微信红包',
    469762097: '微信红包',
    11879048186: '位置共享',
}

Type0 = {
    '1': '文字',
    '3': '图片',
    '43': '视频',
    '-1879048185': '微信运动排行榜',
    '5': '',
    '47': '表情包',
    '268445456': '撤回的消息',
    '34': '语音',
    '419430449': '转账',
    '50': '语音电话',
    '100001': '领取红包',
    '10000': '消息已发出，但被对方拒收了。',
    '822083633': '回复消息',
    '922746929': '拍一拍',
    '1090519089': '发送文件',
    '318767153': '付款成功',
    '436207665': '发红包',
}


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    if os.path.exists(path):
        return False
    os.makedirs(path)
    return True


root_path = os.path.abspath('.')
mkdir(os.path.abspath('.') + '/app/DataBase')
mkdir(os.path.abspath('.') + '/app/data/emoji')
if os.path.exists('./app/DataBase/Msg.db'):
    DB = sqlite3.connect("./app/DataBase/Msg.db", check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()
if os.path.exists('./Msg.db'):
    DB = sqlite3.connect("./Msg.db", check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def is_db_exist() -> bool:
    """
    判断数据库是否正常使用
    """
    global DB
    global cursor
    if DB and cursor:
        try:
            sql = 'select * from userinfo where id=2'
            cursor.execute(sql)
            result = cursor.fetchone()
            if result[2]:
                return True
            else:
                return False
        except Exception as e:
            return False
    return False


def init_database():
    global DB
    global cursor
    if os.path.exists('./app/DataBase/Msg.db'):
        DB = sqlite3.connect("./app/DataBase/Msg.db", check_same_thread=False)
        # '''创建游标'''
        cursor = DB.cursor()
    if os.path.exists('./Msg.db'):
        DB = sqlite3.connect("./Msg.db", check_same_thread=False)
        # '''创建游标'''
        cursor = DB.cursor()


def decrypt(db, key):
    if not key:
        print('缺少数据库密钥')
        return False
    if not db:
        print('没有数据库文件')
        return False
    if is_db_exist():
        print('/app/DataBase/Msg.db  已经存在')
        return True
    cmd = './sqlcipher-3.0.1/bin/sqlcipher-shell32.exe'
    param = f"""
    PRAGMA key = '{key}';
    PRAGMA cipher_migrate;
    ATTACH DATABASE './app/DataBase/Msg.db' AS Msg KEY '';
    SELECT sqlcipher_export('Msg');
    DETACH DATABASE Msg;
        """
    with open('./app/data/config.txt', 'w') as f:
        f.write(param)
    p = os.system(f"{os.path.abspath('.')}{cmd} {db} < ./app/data/config.txt")
    global DB
    global cursor
    DB = sqlite3.connect("./app/DataBase/Msg.db", check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def get_myinfo():
    sql = 'select * from userinfo where id=2'
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[2]


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
    try:
        lock.acquire(True)
        sql = 'select conRemark,nickname from rcontact where username=?'
        cursor.execute(sql, [username])
        result = cursor.fetchone()
        if result:
            if result[0]:
                return result[0]
            else:
                return result[1]
    except:
        time.sleep(0.1)
        sql = 'select conRemark,nickname from rcontact where username=?'
        cursor.execute(sql, [username])
        result = cursor.fetchone()
        if result:
            if result[0]:
                return result[0]
            else:
                return result[1]
    finally:
        lock.release()

    return False


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
        return os.path.join(root_path, '/app/data/icons/default_avatar.svg')
    wxid = str(wxid)
    avatar = avatar_md5(wxid)
    path = os.path.join(root_path, 'app', 'data', 'avatar', avatar[:2], avatar[2:4])
    # avatar_path + avatar[:2] + '/' + avatar[2:4]
    for root, dirs, files in os.walk(path):
        for file in files:
            if avatar in file:
                avatar = file
                break
    return os.path.join(path, avatar)
    # return f'''{path}/{avatar}'''
    # return f'''{path}/user_{avatar}.png'''


def get_message(wxid, num):
    sql = '''
    select * from message
    where talker = ?
    order by createTime desc
    limit ?,100
    '''
    cursor.execute(sql, [wxid, num * 100])
    return cursor.fetchall()


def get_text_by_num(wxid, num):
    sql = '''
            SELECT content,strftime('%Y-%m-%d',createTime/1000,'unixepoch','localtime') as days
            from message
            where talker = ? and type=1
            order by days
        '''
    '''group by days'''
    cursor.execute(sql, [wxid])
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
    cursor.execute(sql, [start * 1000, end * 1000])
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
        order by createTime
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
        try:
            cursor.execute(sql, [imgPath])
            result = cursor.fetchone()
            download_emoji(newPath, result[0])
        except sqlite3.ProgrammingError as e:
            print(e, imgPath)
            return False
    return False


def download_emoji(imgPath, url):
    if not url:
        return False
    try:
        resp = requests.get(url)
        with open(imgPath, 'wb') as f:
            f.write(resp.content)
    except:
        return False
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


def send_nums(username):
    sql = '''
        select count(*) from message
        where talker = ? and isSend=1
    '''
    cursor.execute(sql, [username])
    return cursor.fetchone()[0]


def recv_nums(username):
    sql = '''
            select count(*) from message
            where talker = ? and isSend=0
        '''
    cursor.execute(sql, [username])
    return cursor.fetchone()[0]


def get_imgPath(imgPath):
    sql = '''
        select bigImgPath from ImgInfo2
        where thumbImgPath = ?;
    '''
    cursor.execute(sql, [imgPath])
    return cursor.fetchone()[0]


def get_text(username):
    sql = '''
        select content from message
        where talker=? and type=1
    '''
    cursor.execute(sql, [username])
    result = cursor.fetchall()
    return ''.join(map(lambda x: x[0], result))


def msg_type_num(username):
    sql = '''
        select type,count(*) from message
        where talker = ?
        group by type
    '''
    cursor.execute(sql, [username])
    return cursor.fetchall()


def get_msg_start_time(username):
    sql = '''
        select strftime('%Y-%m-%d %H:%M:%S',createTime/1000,'unixepoch','localtime') from message
        where talker = ?
        order by msgId
        limit 1
    '''
    cursor.execute(sql, [username])
    return cursor.fetchone()[0]


def get_msg_end_time(username):
    sql = '''
        select strftime('%Y-%m-%d %H:%M:%S',createTime/1000,'unixepoch','localtime') from message
        where talker = ?
        order by msgId desc
        limit 1
    '''
    cursor.execute(sql, [username])
    try:
        return cursor.fetchone()[0]
    except:
        return None


def get_msg_by_days(username, year='2022'):
    sql = '''
        SELECT strftime('%Y-%m-%d',createTime/1000,'unixepoch','localtime') as days,count(msgId)
        from message
        where talker = ? and strftime('%Y',createTime/1000,'unixepoch','localtime') = ?
        group by days
    '''
    cursor.execute(sql, [username, year])
    result = cursor.fetchall()
    return result


def get_msg_by_day(username):
    sql = '''
            SELECT strftime('%Y-%m-%d',createTime/1000,'unixepoch','localtime') as days,count(msgId)
            from message
            where talker = ?
            group by days
        '''
    cursor.execute(sql, [username])
    result = cursor.fetchall()
    return result


def get_msg_by_month(username, year='2022'):
    sql = '''
            SELECT strftime('%Y-%m',createTime/1000,'unixepoch','localtime') as days,count(msgId)
            from message
            where talker = ? and strftime('%Y',createTime/1000,'unixepoch','localtime') = ?
            group by days
        '''
    cursor.execute(sql, [username, year])
    result = cursor.fetchall()
    return result


def get_msg_by_hour(username):
    sql = '''
                SELECT strftime('%H:00',createTime/1000,'unixepoch','localtime') as days,count(msgId)
                from message
                where talker = ?
                group by days
            '''
    cursor.execute(sql, [username])
    result = cursor.fetchall()
    return result


def get_sport():
    sql = '''
                SELECT createTime,content,strftime('%Y-%m-%d',createTime/1000,'unixepoch','localtime') as months
                from message
                where talker = 'gh_43f2581f6fd6'
            '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_myInfo():
    sql = '''
        select value from userinfo
        where id = 4
    '''
    cursor.execute(sql)
    name = cursor.fetchone()[0]
    sql = '''
            select value from userinfo
            where id = 5
        '''
    cursor.execute(sql)
    email = cursor.fetchone()[0]
    sql = '''
            select value from userinfo
            where id = 6
        '''
    cursor.execute(sql)
    tel = cursor.fetchone()[0]
    sql = '''
            select value from userinfo
            where id = 9
        '''
    cursor.execute(sql)
    QQ = cursor.fetchone()[0]
    sql = '''
                select value from userinfo
                where id = 42
            '''
    cursor.execute(sql)
    wxid = cursor.fetchone()[0]
    sql = '''
                select value from userinfo
                where id = 12291
            '''
    cursor.execute(sql)
    signature = cursor.fetchone()[0]
    sql = '''
                    select value from userinfo
                    where id = 12292
                '''
    cursor.execute(sql)
    city = cursor.fetchone()[0]
    sql = '''
                    select value from userinfo
                    where id = 12293
                '''
    cursor.execute(sql)
    province = cursor.fetchone()[0]
    return {
        'name': name,
        'username': wxid,
        'city': city,
        'province': province,
        'email': email,
        'QQ': QQ,
        'signature': signature,
        'tel': tel,
    }


def search_Latest_chat_time(wxid):
    # 查找聊天最晚的消息
    sql = '''
            SELECT strftime('%H:%M:%S',createTime/1000,'unixepoch','localtime') as t,content,strftime('%Y-%m-%d %H:%M:%S',createTime/1000,'unixepoch','localtime')
            from message
            where talker = ? and t>'00:00:00' and t<'05:00:00' and type=1
            order by t desc
        '''
    cursor.execute(sql, [wxid])
    result = cursor.fetchall()
    return result


def search_emoji(wxid):
    # 查找聊天最晚的消息
    sql = '''
                SELECT imgPath,strftime('%Y-%m-%d %H:%M:%S',createTime/1000,'unixepoch','localtime') as t,count(imgPath)
                from message
                where talker = ? and t>'2022-01-01 00:00:00' and t<'2022-12-31 00::00:00' and type=47 and isSend=0
                group by content
                order by count(imgPath) desc
            '''
    cursor.execute(sql, [wxid])
    result = cursor.fetchall()
    return result


if __name__ == '__main__':
    wxid = 'wxid_8piw6sb4hvfm22'
    # wxid = 'wxid_wt2vsktnu4z022'
    # emotion_analysis(wxid)
    t = search_Latest_chat_time(wxid)
    print(t[0])
    d = get_msg_by_days(wxid)
    print(len(d))
    e = search_emoji(wxid)
    print(e)
    p = get_emoji(e[1][0])
    print(p)
