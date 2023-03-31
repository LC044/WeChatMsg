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
    cmd = './sqlcipher-3.0.1/bin/sqlcipher-shell32.exe'
    print(os.path.abspath('.'))
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
    if result:
        if result[0]:
            return result[0]
        else:
            return result[1]
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
        try:
            cursor.execute(sql, [imgPath])
            result = cursor.fetchone()
            download_emoji(newPath, result[0])
        except sqlite3.ProgrammingError as e:
            print(e, imgPath)
            return False
    return newPath


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


from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Timeline, Grid
import pandas as pd
import xmltodict


def sport(username):
    sports = get_sport()
    ranks = []
    steps = []
    date = []
    for sport in sports:
        try:
            timestamp, content, t = sport
            rank_data = xmltodict.parse(content)
            sub_data = rank_data['msg']['appmsg']['hardwareinfo']['messagenodeinfo']
            # print(sub_data)
            my_rank = sub_data['rankinfo']['rank']['rankdisplay']
            my_steps = int(sub_data['rankinfo']['score']['scoredisplay'])
            # print(f'rank: {my_rank},steps: {my_steps}')
            rank_view = rank_data['msg']['appmsg']['hardwareinfo']['rankview']['rankinfolist']['rankinfo']
            for userinfo in rank_view:
                username0 = userinfo['username']
                if username0 == username:
                    rank_ta = int(userinfo['rank']['rankdisplay'])
                    steps_ta = int(userinfo['score']['scoredisplay'])
                    ranks.append(rank_ta)
                    steps.append(steps_ta)
                    date.append(t)
        except:
            continue
    df = pd.DataFrame({'ranks': ranks, 'score': steps, 'date': date}, index=date)
    months = pd.date_range(date[0], date[-1], freq='M')
    tl = Timeline(init_opts=opts.InitOpts(width="440px", height="245px"))
    tl.add_schema(is_auto_play=True)
    for i in range(len(months) - 1):
        da = df[(months[i + 1].strftime("%Y-%m-%d") >= df['date']) & (df['date'] > months[i].strftime("%Y-%m-%d"))]
        bar = (
            Bar(init_opts=opts.InitOpts(width="400px", height="235px"))
            .add_xaxis(list(da['date']))
            .add_yaxis(
                "步数",
                list(da['score']),
                yaxis_index=1,
                color="#d14a61",
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="步数",
                    type_="value",
                    # grid_index=0,
                    # min_=0,
                    # max_=250,
                    position="right",
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#d14a61")
                    ),
                    # axislabel_opts=opts.LabelOpts(formatter="{value} ml"),
                )
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="排名",
                    # min_=0,
                    # max_=25,
                    position="left",
                    is_inverse=True,
                    # interval=True,
                    # grid_index=1,
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#675bba")
                    ),
                    # axislabel_opts=opts.LabelOpts(formatter="{value} °C"),
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="{}月运动步数".format(months[i + 1].strftime("%Y-%m"))),
                # legend_opts=opts.LegendOpts(is_show=False),
                yaxis_opts=opts.AxisOpts(is_inverse=True)
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    is_show=False
                )
            )
        )
        # init_opts = opts.InitOpts(width="400px", height="235px")
        line = (
            Line(init_opts=opts.InitOpts(width="400px", height="235px"))
            .add_xaxis(list(da['date']))
            .add_yaxis(
                "排名",
                list(da['ranks']),
                yaxis_index=0,
                color="#675bba",
                # label_opts=opts.LabelOpts(is_show=False),

            )
            .set_global_opts(
                yaxis_opts=opts.AxisOpts(is_inverse=True)
            )
        )
        bar.overlap(line)
        grid = Grid()
        grid.add(bar, opts.GridOpts(pos_left="5%", pos_right="20%"), is_control_axis_index=True)
        grid.render("grid_multi_yaxis.html")
        quit()
        # tl.add(bar, "{}".format(months[i].strftime("%Y-%m")))
    # tl.render("./sports.html")

    return {
        username: {
            'ranks': ranks,
            'score': steps,
            'date': date,
        }
    }


def radar_hour(username):
    msg_data = get_msg_by_hour(username)
    x_axis = list(map(lambda x: x[0], msg_data))
    y_data = list(map(lambda x: x[1], msg_data))
    print(x_axis)
    print(y_data)
    max_ = max(y_data)
    c = (
        Line()
        .add_xaxis(xaxis_data=x_axis)
        .add_yaxis(
            series_name="聊天频率",
            y_axis=y_data,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        )
        .render("temperature_change_line_chart.html")
    )


def chat_start_endTime(username):
    start_time = get_msg_start_time(username)
    end_time = get_msg_end_time(username)
    year = start_time[:4]
    month = start_time[5:7]
    day = start_time[8:10]
    hour = start_time[11:13]
    minute = start_time[14:16]
    second = start_time[17:]
    print(year, month, day, hour, minute, second)


if __name__ == '__main__':
    # rconversation = get_rconversation()
    # for i in rconversation:
    #     print(i)
    # contacts = get_all_message('wxid_vqave8lcp49r22')
    # for contact in contacts:
    #     print(contact)
    # [(177325,)] (73546,) (103770,)
    # print(search_send_message(1, 1))
    # print(send_nums('wxid_vqave8lcp49r22'))
    # print(recv_nums('wxid_vqave8lcp49r22'))
    # # for t in get_text('wxid_vqave8lcp49r22'):
    # #     print(t)
    # print(msg_type_num('wxid_vqave8lcp49r22'))
    # st = get_msg_start_time('wxid_vqave8lcp49r22')
    # print(st, timestamp2str(st))
    # st = get_msg_end_time('wxid_vqave8lcp49r22')
    # print(st, timestamp2str(st))
    # print(get_msg_by_month('wxid_8piw6sb4hvfm22', year='2022'))
    # print(len(get_sport()))
    # result = sport('wxid_8piw6sb4hvfm22')
    # print(get_imgPath('THUMBNAIL_DIRPATH://th_92f32326df645b3e1aecef9b6266a3b8'))
    # result = get_msg_by_hour('wxid_8piw6sb4hvfm22')
    # print(result)
    # radar_hour('wxid_8piw6sb4hvfm22')
    # print(result)
    print(get_msg_start_time('wxid_8piw6sb4hvfm22'), get_msg_end_time('wxid_8piw6sb4hvfm22'))
    chat_start_endTime('wxid_8piw6sb4hvfm22')
