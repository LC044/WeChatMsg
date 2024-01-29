import os
from collections import Counter
import sys
from datetime import datetime

from app.DataBase import msg_db, MsgType
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Calendar, Bar, Line, Pie

os.makedirs('./data/聊天统计/',exist_ok=True)
def wordcloud_(wxid, time_range=None):
    import jieba
    txt_messages = msg_db.get_messages_by_type(wxid, MsgType.TEXT, time_range=time_range)
    if not txt_messages:
        return {
            'chart_data': None,
            'keyword': "没有聊天你想分析啥",
            'max_num': "0",
            'dialogs': []
        }
    # text = ''.join(map(lambda x: x[7], txt_messages))
    text = ''.join(map(lambda x: x[7], txt_messages))  # 1“我”说的话，0“Ta”说的话

    total_msg_len = len(text)
    # 使用jieba进行分词，并加入停用词
    words = jieba.cut(text)
    # 统计词频
    word_count = Counter(words)
    # 过滤停用词
    stopwords_file = './app/data/stopwords.txt'
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords1 = set(stopword_file.read().splitlines())
    # 构建 FFmpeg 可执行文件的路径
    stopwords = set()
    stopwords_file = './app/resources/data/stopwords.txt'
    if not os.path.exists(stopwords_file):
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        stopwords_file = os.path.join(resource_dir, 'app', 'resources', 'data', 'stopwords.txt')
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords = set(stopword_file.read().splitlines())
        stopwords = stopwords.union(stopwords1)
    filtered_word_count = {word: count for word, count in word_count.items() if len(word) > 1 and word not in stopwords}

    # 转换为词云数据格式
    data = [(word, count) for word, count in filtered_word_count.items()]
    # text_data = data
    data.sort(key=lambda x: x[1], reverse=True)

    text_data = data[:100] if len(data) > 100 else data
    # 创建词云图
    keyword, max_num = text_data[0]
    w = (
        WordCloud(init_opts=opts.InitOpts())
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[5, 100])
    )
    # return w.render_embed()
    return {
        'chart_data': w.dump_options_with_quotes(),
        'keyword': keyword,
        'max_num': str(max_num),
        'dialogs': msg_db.get_messages_by_keyword(wxid, keyword, num=5, max_len=12)
    }


def wordcloud_christmas(wxid, year='2023'):
    import jieba
    txt_messages = msg_db.get_messages_by_type(wxid, MsgType.TEXT, year)
    if not txt_messages:
        return {
            'wordcloud_chart_data': None,
            'keyword': "没有聊天你想分析啥",
            'max_num': '0',
            'dialogs': [],
            'total_num': 0,
        }
    text = ''.join(map(lambda x: x[7], txt_messages))
    total_msg_len = len(text)
    # 使用jieba进行分词，并加入停用词
    words = jieba.cut(text)
    # 统计词频
    word_count = Counter(words)
    # 过滤停用词
    stopwords_file = './app/data/stopwords.txt'
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords1 = set(stopword_file.read().splitlines())
    # 构建 FFmpeg 可执行文件的路径
    stopwords = set()
    stopwords_file = './app/resources/data/stopwords.txt'
    if not os.path.exists(stopwords_file):
        resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        stopwords_file = os.path.join(resource_dir, 'app', 'resources', 'data', 'stopwords.txt')
    with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
        stopwords = set(stopword_file.read().splitlines())
        stopwords = stopwords.union(stopwords1)

    filtered_word_count = {word: count for word, count in word_count.items() if len(word) > 1 and word not in stopwords}
    # 转换为词云数据格式
    data = [(word, count) for word, count in filtered_word_count.items()]
    # text_data = data
    data.sort(key=lambda x: x[1], reverse=True)

    text_data = data[:100] if len(data) > 100 else data
    # 创建词云图
    keyword, max_num = text_data[0]
    w = (
        WordCloud()
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[5, 40])
    )
    # return w.render_embed()
    dialogs = msg_db.get_messages_by_keyword(wxid, keyword, num=3, max_len=12, year_=year)

    return {
        'wordcloud_chart_data': w.dump_options_with_quotes(),
        'keyword': keyword,
        'keyword_max_num': str(max_num),
        'dialogs': dialogs,
        'total_num': total_msg_len,
    }


def calendar_chart(wxid, time_range=None):
    calendar_data = msg_db.get_messages_by_days(wxid, time_range)
    if not calendar_data:
        return {
            'chart_data': None,
            'calendar_chart_data': None,
            'chat_days': 0,
            # 'chart':c,
        }
    min_ = min(map(lambda x: x[1], calendar_data))
    max_ = max(map(lambda x: x[1], calendar_data))
    start_date_ = calendar_data[0][0]
    end_date_ = calendar_data[-1][0]
    print(start_date_, '---->', end_date_)
    calendar_days = (start_date_, end_date_)
    calendar_title = '和Ta的聊天情况'
    c = (
        Calendar()
        .add(
            "",
            calendar_data,
            calendar_opts=opts.CalendarOpts(range_=calendar_days)
        )
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                max_=max_,
                min_=min_,
                orient="horizontal",
                pos_bottom="0px",
                pos_left="0px",
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return {
        'chart_data': c.dump_options_with_quotes(),
        'calendar_chart_data': c.dump_options_with_quotes(),
        'chat_days': len(calendar_data),
        # 'chart':c,
    }


def month_count(wxid, time_range=None):
    """
    每月聊天条数
    """
    msg_data = msg_db.get_messages_by_month(wxid, time_range)
    y_data = list(map(lambda x: x[1], msg_data))
    x_axis = list(map(lambda x: x[0], msg_data))
    m = (
        Bar(init_opts=opts.InitOpts())
        .add_xaxis(x_axis)
        .add_yaxis("消息数量", y_data,
                   label_opts=opts.LabelOpts(is_show=True),
                   itemstyle_opts=opts.ItemStyleOpts(color="#ffae80"),
                   )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="逐月统计", subtitle=None),
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            yaxis_opts=opts.AxisOpts(
                name="消息数",
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=min(y_data),
                max_=max(y_data),
                dimension=1,  # 根据第2个维度（y 轴）进行映射
                is_piecewise=False,  # 是否分段显示
                range_color=["#ffbe7a", "#fa7f6f"],  # 设置颜色范围
                type_="color",
                pos_right="0%",
            ),
        )
    )
    return {
        'chart_data': m.dump_options_with_quotes(),
        # 'chart': m,
    }


def hour_count(wxid, is_Annual_report=False, year='2023'):
    """
    小时计数聊天条数
    """
    msg_data = msg_db.get_messages_by_hour(wxid, is_Annual_report, year)
    print(msg_data)
    y_data = list(map(lambda x: x[1], msg_data))
    x_axis = list(map(lambda x: x[0], msg_data))
    h = (
        Line(init_opts=opts.InitOpts())
        .add_xaxis(xaxis_data=x_axis)
        .add_yaxis(
            series_name="聊天频率",
            y_axis=y_data,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值", value=int(10)),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="聊天时段", subtitle=None),
            # datazoom_opts=opts.DataZoomOpts(),
            # toolbox_opts=opts.ToolboxOpts(),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False
            )
        )
    )

    return {
        'chart_data': h
    }


types = {
    '文本': 1,
    '图片': 3,
    '语音': 34,
    '视频': 43,
    '表情包': 47,
    '音乐与音频': 4903,
    '文件': 4906,
    '分享卡片': 4905,
    '转账': 492000,
    '音视频通话': 50,
    '拍一拍等系统消息': 10000,
}
types_ = {
    1: '文本',
    3: '图片',
    34: '语音',
    43: '视频',
    47: '表情包',
    4957: '引用消息',
    4903: '音乐与音频',
    4906: '文件',
    4905: '分享卡片',
    492000: '转账',
    50: '音视频通话',
    10000: '拍一拍等系统消息',
}


def get_weekday(timestamp):
    # 将时间戳转换为日期时间对象
    dt_object = datetime.fromtimestamp(timestamp)

    # 获取星期几，0代表星期一，1代表星期二，以此类推
    weekday = dt_object.weekday()
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[weekday]


def sender(wxid, time_range, my_name='', ta_name=''):
    msg_data = msg_db.get_messages(wxid, time_range)

    types_count = {}
    send_num = 0  # 发送消息的数量
    weekday_count = {}
    for message in msg_data:
        type_ = message[2]
        is_sender = message[4]
        subType = message[3]
        timestamp = message[5]
        weekday = get_weekday(timestamp)
        str_time = message[8]
        send_num += is_sender
        type_ = f'{type_}{subType:0>2d}' if subType != 0 else type_
        type_ = int(type_)
        if type_ in types_count:
            types_count[type_] += 1
        else:
            types_count[type_] = 1
        if weekday in weekday_count:
            weekday_count[weekday] += 1
        else:
            weekday_count[weekday] = 1
    receive_num = len(msg_data) - send_num
    data = [[types_.get(key), value] for key, value in types_count.items() if key in types_]
    if not data:
        return {
            'chart_data_sender': None,
            'chart_data_types': None,
            'chart_data_weekday': None,
        }
    p1 = (
        Pie()
        .add(
            "",
            data,
            center=["40%", "50%"],
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            title_opts=opts.TitleOpts(title="消息类型占比"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%",pos_top="20%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        # .render("./data/聊天统计/types_pie.html")
    )
    p2 = (
        Pie()
        .add(
            "",
            [[my_name, send_num], [ta_name, receive_num]],
            center=["40%", "50%"],
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            title_opts=opts.TitleOpts(title="双方消息占比"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%",pos_top="20%", orient="vertical"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}\n{d}%"))
        # .render("./data/聊天统计/pie_scroll_legend.html")
    )
    p3 = (
        Pie()
        .add(
            "",
            [[key,value] for key,value in weekday_count.items()],
            radius=["40%", "75%"],
        )
        .set_global_opts(
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            title_opts=opts.TitleOpts(title="星期分布图"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}\n{d}%"))
        # .render("./data/聊天统计/pie_weekdays.html")
    )
    return {
        'chart_data_sender': p2.dump_options_with_quotes(),
        'chart_data_types': p1.dump_options_with_quotes(),
        'chart_data_weekday': p3.dump_options_with_quotes(),
    }

if __name__ == '__main__':
    msg_db.init_database(path='../DataBase/Msg/MSG.db')
    # w = wordcloud('wxid_0o18ef858vnu22')
    # w_data = wordcloud('wxid_27hqbq7vx5hf22', True, '2023')
    # # print(w_data)
    # w_data['chart_data'].render("./data/聊天统计/wordcloud.html")
    wxid = 'wxid_0o18ef858vnu22'
    # data = month_count(wxid, time_range=None)
    # data['chart'].render("./data/聊天统计/month_count.html")
    # data = calendar_chart(wxid, time_range=None)
    # data['chart'].render("./data/聊天统计/calendar_chart.html")
    data = sender(wxid, time_range=None, my_name='发送', ta_name='接收')
    print(data)
