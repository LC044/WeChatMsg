import os
import sys

import requests
from flask import Flask, render_template, send_file, jsonify, make_response

from app.DataBase import msg_db
from app.analysis import analysis
from app.person import Contact, Me
from app.util.emoji import get_most_emoji

app = Flask(__name__)

wxid = ''
contact: Contact = None

html: str = ''
api_url = 'http://api.lc044.love/upload'


@app.route("/")
def index():
    # 渲染模板，并传递图表的 HTML 到模板中
    return "index.html"


@app.route("/christmas")
def christmas():
    # 渲染模板，并传递图表的 HTML 到模板中
    try:
        first_message, first_time = msg_db.get_first_time_of_message(contact.wxid)
    except TypeError:
        first_time = '2023-01-01 00:00:00'
    data = {
        'ta_avatar_path': contact.smallHeadImgUrl,
        'my_avatar_path': Me().smallHeadImgUrl,
        'ta_nickname': contact.remark,
        'my_nickname': Me().name,
        'first_time': first_time,
    }
    wordcloud_cloud_data = analysis.wordcloud_christmas(contact.wxid)
    msg_data = msg_db.get_messages_by_hour(contact.wxid, year_="2023")
    msg_data.sort(key=lambda x: x[1], reverse=True)
    desc = {
        '夜猫子': {'22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00'},
        '正常作息': {'06:00', "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00",
                     "17:00", "18:00", "19:00", "20:00", "21:00"},
    }
    time_, num = msg_data[0] if msg_data else ('', 0)
    chat_time = f"凌晨{time_}" if time_ in {'00:00', '01:00', '02:00', '03:00', '04:00', '05:00'} else time_
    label = '夜猫子'
    for key, item in desc.items():
        if time_ in item:
            label = key
    latest_dialog = msg_db.get_latest_time_of_message(contact.wxid, year_='2023')
    latest_time = latest_dialog[0][2] if latest_dialog else ''
    time_data = {
        'latest_time': latest_time,
        'latest_time_dialog': latest_dialog,
        'chat_time_label': label,
        'chat_time': chat_time,
        'chat_time_num': num,
    }
    month_data = msg_db.get_messages_by_month(contact.wxid, True, year_='2023')

    if month_data:
        month_data.sort(key=lambda x: x[1])
        max_month, max_num = month_data[-1]
        min_month, min_num = month_data[0]
        min_month = min_month[-2:].lstrip('0') + '月'
        max_month = max_month[-2:].lstrip('0') + '月'
    else:
        max_month, max_num = '月份', 0
        min_month, min_num = '月份', 0
    month_data = {
        'year': '2023',
        'total_msg_num': msg_db.get_messages_number(contact.wxid, '2023'),
        'max_month': max_month,
        'min_month': min_month,
        'max_month_num': max_num,
        'min_month_num': min_num,
    }
    calendar_data = analysis.calendar_chart(contact.wxid, True, year='2023')
    emoji_msgs = msg_db.get_messages_by_type(contact.wxid, 47, year_='2023')
    url, num = get_most_emoji(emoji_msgs)
    emoji_data = {
        'emoji_total_num': len(emoji_msgs),
        'emoji_url': url,
        'emoji_num': num,
    }
    global html
    html = render_template("christmas.html", **data, **wordcloud_cloud_data, **time_data, **month_data, **calendar_data,
                           **emoji_data)
    return html


@app.route('/home')
def home():
    try:
        first_message, first_time = msg_db.get_first_time_of_message(contact.wxid)
    except TypeError:
        return set_text('咱就是说，一次都没聊过就别分析了')
    data = {
        'sub_title': '二零二三年度报告',
        'avatar_path': contact.avatar_path,
        'nickname': contact.remark,
        'first_time': first_time,
    }

    return render_template('home.html', **data)


@app.route('/upload')
def upload():
    global html
    data = {
        'html_content': html,
        'wxid': contact.wxid,
        'username': Me().wxid,
    }
    response = requests.post(api_url, data=data)
    print(response.json())
    response = make_response(response.json())
    response.headers.add('Access-Control-Allow-Origin', '*')  # Replace '*' with specific origins if needed
    response.headers.add('Content-Type', 'application/json')

    return response


@app.route('/wordcloud/<who>/')
def one(who):
    wxid = contact.wxid
    # wxid = 'wxid_lltzaezg38so22'
    # print('wxid:'+wxid)
    world_cloud_data = analysis.wordcloud(wxid, who=who)  # 获取与Ta的对话数据
    # print(world_cloud_data)
    who = "你" if who == '1' else "TA"
    with open('wordcloud.html', 'w', encoding='utf-8') as f:
        f.write(render_template('wordcloud.html', **world_cloud_data))
    return render_template('wordcloud.html', **world_cloud_data, who=who)


def set_text(text):
    html = '''
        <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Centered Text</title>
        <style>
            body {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }

            .centered-text {
                font-size: 2em;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="centered-text">
            <!-- 这里是要显示的四个大字 -->
            %s
            <img src="https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.2.8/assets/newemoji/Yellowdog.png" id="旺柴" class="emoji_img">
        </div>
    </body>
    </html>
        ''' % (text)
    return html


@app.route('/test')
def test():
    return set_text('以下内容仅对VIP开放')


def run(port=21314):
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


@app.route('/data/avatar/<filename>')
def get_image(filename):
    try:
        # 返回动态生成的图片
        return send_file(os.path.join("../../data/avatar/", filename), mimetype='image/png')
    except:
        return send_file(os.path.join(f"{os.getcwd()}/data/avatar/", filename), mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
