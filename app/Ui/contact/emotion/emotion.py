import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line

from app.log import log
from ....DataBase import data


def load_data(wxid):
    message_data = data.get_text_by_num(wxid, 1)
    df = pd.DataFrame(message_data, columns=['message', 'date'])
    # print(df)
    d = df.groupby('date')
    for key, value in d:
        yield key, value['message'].values


import snownlp


@log
def emotion_analysis(wxid):
    dates = []
    emotions = []
    for date, messages in load_data(wxid):
        dates.append(date)
        s = 0
        for msg in messages:
            val = snownlp.SnowNLP(msg).sentiments
            s += val
        emotions.append(s / len(messages))
    emotions = np.array(emotions)
    emotions = np.around(emotions, 3) * 100
    emotions = np.around(emotions, 1)
    return dates, emotions


@log
def plot_emotion(wxid):
    """
    画图
    """
    datas, emotions = emotion_analysis(wxid)  # 获取数据
    max_ = max(emotions)
    min_ = min(emotions)
    c = (
        Line()
        .add_xaxis(
            xaxis_data=datas,
        )
        .add_yaxis(
            series_name="情感趋势",
            is_smooth=True,
            y_axis=emotions,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值", value=int(max_ * 100) / 100),
                    opts.MarkPointItem(type_="min", name="最小值", value=int(min_ * 100) / 100),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        )
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                max_=max_,
                min_=min_,
            ),
            xaxis_opts=opts.AxisOpts(
                type_='time'
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True, link=[{"xAxisIndex": "all"}]
            ),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .render("./data/聊天统计/emotion_chart.html")
    )


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *

from . import emotionUi


class EmotionController(QWidget, emotionUi.Ui_Dialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.ta_username = username

        # self.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')
        # 加载动画
        self.center()
        self.label_01()

    def center(self):  # 定义一个函数使得窗口居中显示
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))

    def label_01(self):
        w = self.size().width()
        h = self.size().height()
        self.label = QLabel(self)
        self.label.setGeometry(w // 2, h // 2, 100, 100)
        self.label.setToolTip("这是一个标签")
        self.m_movie()

    def m_movie(self):
        movie = QMovie("./app/data/bg.gif")
        self.label.setMovie(movie)
        movie.start()

    def initUI(self):
        self.label.setVisible(False)
        # self.setStyleSheet('''QWidget{background-color:rgb(244, 244, 244);}''')
        main_box = QHBoxLayout(self)
        self.browser1 = QWebEngineView()
        self.browser1.load(QUrl('file:///data/聊天统计/emotion_chart.html'))
        # self.browser1.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')

        splitter1 = QSplitter(Qt.Vertical)

        splitter1.addWidget(self.browser1)
        main_box.addWidget(splitter1)
        self.setLayout(main_box)

    def setBackground(self):
        palette = QPalette()
        pix = QPixmap("./app/data/bg.png")
        pix = pix.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)  # 自适应图片大小
        palette.setBrush(self.backgroundRole(), QBrush(pix))  # 设置背景图片
        # palette.setColor(self.backgroundRole(), QColor(192, 253, 123))  # 设置背景颜色
        self.setPalette(palette)

    def start(self):
        # 防止卡死，新建线程处理数据
        self.Thread = LoadData(self.ta_username)
        self.Thread.okSignal.connect(self.initUI)
        self.Thread.start()


class LoadData(QThread):
    """
    发送信息线程
    """
    okSignal = pyqtSignal(int)

    def __init__(self, ta_u, parent=None):
        super().__init__(parent)
        self.ta_username = ta_u

    def run(self):
        plot_emotion(self.ta_username)
        self.okSignal.emit(10)


if __name__ == '__main__':
    # wxid = 'wxid_8piw6sb4hvfm22'
    wxid = 'wxid_wt2vsktnu4z022'
    load_data(wxid)
