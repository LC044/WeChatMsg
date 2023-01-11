# -*- coding: utf-8 -*-
"""
@File    : data.py
@Author  : Shuaikang Zhou
@Time    : 2022/12/13 20:59
@IDE     : Pycharm
@Version : Python3.10
@comment : ···
"""
import json
import pymysql
import random
import time
import hashlib
import datetime
import os
import shutil
f = open('./app/data/config.json','r')
config = json.loads(f.read())
username = config['username']
password = config['password']
database = config['database']
# 打开数据库连接t
db = pymysql.connect(
    host='localhost',
    user=username,
    password=password,
    database=database,
    autocommit=True
)
cursor = db.cursor()


def register(username, password, nickname):
    """
    注册账号
    :param username: 用户名
    :param password: 密码
    :param nickname: 昵称
    :return:
    """
    try:
        create = 'insert into users (username,password,createTime) values (%s,%s,%s)'
        timestamp = float(time.time())
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(create, [username, password, dt])
        create = 'insert into userinfo (username,nickname) values (%s,%s)'
        cursor.execute(create, [username, nickname])
        db.commit()
        try:
            sql = f'''
            create view msg_view_{username}
            as 
            select msgId,type,IsSend,createTime,content,talkerId from message
            where username = %s
            order by msgId;
            '''
            cursor.execute(sql, [username])
            sql = f'''
            create view contact_view_{username}
            as 
            select contactId,conRemark,type,addTime from contact
            where username = %s;
            '''
            cursor.execute(sql, [username])
            sql = f'''
            create view group_view_{username}
            as
            select g_id,g_name,gu_nickname,gu_type,gu_time from group_users,`group`
            where gu_uid=%s and group_users.gu_gid=`group`.g_id;
            '''
            cursor.execute(sql, [username])
            db.commit()
        except pymysql.err.OperationalError:
            print('视图已经存在')
    except pymysql.err.IntegrityError:
        print('用户已存在')
        return False
    return True


def login(username, password):
    select = 'select * from users where username = %s and password = %s'
    cursor.execute(select, [username, password])
    result = cursor.fetchall()
    if result:
        return True
    return False


def del_user(username):
    sql = 'delete from users where username = %s'
    cursor.execute(sql, [username])
    db.commit()
    return True


def searchUser(username):
    select = 'select * from users where username = %s'
    cursor.execute(select, [username])
    result = cursor.fetchall()
    if result:
        return True
    return False


def add_contact(username, contactId, conRemark, _type=3):
    send = 'insert into contact (username,conRemark,type,addTime,contactId) values(%s,%s,%s,%s,%s)'
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    select = 'select * from userinfo where username = %s '
    cursor.execute(select, [username])
    result = cursor.fetchall()
    if not result:
        return False
    if not conRemark:
        conRemark = None
    try:
        if _type == 3:
            cursor.execute(send, [username, conRemark, 3, dt, contactId])
            db.commit()
            return (contactId, conRemark, 3, dt)
    except:
        return False


def get_userinfo(username):
    sql = 'select * from userinfo where username = %s'
    cursor.execute(sql, [username])
    result = cursor.fetchone()
    return result[0]


def online(username, socket=None):
    status = random.randint(32010, 52090)
    sql = 'update userinfo set status = %s where username=%s'
    cursor.execute(sql, [status, username])
    db.commit()

    return status


def tell_online(username, socket):
    if socket:
        contacts = get_contacts(username)
        for contact in contacts:
            contactID = contact[0]
            status = check_online(contactID)
            if status != -1:
                ta_addr = ('localhost', status)
                send_data = {
                    'type': 'T',
                    'username': username,
                    'content': '在线0000_1'
                }
                socket.sendto(json.dumps(send_data).encode('utf-8'), ta_addr)


def offline(username):
    status = -1
    sql = 'update userinfo set status = %s where username=%s'
    cursor.execute(sql, [status, username])
    db.commit()
    return status


def check_online(username):
    db.commit()
    sql = 'select status from userinfo where username=%s'
    cursor.execute(sql, [username])
    db.commit()
    result = cursor.fetchone()
    # print(username, '端口号：', result)
    if result:
        return result[0]
    else:
        return -1


def send_msg(IsSend, msg, ta, me, status=-1, _type=3):
    if status == -1:
        return False
    send = 'insert into message (type,isSend,createTime,content,talkerId,username) values(%s,%s,%s,%s,%s,%s)'
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if _type == 3:
        cursor.execute(send, [_type, IsSend, dt, msg, ta, me])
        db.commit()
        return 1, _type, IsSend, datetime.datetime.now(), msg, ta


def send_group_msg(gid, msg, talker, IsSend=0, _type=3):
    send = 'insert into group_message (g_id,gm_type,gm_content,gm_time,gm_talker,gm_isSend) values(%s,%s,%s,%s,%s,%s)'
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if _type == 3:
        cursor.execute(send, [gid, _type, msg, dt, talker, IsSend])
        db.commit()
        return 1, gid, _type, msg, datetime.datetime.now(), talker, IsSend


def get_group_message(g_id):
    sql = f'select * from group_message where g_id = %s order by gm_id'
    cursor.execute(sql, [g_id])
    result = cursor.fetchall()
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
    avatar_path = r"./data/avatar/"
    path = avatar_path + avatar[:2] + '/' + avatar[2:4]
    for root, dirs, files in os.walk(path):
        for file in files:
            if avatar in file:
                avatar = file
                break
    return path + '/' + avatar


def get_contacts(username):
    sql = f'select * from contact_view_{username} '
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_myinfo(username):
    sql = 'select * from userinfo where username = %s'
    cursor.execute(sql, [username])
    result = cursor.fetchone()
    return result


def update_userinfo(userinfo):
    sql = '''
    update userinfo
    set 
        nickname=%s,
        gender=%s,
        city=%s,
        province=%s,
        tel=%s,
        email=%s,
        signsture=%s
    where username=%s
    '''
    cursor.execute(sql, userinfo)


def get_nickname(username):
    sql = 'select nickname from userinfo where username=%s'
    cursor.execute(sql, [username])
    result = cursor.fetchone()
    return result[0]


def update_conRemark(username, contactId, new_conRemark):
    sql = 'update contact set conRemark=%s where username=%s and contactId=%s'
    cursor.execute(sql, [new_conRemark, username, contactId])
    db.commit()
    return True


def delete_contact(username, contactId):
    sql = 'delete from contact where username=%s and contactId=%s'
    cursor.execute(sql, [username, contactId])
    db.commit()
    return True


def delete_group(uid, gid):
    sql = 'delete from group_users where gu_uid=%s and gu_gid=%s'
    cursor.execute(sql, [uid, gid])
    db.commit()
    return True


def get_remark(username, talkerId):
    sql = f'select conRemark from contact_view_{username} where contactId = %s'
    cursor.execute(sql, [talkerId])
    result = cursor.fetchone()
    return result[0]


def mycopyfile(srcfile, dstpath):
    # 复制函数
    """
    复制文件
    :param srcfile: 原路径
    :param dstpath: 新路径
    :return:
    """
    # if 1:
    try:
        if not os.path.isfile(srcfile):
            print("%s not exist!" % (srcfile))
            return
        else:
            print(dstpath)
            if os.path.isfile(dstpath):
                os.remove(dstpath)
            fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
            dpath, dname = os.path.split(dstpath)
            if not os.path.exists(dpath):
                os.makedirs(dpath)  # 创建路径
            # dstpath = '/'.join(dstpath.split('/')[:-1])+'/'

            # print(dpath,dname)
            shutil.copy(srcfile, dpath)  # 复制文件
            os.rename(dpath + '/' + fname, dstpath)
            # print ("copy %s -> %s"%(srcfile, dstpath + fname))
    except:
        print('文件已存在')


def get_message(username, talkerId):
    sql = f'select * from msg_view_{username} where talkerId = %s order by msgId'
    cursor.execute(sql, [talkerId])
    result = cursor.fetchall()
    return result


def create_group(g_name, g_admin, g_notice=None, g_intro=None):
    g_id = random.randint(10000, 99999)
    sql = '''insert into `group` (g_id,g_name,g_admin,g_notice,g_intro,g_time) values (%s, %s, %s, %s, %s, %s);'''
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    param = [g_id, g_name, g_admin, g_notice, g_intro, dt]
    print(param)
    cursor.execute(sql, param)
    sql = '''insert into `group_users` (gu_uid,gu_gid,gu_time,gu_nickname,gu_type) values (%s, %s, %s, %s, %s);'''
    param = [g_admin, g_id, dt, None, 1]
    cursor.execute(sql, param)
    db.commit()
    return g_id


def add_group(username, g_id, nickname):
    group = search_group(g_id)
    if not group:
        return False
    if not nickname:
        nickname = None
    sql = 'insert into group_users (gu_uid,gu_gid,gu_time,gu_nickname,gu_type) values (%s,%s,%s,%s,%s)'
    dt = dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(sql, [username, g_id, dt, nickname, 2])
    db.commit()
    return [g_id, dt, nickname, 2]


def search_group(gid):
    sql = 'select * from `group` where g_id=%s'
    cursor.execute(sql, [gid])
    result = cursor.fetchone()
    return result


def get_groups(username):
    sql = f'select * from group_view_{username}'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_group_users(g_id):
    db.commit()
    sql = '''
        select gu_uid,gu_gid,gu_time,gu_nickname,status 
        from group_users,userinfo 
        where gu_gid=%s and 
        gu_uid=userinfo.username 
    '''
    cursor.execute(sql, [g_id])
    db.commit()
    result = cursor.fetchall()
    return result


# send_msg(3, '你好', '123456')
if __name__ == '__main__':
    # add_contact('2020303457', '周帅康')
    # contacts = get_contacts('')
    # print(contacts)
    # messages = get_message('2020303457', '')
    # print(messages)
    # online('2020303457')
    # status = check_online('2020303457')
    # print('status:', status)
    # offline('2020303457')
    # status = check_online('2020303457')
    # print('status:', status)
    # print(get_remark('', 2020303457))
    # print(get_groups('2020303457'))
    # # print(create_group("DB实验", '2020303457', g_notice=str(12), g_intro="test"))
    # print(get_groups(''))
    # print(get_group_users(61067))
    print(get_myinfo(''))
