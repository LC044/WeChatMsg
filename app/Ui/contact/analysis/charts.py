import os
import jieba
from pyecharts import options as opts
from pyecharts.charts import Pie, WordCloud, Calendar, Bar
from ....DataBase import data

data.mkdir(os.path.abspath('.') + '/data/聊天统计')

Type = {
    '1': '文字',
    '3': '图片',
    '43': '视频',
    '-1879048185': '微信运动排行榜',
    '5': '',
    '47': '表情包',
    '268445456': '撤回消息',
    '34': '语音',
    '419430449': '转账',
    '50': '语音电话',
    '100001': '领取红包',
    '10000': '消息已发出，但被对方拒收了。',
    '822083633': '回复消息',
    '922746929': '拍一拍',
    '1090519089': '文件',
    '318767153': '付款成功',
    '436207665': '发红包',
    '49': '分享链接'
}


def send_recv_rate(username):
    send_num = data.send_nums(username)
    recv_num = data.recv_nums(username)
    total_num = send_num + recv_num
    print(send_num, recv_num)
    c = (
        Pie(init_opts=opts.InitOpts(width="460px", height="240px"))
        .add(
            "",
            [
                ('发送', send_num), ('接收', recv_num)
            ],
            center=["40%", "50%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"信息发送接收",subtitle=f"总计：{total_num}条消息", pos_bottom="0%"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}:{d}%"),
        )
        .render("./data/聊天统计/send_recv_rate.html")
    )


def msg_type_rate(username):
    type_data = data.msg_type_num(username)
    type_data = sorted(type_data, key=lambda x: x[1], reverse=True)
    data1 = type_data[:4]
    data2 = sum(map(lambda x: x[1], type_data[4:]))
    print(type_data)
    new_data = []
    for t in data1:
        try:
            new_data.append((Type[str(t[0])], t[1]))
        except:
            new_data.append(('未知类型', t[1]))
    new_data.append(('其他', data2))

    c = (
        Pie(init_opts=opts.InitOpts(width="460px", height="240px"))
        .add(
            "",
            new_data
            ,
            center=["40%", "50%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"消息类型占比", pos_bottom="0%"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}:{d}%"),
        )
        .render("./data/聊天统计/msg_type_rate.html")
    )


def message_word_cloud(username):
    text = data.get_text(username)
    total_msg_len = len(text)
    word_list = jieba.cut(text)
    # word = " ".join(word_list)
    # print(word)
    stopwords = set()
    content = [line.strip() for line in open('./app/data/stopwords.txt', 'r', encoding='utf-8').readlines()]
    stopwords.update(content)
    wordcount = {}
    for word in jieba.cut(text):
        if len(word) > 1 and word not in stopwords:
            wordcount[word] = wordcount.get(word, 0) + 1
    text_data = sorted(wordcount.items(), key=lambda x: x[1], reverse=True)
    if len(text_data) > 100:
        text_data = text_data[:100]
    print(text_data)
    (
        WordCloud(init_opts=opts.InitOpts(width="900px", height="550px"))
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[20, 100])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"词云图", subtitle=f"总计{total_msg_len}字",
                title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
        .render("./data/聊天统计/wordcloud.html")
    )


def calendar_chart(username):
    msg_data = data.get_msg_by_days(username)
    min_ = min(map(lambda x: x[1], msg_data))
    max_ = max(map(lambda x: x[1], msg_data))
    c = (
        Calendar(init_opts=opts.InitOpts(width="460px", height="255px"))
        .add(
            "",
            msg_data,
            calendar_opts=opts.CalendarOpts(range_="2022")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="2022年聊天情况"),
            visualmap_opts=opts.VisualMapOpts(
                max_=max_,
                min_=min_,
                orient="horizontal",
                # is_piecewise=True,
                # pos_top="200px",
                pos_bottom="0px",
                pos_left="0px",
            ),
        )
        .render("./data/聊天统计/calendar.html")
    )


def month_num(username):
    """
    每月聊天条数
    """
    msg_data = data.get_msg_by_month(username, year='2022')
    y_data = list(map(lambda x: x[1], msg_data))
    x_axis = list(map(lambda x: x[0], msg_data))
    c = (
        Bar(init_opts=opts.InitOpts(width="440px", height="245px"))
        .add_xaxis(x_axis)
        .add_yaxis("消息数量", y_data)
        # .add_yaxis("商家B", Faker.values())
        .set_global_opts(
            title_opts=opts.TitleOpts(title="逐月聊天统计", subtitle=None),
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
        )
        .render("./data/聊天统计/month_num.html")
    )


if __name__ == '__main__':
    send_recv_rate('wxid_wt2vsktnu4z022')
