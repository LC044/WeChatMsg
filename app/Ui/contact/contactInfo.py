from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from app.person import Contact
from .analysis import analysis
from .contactInfoUi import Ui_Form
from .emotion import emotion
from .userinfo import userinfo


class ContactInfo(QWidget, Ui_Form):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''
    def __init__(self, wxid, parent=None):
        super(ContactInfo, self).__init__(parent)
        self.setupUi(self)
        self.contact = Contact(wxid)
        self.view_userinfo = userinfo.UserinfoController(self.contact)
        self.view_analysis = analysis.AnalysisController(wxid)
        self.view_emotion = emotion.EmotionController(wxid)
        self.btn_analysis.clicked.connect(self.analysis)
        self.init_ui()

    def init_ui(self):
        self.label_remark.setText(self.contact.conRemark)
        self.stackedWidget.addWidget(self.view_userinfo)
        self.stackedWidget.addWidget(self.view_analysis)
        self.stackedWidget.addWidget(self.view_emotion)
        self.stackedWidget.setCurrentWidget(self.view_userinfo)
        menu = QMenu(self)
        self.toDocxAct = QAction(QIcon('app/data/icons/word.svg'), '导出Docx', self)
        self.toCSVAct = QAction(QIcon('app/data/icons/csv.svg'), '导出CSV', self)
        self.toHtmlAct = QAction(QIcon('app/data/icons/html.svg'), '导出HTML', self)
        self.toolButton_output.setPopupMode(QToolButton.MenuButtonPopup)
        menu.addAction(self.toDocxAct)
        menu.addAction(self.toCSVAct)
        menu.addAction(self.toHtmlAct)
        self.toolButton_output.setMenu(menu)
        # self.toolButton_output.addSeparator()
        self.toHtmlAct.triggered.connect(self.output)
        self.toDocxAct.triggered.connect(self.output)
        self.toCSVAct.triggered.connect(self.output)

    def analysis(self):
        self.stackedWidget.setCurrentWidget(self.view_analysis)
        # 判断talkerId是否已经分析过了
        # 是：则清空其他界面，直接显示该界面
        # 否：清空其他界面，创建用户界面并显示
        if 'room' in self.contact.wxid:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return
        self.view_analysis.start()

    def output(self):
        return
