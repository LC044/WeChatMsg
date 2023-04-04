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
        self.setStyleSheet('''QWidget{background-color:rgb(244, 244, 244);}''')

        main_box = QVBoxLayout(self)

        self.browser1 = QWebEngineView()
        self.browser1.load(QUrl('file:///data/聊天统计/title.html'))
        self.browser2 = QWebEngineView()
        self.browser2.load(QUrl('file:///data/聊天统计/wordcloud.html'))
        self.browser3 = QWebEngineView()
        self.browser3.load(QUrl('file:///data/聊天统计/time.html'))
        # self.browser3.resize(800, 600)
        self.browser4 = QWebEngineView()
        self.browser4.load(QUrl('http://www.baidu.com'))
        # self.browser4.resize(800, 600)
        self.browser5 = QWebEngineView()
        self.browser5.load(QUrl('file:///data/聊天统计/chat_session.html'))
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

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setEnabled(True)
        self.scrollArea.adjustSize()
        self.scrollArea.setWidgetResizable(False)
        scrollAreaContent = QWidget(self.scrollArea)
        Vlayout2 = QVBoxLayout(scrollAreaContent)

        # splitter2 = QSplitter(Qt.Vertical)
        # splitter2.addWidget(self.browser2)
        # # splitter2.resize(800, 600)
        # Vlayout2.addWidget(splitter2)
        #
        # splitter3 = QSplitter(Qt.Vertical)
        # splitter3.addWidget(self.browser3)
        # Vlayout2.addWidget(splitter3)
        #
        # splitter4 = QSplitter(Qt.Vertical)
        # splitter4.addWidget(self.browser4)
        # Vlayout2.addWidget(splitter4)
        #
        # splitter5 = QSplitter(Qt.Vertical)
        # splitter5.addWidget(self.browser6)
        # Vlayout2.addWidget(splitter5)

        # Vlayout2.addWidget(self.browser3, stretch=1)
        # Vlayout2.addWidget(self.browser6, stretch=2)
        # Vlayout2.addWidget(self.browser5, stretch=3)
        # Vlayout2.addWidget(self.browser7, stretch=4)
        # Vlayout2.addWidget(self.browser8, stretch=5)
        # Vlayout2.addWidget(self.browser9, stretch=6)
        Vlayout2.addWidget(self.browser10, stretch=7)

        # Vlayout2.setStretch(0, 1)
        # Vlayout2.setStretch(1, 10)

        scrollAreaContent.setLayout(Vlayout2)
        # self.scrollArea.setWidget(scrollAreaContent)
        self.scrollArea.setWidget(self.browser9)
        main_box.addWidget(self.browser10)
        main_box.addWidget(self.scrollArea)
        main_box.setStretch(0, 1)
        main_box.setStretch(1, 10)
        '''
        splitter1 = QSplitter(Qt.Vertical)
        splitter2 = QSplitter(Qt.Horizontal)
        splitter3 = QSplitter(Qt.Horizontal)
        splitter4 = QSplitter(Qt.Vertical)
        splitter5 = QSplitter(Qt.Horizontal)
        splitter6 = QSplitter(Qt.Vertical)
        splitter7 = QSplitter(Qt.Vertical)
        splitter8 = QSplitter(Qt.Vertical)
        splitter9 = QSplitter(Qt.Vertical)

        splitter1.addWidget(self.browser1)
        splitter1.addWidget(splitter2)
        splitter1.setSizes([1, 13])

        splitter2.addWidget(splitter6)
        splitter2.addWidget(splitter3)
        splitter2.setSizes([1, 3])

        splitter3.addWidget(splitter4)
        splitter3.addWidget(splitter8)
        splitter3.setSizes([2, 1])

        splitter4.addWidget(splitter5)
        splitter4.addWidget(self.browser2)
        splitter4.setSizes([2, 13])

        splitter5.addWidget(self.browser3)
        # splitter5.addWidget(self.browser4)

        splitter6.addWidget(self.browser5)
        splitter6.addWidget(splitter7)
        splitter6.setSizes([1, 2])

        splitter7.addWidget(self.browser6)
        splitter7.addWidget(self.browser7)

        splitter8.addWidget(self.browser8)
        splitter8.addWidget(splitter9)
        splitter8.setSizes([1, 2])

        splitter9.addWidget(self.browser9)
        splitter9.addWidget(self.browser10)
'''
        # main_box.addWidget(splitter1)
        self.setLayout(main_box)
        # self.setLayout(Vlayout1)

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
