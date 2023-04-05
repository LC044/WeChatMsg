import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *

QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
from . import charts


class AnalysisController(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.ta_username = username
        # self.setWindowTitle('数据分析')
        # self.setWindowIcon(QIcon('./app/data/icon.png'))

        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet('''QWidget{background-color:rgb(255, 255, 255);}''')
        # self.setBackground()
        # self.resize(400, 300)
        self.center()
        self.setAttribute(Qt.WA_AttributeCount)
        self.label_01()
        self.Thread = LoadData(username)
        self.Thread.okSignal.connect(self.initUI)
        self.Thread.start()

    def center(self):  # 定义一个函数使得窗口居中显示
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))

    def label_01(self):
        self.label = QLabel(self)
        size = self.geometry()
        self.label.setGeometry(size.width() // 2, self.height() // 2, 100, 100)
        self.label.setToolTip("这是一个标签")
        self.m_movie()

    def m_movie(self):
        movie = QMovie("./app/data/bg.gif")
        self.label.setMovie(movie)
        movie.start()

    def initUI(self):
        self.label.setVisible(False)
        self.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')

        main_box = QVBoxLayout(self)
        main_box.setContentsMargins(0, 0, 0, 0)
        main_box.setSpacing(0)

        self.browser1 = QWebEngineView()
        self.browser1.load(QUrl('file:///data/聊天统计/title.html'))
        self.browser1.setMinimumSize(810, 60)
        self.browser1.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')
        self.browser2 = QWebEngineView()
        self.browser2.load(QUrl('file:///data/聊天统计/wordcloud.html'))
        self.browser2.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')
        # self.browser2.setMinimumWidth(810)
        self.browser2.setMinimumSize(810, 810)
        self.browser3 = QWebEngineView()
        self.browser3.load(QUrl('file:///data/聊天统计/time.html'))
        self.browser3.setMaximumSize(810, 100)
        self.browser3.adjustSize()
        self.browser4 = QWebEngineView()
        self.browser4.load(QUrl('http://www.baidu.com'))
        self.browser4.resize(800, 600)
        self.browser5 = QWebEngineView()
        self.browser5.load(QUrl('file:///data/聊天统计/chat_session.html'))
        # self.browser5.adjustSize()

        # self.browser5.resize(800, 600)
        self.browser6 = QWebEngineView()
        self.browser6.load(QUrl('file:///data/聊天统计/sports.html'))
        self.browser7 = QWebEngineView()
        self.browser7.load(QUrl('file:///data/聊天统计/month_num.html'))
        self.browser8 = QWebEngineView()
        self.browser8.load(QUrl('file:///data/聊天统计/calendar.html'))
        self.browser9 = QWebEngineView()
        self.browser9.load(QUrl('file:///data/聊天统计/msg_type_rate.html'))
        self.browser10 = QWebEngineView()
        self.browser10.load(QUrl('file:///data/聊天统计/send_recv_rate.html'))
        self.browser10.adjustSize()
        # self.browser10.
        main_box.addWidget(self.browser1)

        self.scrollArea = QScrollArea()
        self.scrollArea.setEnabled(True)
        self.scrollArea.adjustSize()

        scrollAreaContent = QWidget(self.scrollArea)
        scrollAreaContent.setStyleSheet('''QWidget{background-color:rgb(240, 240, 240);}''')

        Vlayout2 = QVBoxLayout()
        Vlayout2.setContentsMargins(0, 0, 0, 0)
        Vlayout2.setSpacing(0)

        Vlayout2.addWidget(self.browser3)
        Vlayout2.addWidget(self.browser2)

        Vlayout2.addWidget(self.browser8)
        Vlayout2.addWidget(self.browser6)
        Vlayout2.addWidget(self.browser5)
        Vlayout2.addWidget(self.browser7)

        Vlayout2.addWidget(self.browser9)
        Vlayout2.addWidget(self.browser10)
        scrollAreaContent.setLayout(Vlayout2)

        self.scrollArea.setWidget(scrollAreaContent)
        main_box.addWidget(self.scrollArea)
        main_box.setStretch(0, 1)
        main_box.setStretch(1, 10)
        self.setLayout(main_box)

    def setBackground(self):
        palette = QPalette()
        pix = QPixmap("./app/data/bg.png")
        pix = pix.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)  # 自适应图片大小
        palette.setBrush(self.backgroundRole(), QBrush(pix))  # 设置背景图片
        # palette.setColor(self.backgroundRole(), QColor(192, 253, 123))  # 设置背景颜色
        self.setPalette(palette)


class LoadData(QThread):
    """
    发送信息线程
    """
    okSignal = pyqtSignal(int)

    def __init__(self, ta_u, parent=None):
        super().__init__(parent)
        self.ta_username = ta_u

    def run(self):
        charts.chat_start_endTime(self.ta_username)
        charts.title(self.ta_username)
        charts.send_recv_rate(self.ta_username)
        charts.message_word_cloud(self.ta_username)
        charts.msg_type_rate(self.ta_username)
        charts.calendar_chart(self.ta_username)
        charts.month_num(self.ta_username)
        charts.sport(self.ta_username)
        charts.chat_session(self.ta_username)
        self.okSignal.emit(10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
