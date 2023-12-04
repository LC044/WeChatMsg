import json
import os
import sys

from flask import Flask, render_template, send_file
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

from app.DataBase import msg_db
from app.analysis import analysis
from app.person_pc import ContactPC, MePC

app = Flask(__name__)

wxid = ''
contact: ContactPC = None


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
        'avatar_path': contact.avatar_path,
        'nickname': contact.remark,
        'first_time': msg_db.get_first_time_of_message(contact.wxid)[1],
    }
    return render_template('home.html', **data)


@app.route('/wordcloud')
def one():
    wxid = contact.wxid
    # wxid = 'wxid_lltzaezg38so22'
    world_cloud_data = analysis.wordcloud(wxid)

    with open('wordcloud.html', 'w', encoding='utf-8') as f:
        f.write(render_template('wordcloud.html', **world_cloud_data))
    return render_template('wordcloud.html', **world_cloud_data)


@app.route('/test')
def test():
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(["A", "B", "C", "D", "E"])
        .add_yaxis("Series", [5, 20, 36, 10, 75])
        .set_global_opts(title_opts=opts.TitleOpts(title="Flask and Pyecharts Interaction"))
    )
    return bar.dump_options_with_quotes()


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
