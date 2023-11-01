import os

import jieba
import pandas as pd
import xmltodict
from pyecharts import options as opts
from pyecharts.charts import Pie, WordCloud, Calendar, Bar, Line, Timeline, Grid

from ....DataBase import data

# from app.DataBase import data

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
charts_width = 800
charts_height = 450
wordcloud_width = 780
wordcloud_height = 720


def send_recv_rate(username):
    send_num = data.send_nums(username)
    recv_num = data.recv_nums(username)
    total_num = send_num + recv_num
    print(send_num, recv_num)
    c = (
        Pie(init_opts=opts.InitOpts(
            # bg_color='rgb(240,240,240)',
            width=f"{charts_width}px",
            height=f"{charts_height}px")
        )
        .add(
            "",
            [
                ('发送', send_num), ('接收', recv_num)
            ],
            center=["40%", "50%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"信息发送接收", subtitle=f"总计：{total_num}条消息", pos_bottom="0%"),
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
        Pie(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
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
    # print(text_data)
    (
        WordCloud(init_opts=opts.InitOpts(width=f"{wordcloud_width}px", height=f"{wordcloud_height}px"))
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[20, 100])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"词云图", subtitle=f"总计{total_msg_len}字",
                title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            legend_opts=opts.LegendOpts(is_show=False)
        )
        .render("./data/聊天统计/wordcloud.html")
    )


def calendar_chart(username):
    msg_data = data.get_msg_by_days(username, year='2022')
    if not msg_data:
        return False
    min_ = min(map(lambda x: x[1], msg_data))
    max_ = max(map(lambda x: x[1], msg_data))
    c = (
        Calendar(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
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
            legend_opts=opts.LegendOpts(is_show=False)
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
        Bar(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
        .add_xaxis(x_axis)
        .add_yaxis("消息数量", y_data)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="逐月统计", subtitle=None),
            datazoom_opts=opts.DataZoomOpts(),
            toolbox_opts=opts.ToolboxOpts(),
        )
        .render("./data/聊天统计/month_num.html")
    )


def chat_session(username):
    msg_data = data.get_msg_by_hour(username)
    x_axis = list(map(lambda x: x[0], msg_data))
    y_data = list(map(lambda x: x[1], msg_data))
    # print(x_axis)
    # print(y_data)
    # max_ = max(y_data)
    c = (
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
        .render("./data/聊天统计/chat_session.html")
    )


def sport(username):
    sports = data.get_sport()
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
    try:
        # todo 可能没有运动信息
        df = pd.DataFrame({'ranks': ranks, 'score': steps, 'date': date}, index=date)
        months = pd.date_range(date[0], date[-1], freq='M')
    except:
        months = []
    tl = Timeline(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
    tl.add_schema(is_auto_play=True)
    for i in range(len(months) - 1):
        da = df[(months[i + 1].strftime("%Y-%m-%d") >= df['date']) & (df['date'] > months[i].strftime("%Y-%m-%d"))]
        bar = (
            Bar(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
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
                    is_show=False,
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
                title_opts=opts.TitleOpts(
                    title="{}".format(months[i + 1].strftime("%Y-%m")),

                ),
                # legend_opts=opts.LegendOpts(is_show=False),
                yaxis_opts=opts.AxisOpts(is_inverse=True),
                # xaxis_opts=opts.AxisOpts(type_='time')
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    is_show=False
                )
            )
        )
        # init_opts = opts.InitOpts(width="400px", height="235px")
        line = (
            Line(init_opts=opts.InitOpts(width=f"{charts_width}px", height=f"{charts_height}px"))
            .add_xaxis(list(da['date']))
            .add_yaxis(
                "排名",
                list(da['ranks']),
                yaxis_index=0,
                color="#675bba",
                # label_opts=opts.LabelOpts(is_show=False),

            )
            .set_global_opts(
                yaxis_opts=opts.AxisOpts(is_inverse=True),
                # xaxis_opts=opts.AxisOpts(type_='time')
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    is_show=False
                )
            )
        )
        bar.overlap(line)
        grid = Grid()
        grid.add(bar, opts.GridOpts(pos_left="5%", pos_right="11%"), is_control_axis_index=True)
        # grid.render("grid_multi_yaxis.html")
        tl.add(grid, "{}".format(months[i].strftime("%Y-%m")))
    tl.render("./data/聊天统计/sports.html")
    return {
        username: {
            'ranks': ranks,
            'score': steps,
            'date': date,
        }
    }


def chat_start_endTime(username):
    start_time = data.get_msg_start_time(username)
    end_time = data.get_msg_end_time(username)
    year = start_time[:4]
    month = start_time[5:7]
    day = start_time[8:10]
    hour = start_time[11:13]
    minute = start_time[14:16]
    second = start_time[17:]
    html = '''
    <html>
<head>
    <meta charset="UTF-8">
    <title>聊天时间</title>
    <style>
/* 倒计时开始 */
.gn_box {
padding: 0px 0px;
margin-bottom:0px;
text-align: center;
background-color: #fff;
}
#t_d{
color: #982585;
font-size: 18px;
}
#t_h{
color: #8f79c1;
font-size: 18px;
}
#t_m{
color: #65b4b5;
font-size: 18px;
}
#t_s{
color: #83caa3;
font-size: 18px;
}
#text{
color: #E80017;
font-size: 18px;
}
    </style>
    <!--倒计时开始-->
</head>
<body>
<div class="gn_box">
    <h1>
        <font color="#E80017">第</font><font color="#D1002E">一次</font><font color="#BA0045">聊天</font><font
            color="#A3005C">发生</font><font color="#8C0073">在</font>
        <font color="#75008A">%s</font><font color="#5E00A1">-</font><font color="#4700B8">%s</font><font
            color="#3000CF"> %s</font><font color="#1900E6">:%s</font><font color="#0200FD">:%s</font>
    </h1>
    <center>
        <div id="CountMsg" class="HotDate">
            <span id="text">距今已有</span>
            <span id="t_d">626 天</span>
            <span id="t_h">6 时</span>
            <span id="t_m">26 分</span>
            <span id="t_s">26 秒</span>
        </div>
    </center>
</div>
<!--倒计时结束-->
<script type="text/javascript"> function getRTime() {
var EndTime = new Date('%s');
var NowTime = new Date();
var t = NowTime.getTime()-EndTime.getTime();
var d = Math.floor(t / 1000 / 60 / 60 / 24);
var h = Math.floor(t / 1000 / 60 / 60 %% 24);
var m = Math.floor(t / 1000 / 60 %% 60);
var s = Math.floor(t / 1000 %% 60);
document.getElementById("t_d").innerHTML = d + " 天";
document.getElementById("t_h").innerHTML = h + " 时";
document.getElementById("t_m").innerHTML = m + " 分";
document.getElementById("t_s").innerHTML = s + " 秒";
}
setInterval(getRTime, 1000);
</script>
</body>
</html>
    ''' % (year, month + '-' + day, hour, minute, second, start_time)
    print(year, month, day, hour, minute, second)
    with open('./data/聊天统计/time.html', 'w', encoding='utf-8') as f:
        f.write(html)


def title(username):
    conRemark = data.get_conRemark(username)
    avatar = data.get_avator(username)
    html = '''
    <html>
<head>
    <meta charset="UTF-8">
    <title>聊天时间</title>
    <style>
/* 倒计时开始 */
.gn_box {
padding: 0px 0px;
margin-bottom: 0px;
text-align: center;
background-color: #fff;
}
#t_d{
color: #982585;
font-size: 18px;
}
#t_h{
color: #8f79c1;
font-size: 18px;
}
#t_m{
color: #65b4b5;
font-size: 18px;
}
#t_s{
color: #83caa3;
font-size: 18px;
}
#text{
color: #E80017;
font-size: 18px;
}
#conRemark{
   color: #A3005C;
   font-size: 28px;
}
#table {
    width: 600px; height: 100px;//可随意
    position: absolute; left: 0; top: 0; right: 0; bottom: 0;
    margin: auto;    /* 有了这个就自动居中了 */
}
    </style>
    <!--倒计时开始-->
</head>
<body>
<div class="gn_box">
    <table align="center" style="margin:0px auto;">
        <tr valign="middle">
            <td valign="middle">
                <table>
                    <tr>
                        <td>
                            <img src="../../../%s" height="40" width="40"
                                 alt="Avatar"/>
                        </td>
                    </tr>
                </table>
            </td>
            <td align="center" valign="middle">
                <table>
                    <tr>
                        <td>
                            <font id="conRemark">%s</font>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <div>
        <span>

        </span>
        <span></span>
    </div>
</div>
</body>
</html>
    ''' % (avatar, conRemark)
    print('头像地址', avatar)
    with open('./data/聊天统计/title.html', 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == '__main__':
    # send_recv_rate('wxid_wt2vsktnu4z022')
    sport('wxid_wt2vsktnu4z022')
