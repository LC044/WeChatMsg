import json

from flask import Flask, render_template
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

from app.DataBase import msg_db
from app.analysis import analysis

app = Flask(__name__)


@app.route("/")
def index():
    # 创建一个简单的柱状图
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(["A", "B", "C", "D", "E"])
        .add_yaxis("Series", [5, 20, 36, 10, 75])
        .set_global_opts(title_opts=opts.TitleOpts(title="Flask and Pyecharts Interaction"))
    )

    # 将图表转换成 HTML
    chart_html = bar.render_embed()

    # 渲染模板，并传递图表的 HTML 到模板中
    return render_template("index.html", chart_html=chart_html)


@app.route("/index")
def index0():
    return render_template("index1.html")


@app.route('/home')
def home():
    data = {
        'sub_title': '二零二三年度报告',
        'avatar_path': "static/my_resource/avatar.png",
        'nickname': '司小远',
        'first_time': '2023-09-18 20:39:08',
    }
    return render_template('home.html', **data)


@app.route('/message_num')
def one():
    msg_db.init_database(path='../DataBase/Msg/MSG.db')
    wxid = 'wxid_0o18ef858vnu22'
    wxid = 'wxid_8piw6sb4hvfm22'
    # wxid = 'wxid_lltzaezg38so22'
    world_cloud_data = analysis.wordcloud(wxid)
    # 创建一个简单的柱状图
    with open('message_num_test.html','w',encoding='utf-8') as f:
        f.write(render_template('message_num.html', **world_cloud_data))
    return render_template('message_num.html', **world_cloud_data)


@app.route('/test')
def test():
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(["A", "B", "C", "D", "E"])
        .add_yaxis("Series", [5, 20, 36, 10, 75])
        .set_global_opts(title_opts=opts.TitleOpts(title="Flask and Pyecharts Interaction"))
    )
    return bar.dump_options_with_quotes()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
