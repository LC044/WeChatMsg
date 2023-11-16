from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app import person
from app.DataBase.output_pc import Output
from app.Ui.Icon import Icon
from .contactInfoUi import Ui_Form
from .userinfo import userinfo


class ContactInfo(QWidget, Ui_Form):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''
    def __init__(self, contact, me: person.Me = None, parent=None):
        super(ContactInfo, self).__init__(parent)
        self.setupUi(self)
        self.contact = contact
        self.view_userinfo = userinfo.UserinfoController(self.contact)

        # self.btn_analysis.clicked.connect(self.analysis)
        # self.btn_emotion.clicked.connect(self.emotionale_Analysis)
        # self.btn_report.clicked.connect(self.annual_report)
        self.btn_back.clicked.connect(self.back)
        self.Me = me
        # self.
        self.init_ui()

    def init_ui(self):
        self.btn_back.setIcon(Icon.Back)
        self.btn_report.setIcon(Icon.Annual_Report_Icon)
        self.btn_analysis.setIcon(Icon.Analysis_Icon)
        self.btn_emotion.setIcon(Icon.Emotion_Icon)
        self.label_remark.setText(self.contact.remark)
        self.stackedWidget.addWidget(self.view_userinfo)
        self.stackedWidget.setCurrentWidget(self.view_userinfo)
        menu = QMenu(self)
        self.toDocxAct = QAction(Icon.ToDocx, '导出Docx', self)
        self.toCSVAct = QAction(Icon.ToCSV, '导出CSV', self)
        self.toHtmlAct = QAction(Icon.ToHTML, '导出HTML', self)
        self.toolButton_output.setPopupMode(QToolButton.MenuButtonPopup)
        self.toolButton_output.clicked.connect(self.toolButton_show)
        menu.addAction(self.toDocxAct)
        menu.addAction(self.toCSVAct)
        menu.addAction(self.toHtmlAct)
        self.toolButton_output.setMenu(menu)
        self.toolButton_output.setIcon(Icon.Output)
        # self.toolButton_output.addSeparator()
        self.toHtmlAct.triggered.connect(self.output)
        self.toDocxAct.triggered.connect(self.output)
        self.toCSVAct.triggered.connect(self.output)

    def toolButton_show(self):
        self.toolButton_output.showMenu()

    def analysis(self):
        self.stackedWidget.setCurrentWidget(self.view_analysis)
        if 'room' in self.contact.wxid:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return
        self.view_analysis.start()

    def annual_report(self):
        QMessageBox.warning(
            self,
            "提示",
            "敬请期待"
        )
        return
        # self.report = report.ReportController(self.contact)
        # self.report.show()

    def emotionale_Analysis(self):
        self.stackedWidget.setCurrentWidget(self.view_emotion)
        if 'room' in self.contact.wxid:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return
        self.view_emotion.start()

    def back(self):
        """
        将userinfo界面设置为可见，其他界面设置为不可见
        """
        self.stackedWidget.setCurrentWidget(self.view_userinfo)

    def output(self):
        """
        导出聊天记录
        :return:
        """
        self.stackedWidget.setCurrentWidget(self.view_userinfo)
        if self.sender() == self.toDocxAct:
            print('功能暂未实现')
            QMessageBox.warning(self,
                                "别急别急",
                                "马上就实现该功能"
                                )
            return
            self.outputThread = Output(self.Me, self.contact.wxid)
        elif self.sender() == self.toCSVAct:
            # QMessageBox.warning(self,
            #                     "别急别急",
            #                     "马上就实现该功能"
            #                     )
            # print('开始导出csv')
            # return
            self.outputThread = Output(self.contact, type_=Output.CSV)
            print('导出csv')
        elif self.sender() == self.toHtmlAct:
            print('功能暂未实现')
            QMessageBox.warning(self,
                                "别急别急",
                                "马上就实现该功能"
                                )
            return
        self.outputThread.progressSignal.connect(self.output_progress)
        self.outputThread.rangeSignal.connect(self.set_progressBar_range)
        self.outputThread.okSignal.connect(self.hide_progress_bar)
        self.outputThread.start()

    def hide_progress_bar(self, int):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Information)
        reply.setWindowTitle('OK')
        reply.setText(f"导出聊天记录成功\n在.\\data\\目录下")
        reply.addButton("确认", QMessageBox.AcceptRole)
        reply.addButton("取消", QMessageBox.RejectRole)
        api = reply.exec_()
        self.view_userinfo.progressBar.setVisible(False)

    def output_progress(self, value):
        self.view_userinfo.progressBar.setProperty('value', value)

    def set_progressBar_range(self, value):
        self.view_userinfo.progressBar.setVisible(True)
        self.view_userinfo.progressBar.setRange(0, value)
