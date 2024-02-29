import os
import sys
import time
from urllib.parse import urljoin

import requests
from flask import Flask, render_template, send_file, jsonify, make_response, request
from pyecharts.charts import Bar

from app.DataBase import msg_db, micro_msg_db
from app.DataBase.hard_link import decodeExtraBuf
from app.analysis import analysis
from app.config import SERVER_API_URL
from app.person import Contact, Me, ContactDefault
from app.util.emoji import get_most_emoji
from app.util.region_conversion import conversion_region_to_chinese

app = Flask(__name__)

run_flag = False
wxid = ''
contact: Contact = None
start_time = '2023-1-01 00:00:00'
end_time = '2023-12-31 23:59:59'
time_range = (start_time, end_time)
html: str = ''

api_url = urljoin(SERVER_API_URL,'upload')



def get_contact(wxid) -> ContactDefault | Contact:
    contact_info_list = micro_msg_db.get_contact_by_username(wxid)
    if not contact_info_list:
        return ContactDefault('')
    detail = decodeExtraBuf(contact_info_list[9])
    # detail = {}
    contact_info = {
        'UserName': contact_info_list[0],
        'Alias': contact_info_list[1],
        'Type': contact_info_list[2],
        'Remark': contact_info_list[3],
        'NickName': contact_info_list[4],
        'smallHeadImgUrl': contact_info_list[7],
        'label_name': contact_info_list[10],
        'detail': detail,
    }
    contact =Contact(contact_info)
    print(detail)
    # region = contact.detail.get('region')
    # area = conversion_region_to_chinese(region)
    # print(area)
    return contact


@app.route("/")
def index():
    contact_topN_num = msg_db.get_chatted_top_contacts(time_range=time_range, top_n=9999999, contain_chatroom=True)
    total_msg_num = sum(list(map(lambda x: x[1], contact_topN_num)))
    contact_topN = []
    for wxid, num in contact_topN_num:
        contact = get_contact(wxid)
        text_length = 0
        contact_topN.append([contact, num, text_length])
    contacts_data = analysis.contacts_analysis(contact_topN)
    contact_topN = []
    send_msg_num = msg_db.get_send_messages_number_sum(time_range)
    contact_topN_num = msg_db.get_chatted_top_contacts(time_range=time_range, top_n=9999999, contain_chatroom=False)

    for wxid, num in contact_topN_num[:6]:
        contact = get_contact(wxid)
        text_length = msg_db.get_message_length(wxid, time_range)
        contact_topN.append([contact, num, text_length])

    my_message_counter_data = analysis.my_message_counter(time_range=time_range)
    data = {
        'avatar': Me().smallHeadImgUrl,
        'contact_topN': contact_topN,
        'contact_num': len(contact_topN_num),
        'send_msg_num': send_msg_num,
        'receive_msg_num': total_msg_num - send_msg_num,
    }
    return render_template('index.html', **data,**contacts_data, **my_message_counter_data)


@app.route("/christmas/<wxid>")
def christmas(wxid):
    contact = get_contact(wxid)
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
    wordcloud_cloud_data = analysis.wordcloud_christmas(contact.wxid,time_range=time_range)
    msg_data = msg_db.get_messages_by_hour(contact.wxid, time_range=time_range)
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
    latest_dialog = msg_db.get_latest_time_of_message(contact.wxid, time_range=time_range)
    latest_time = latest_dialog[0][2] if latest_dialog else ''
    time_data = {
        'latest_time': latest_time,
        'latest_time_dialog': latest_dialog,
        'chat_time_label': label,
        'chat_time': chat_time,
        'chat_time_num': num,
    }
    month_data = msg_db.get_messages_by_month(contact.wxid, time_range=time_range)

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
        'total_msg_num': msg_db.get_messages_number(contact.wxid, time_range=time_range),
        'max_month': max_month,
        'min_month': min_month,
        'max_month_num': max_num,
        'min_month_num': min_num,
    }

    calendar_data = analysis.calendar_chart(contact.wxid, time_range)
    emoji_msgs = msg_db.get_messages_by_type(contact.wxid, 47, time_range=time_range)
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


@app.route('/upload')
def upload():
    global html
    data = {
        'html_content': html,
        'wxid': contact.wxid,
        'username': Me().wxid,
        'token':Me().token,
        'type': 'contact'
    }
    response = requests.post(api_url, data=data)
    print(response)
    print(response.json())
    response = make_response(response.json())
    response.headers.add('Access-Control-Allow-Origin', '*')  # Replace '*' with specific origins if needed
    response.headers.add('Content-Type', 'application/json')
    return response


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
    global run_flag
    if not run_flag:
        try:
            app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
            run_flag = True
        except:
            pass
    else:
        pass


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


@app.route('/month_count', methods=['POST'])
def get_chart_options():
    wxid = request.json.get('wxid')
    time_range = request.json.get('time_range', [])
    data = analysis.month_count(wxid, time_range=time_range)
    return jsonify(data)


@app.route('/wordcloud', methods=['POST'])
def get_wordcloud():
    wxid = request.json.get('wxid')
    time_range = request.json.get('time_range', [])

    world_cloud_data = analysis.wordcloud_(wxid, time_range=time_range)
    return jsonify(world_cloud_data)


@app.route('/charts/<wxid>')
def charts(wxid):
    # 渲染模板，并传递图表的 HTML 到模板中
    contact = get_contact(wxid)
    try:
        first_message, first_time = msg_db.get_first_time_of_message(wxid)
    except TypeError:
        first_time = '2023-01-01 00:00:00'
    data = {
        'wxid': wxid,
        'my_nickname': Me().name,
        'ta_nickname': contact.remark,
        'first_time': first_time
    }
    return render_template('charts.html', **data)


@app.route('/calendar', methods=['POST'])
def get_calendar():
    wxid = request.json.get('wxid')
    time_range = request.json.get('time_range', [])
    world_cloud_data = analysis.calendar_chart(wxid, time_range=time_range)
    return jsonify(world_cloud_data)


@app.route('/message_counter', methods=['POST'])
def get_counter():
    wxid = request.json.get('wxid')
    time_range = request.json.get('time_range', [])
    contact = get_contact(wxid)
    data = analysis.sender(wxid, time_range=time_range, my_name=Me().name, ta_name=contact.remark)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
