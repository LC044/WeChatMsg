from collections import Counter
from datetime import datetime
import re 

from PyQt5.QtCore import QFile, QTextStream, QIODevice

import sys

sys.path.append('.')

from app.DataBase import msg_db, MsgType
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Calendar, Bar, Line
from app.resources import resource_rc
from app.util.emoji import get_emoji

var = resource_rc.qt_resource_name
charts_width = 800
charts_height = 450
wordcloud_width = 780
wordcloud_height = 720


def wordcloud(wxid, year='all', who='1'):
    import jieba
    txt_messages = msg_db.get_messages_by_type(wxid, MsgType.TEXT, year)
    if not txt_messages:
        return {
            'chart_data': None,
            'keyword': "没有聊天你想分析啥",
            'max_num': "0",
            'dialogs': []
        }
    # text = ''.join(map(lambda x: x[7], txt_messages))
    text = ''.join(map(lambda x: x[7] if x[4] == int(who) else '', txt_messages))  # 1“我”说的话，0“Ta”说的话

    total_msg_len = len(text)
    # 使用jieba进行分词，并加入停用词
    words = jieba.cut(text)
    # 统计词频
    word_count = Counter(words)
    # 过滤停用词
    stopwords_file = './app000/data/stopwords.txt'
    try:
        with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
            stopwords = set(stopword_file.read().splitlines())
    except:
        file = QFile(':/data/stopwords.txt')
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            stream = QTextStream(file)
            stream.setCodec('utf-8')
            content = stream.readAll()
            file.close()
            stopwords = set(content.splitlines())
    filtered_word_count = {word: count for word, count in word_count.items() if len(word) > 1 and word not in stopwords}

    # 转换为词云数据格式
    data = [(word, count) for word, count in filtered_word_count.items()]
    # text_data = data
    data.sort(key=lambda x: x[1], reverse=True)

    text_data = data[:100] if len(data) > 100 else data
    # 创建词云图
    keyword, max_num = text_data[0]
    w = (
        WordCloud(init_opts=opts.InitOpts(width=f"{wordcloud_width}px", height=f"{wordcloud_height}px"))
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[5, 40])
    )
    # return w.render_embed()
    return {
        'chart_data': w.dump_options_with_quotes(),
        'keyword': keyword,
        'max_num': str(max_num),
        'dialogs': msg_db.get_messages_by_keyword(wxid, keyword, num=5, max_len=12)
    }


def calendar_chart(wxid, year='all'):
    data_length = msg_db.get_messages_length_with_ta(wxid, year)  # 获取和他的聊天条数
    print(f'聊天总数：{data_length}')
    calendar_data = msg_db.get_messages_by_days(wxid, year)

    if not calendar_data:
        return False
    min_ = min(map(lambda x: x[1], calendar_data))
    max_ = max(map(lambda x: x[1], calendar_data))
    max_date = next(x[0] for x in calendar_data if x[1] == max_)
    date_obj = datetime.strptime(max_date, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%Y年%m月%d日")
    print(formatted_date)

    start_date_ = calendar_data[0][0]
    end_date_ = calendar_data[-1][0]
    print(start_date_, '---->', end_date_)

    # 计算两个日期之间的天数差
    date1 = datetime.strptime(str(start_date_), "%Y-%m-%d")
    date2 = datetime.strptime(str(end_date_), "%Y-%m-%d")
    date_num = (date2 - date1).days + 1
    print(date_num)

    if year != 'all':
        calendar_days = year
        calendar_title = f'{year}年聊天情况'
    else:
        calendar_days = (start_date_, end_date_)
        calendar_title = '和Ta的聊天情况'
    c = (
        Calendar(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
        .add(
            "",
            calendar_data,
            calendar_opts=opts.CalendarOpts(range_=calendar_days)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=calendar_title),
            visualmap_opts=opts.VisualMapOpts(
                max_=max_,
                min_=min_,
                orient="horizontal",
                # is_piecewise=True,
                # pos_top="200px",
                pos_bottom="0px",
                pos_left="0px",
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return {
        'chart_data': c.dump_options_with_quotes(),
        'data_length': data_length,  # 和xx的聊天记录总数
        'max_date': formatted_date,
        'max_num': str(max_),
        'date_num': str(date_num),
        'dialogs': msg_db.get_first_time_of_message(wxid)  # 非年度报告使用
    }


def month_count(wxid, year='all'):
    """
    每月聊天条数
    """
    msg_data = msg_db.get_messages_by_month(wxid, year)
    y_data = list(map(lambda x: x[1], msg_data))
    x_axis = list(map(lambda x: x[0], msg_data))
    # 获取聊天的月数
    if year != 'all':
        if all(y > 0 for y in y_data):
            conc = "我们这一年每个月都有在聊天"
        else:
            months_with_chat = sum(1 for y in y_data if y > 0)
            conc = f"我们这一年有{months_with_chat}个月都在聊天"
    else:
        months_with_chat = sum(1 for y in y_data if y > 0)
        conc = f"我们有{months_with_chat}个月都在聊天"
    print("聊天月数", conc)
    # 月平均聊天条数
    average_num = round(sum(y_data)/12)
    print(f'月平均聊天条数:{average_num}')
    # 月聊天条数最大值和最小值
    max_num = max(y_data)
    max_num_month = next(x[0] for x in msg_data if x[1] == max_num)
    min_num = min(y_data)
    min_num_month = next(x[0] for x in msg_data if x[1] == max_num)
    print(f'{max_num_month}月聊天条数:{max_num},{min_num_month}月聊天条数:{min_num}')

    m = (
        Bar(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
        .add_xaxis(x_axis)
        .add_yaxis("消息数量", y_data,
                   label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(color="skyblue"),
                   )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="逐月统计", subtitle=None),
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
            visualmap_opts=opts.VisualMapOpts(
                min_=min(y_data),
                max_=max(y_data),
                dimension=1,  # 根据第2个维度（y 轴）进行映射
                is_piecewise=False,  # 是否分段显示
                range_color=["#66ccff", "#003366"],  # 设置颜色范围
                type_="color",
                pos_right="0%",
            ),
        )
    )

    return {
        'chart_data': m.dump_options_with_quotes(),
        'txt': conc,
        'month_average_num': average_num,
        'max_num_month': max_num_month,
        'max_num': max_num,
        'min_num_month': max_num_month,
        'min_num': min_num
    }


def hour_count(wxid, year='all'):
    """
    小时计数聊天条数
    """
    msg_data = msg_db.get_messages_by_hour(wxid, year)
    print(msg_data)
    y_data = list(map(lambda x: x[1], msg_data))
    x_axis = list(map(lambda x: x[0], msg_data))
    max_num = max(y_data)
    max_num_hour = next(x[0] for x in msg_data if x[1] == max_num)
    print(f'{max_num_hour}：{max_num}')
    h = (
        Line(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
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
    late_data = msg_db.get_lateDay_messages(wxid, year)  # 最晚的消息记录
    early_data = msg_db.get_earlyDay_messages(wxid, year)  # 早上最早的记录
    print(late_data)
    print(early_data)
    return {
        'chart_data': h.dump_options_with_quotes(),
        'max_num_hour': max_num_hour,
        'max_num': max_num,
        'late_data': late_data,
        'early_data': early_data
    }


def emoji_count(wxid, year='all'):
    # 最常发的表情
    txt_messages = msg_db.get_messages_by_type(wxid, MsgType.TEXT, year)
    me_txt_messages = ''.join(map(lambda x: x[7] if x[4] == 1 else '', txt_messages))
    ta_txt_messages = ''.join(map(lambda x: x[7] if x[4] == 0 else '', txt_messages))

    pattern = re.compile(r"\[.+?\]")
    MeEmoji = re.findall(pattern, me_txt_messages)
    TaEmoji = re.findall(pattern, ta_txt_messages)

    # 按照出现次数统计
    MeEmoji_num = Counter(MeEmoji)
    TaEmoji_num = Counter(TaEmoji)

    # 打印统计结果
    ta_total_emoji_num = len(TaEmoji)
    me_total_emoji_num = len(MeEmoji)
    ta_max_emoji = TaEmoji_num.most_common(10)
    me_max_emoji = MeEmoji_num.most_common(10)
    print("ta发的表情数：", len(TaEmoji))
    print("我发的表情数：", len(MeEmoji))
    print("---"*10)
    print("ta最常用的 10 个表情：\n", TaEmoji_num.most_common(10))
    print("---"*10)
    print("我最常用的 10 个表情：\n", MeEmoji_num.most_common(10))

    # 最常发的表情包图片
    MeImgList, TaImgList = msg_db.get_emoji_Img(wxid, year)
    MeImgDict = {}
    TaImgDict = {}
    for xml, num in MeImgList:
        MeImgDict[get_emoji(xml)] = num
    for xml, num in TaImgList:
        TaImgDict[get_emoji(xml)] = num
    return {
        'ta_total_emoji_num': ta_total_emoji_num,
        'me_total_emoji_num': me_total_emoji_num,
        'ta_max_emoji': ta_max_emoji,
        'me_max_emoji': me_max_emoji,
        'MeImgDict': MeImgDict,  # 三张图片地址+数量，字典格式，path为key
        'MeImgDict': MeImgDict
    }


class Analysis:
    pass


if __name__ == '__main__':
    msg_db.init_database(path='../DataBase/Msg/MSG.db')
    # w = wordcloud('wxid_0o18ef858vnu22')
    w_data = wordcloud('wxid_27hqbq7vx5hf22', '2023')
    # # print(w_data)
    # # w['chart_data'].render("./data/聊天统计/wordcloud.html")
    c = calendar_chart('wxid_27hqbq7vx5hf22', '2023')
    # c['chart_data'].render("./data/聊天统计/calendar.html")
    # # print('c:::', c)
    m = month_count('wxid_27hqbq7vx5hf22', False, '2023')
    # m['chart_data'].render("./data/聊天统计/month_num.html")
    # h = hour_count('wxid_27hqbq7vx5hf22')
    # h['chart_data'].render("./data/聊天统计/hour_count.html")

    h = emoji_count('wxid_27hqbq7vx5hf22')
    # h['chart_data'].render("./data/聊天统计/hour_count.html")
