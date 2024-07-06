from datetime import datetime

from PyQt5.QtCore import pyqtSignal, QUrl, QThread
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QToolButton, QMessageBox

from app.ui.Icon import Icon
from .contactInfoUi import Ui_Form
from .userinfo import userinfo
from ..menu.export_time_range import TimeRangeDialog
from ...DataBase import msg_db
from ...person import Contact, Me
from app.ui.contact.export.export_dialog import ExportDialog


class ContactInfo(QWidget, Ui_Form):
    """
    显示联系人信息
    """
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''
    def __init__(self, contact, parent=None):
        super(ContactInfo, self).__init__(parent)
        self.time_range = None
        self.setupUi(self)
        self.contact: Contact = contact
        self.view_userinfo = userinfo.UserinfoController(self.contact)
        self.btn_back.clicked.connect(self.back)
        self.init_ui()

    def init_ui(self):
        self.btn_back.setIcon(Icon.Back)
        self.btn_report.setIcon(Icon.Annual_Report_Icon)
        self.btn_analysis.setIcon(Icon.Analysis_Icon)
        self.btn_emotion.setIcon(Icon.Emotion_Icon)
        self.btn_report.clicked.connect(self.annual_report)
        self.btn_analysis.clicked.connect(self.analysis)
        self.btn_emotion.clicked.connect(self.emotionale_Analysis)
        self.stackedWidget.addWidget(self.view_userinfo)
        self.stackedWidget.setCurrentWidget(self.view_userinfo)
        menu = QMenu(self)
        self.toDocxAct = QAction(Icon.ToDocx, '导出Docx', self)
        self.toCSVAct = QAction(Icon.ToCSV, '导出CSV', self)
        self.toHtmlAct = QAction(Icon.ToHTML, '导出HTML', self)
        self.toTxtAct = QAction(Icon.ToTXT, '导出TXT', self)
        self.toAiTxtAct = QAction(Icon.ToTXT, '导出AI对话专用TXT', self)
        self.toJsonAct = QAction(Icon.ToTXT, '导出json', self)
        self.toolButton_output.setPopupMode(QToolButton.MenuButtonPopup)
        self.toolButton_output.clicked.connect(self.toolButton_show)
        menu.addAction(self.toDocxAct)
        menu.addAction(self.toCSVAct)
        menu.addAction(self.toHtmlAct)
        menu.addAction(self.toTxtAct)
        menu.addAction(self.toAiTxtAct)
        menu.addAction(self.toJsonAct)
        self.toolButton_output.setMenu(menu)
        self.toolButton_output.setIcon(Icon.Output)
        # self.toolButton_output.addSeparator()
        self.toHtmlAct.triggered.connect(self.output)
        self.toDocxAct.triggered.connect(self.output)
        self.toCSVAct.triggered.connect(self.output)
        self.toTxtAct.triggered.connect(self.output)
        self.toJsonAct.triggered.connect(self.output)
        self.toAiTxtAct.triggered.connect(self.output)

    def set_contact(self, contact: Contact):
        self.view_userinfo.set_contact(contact)
        self.contact = contact

    def toolButton_show(self):
        self.toolButton_output.showMenu()

    def analysis(self):
        # QDesktopServices.openUrl(QUrl("https://memotrace.cn/"))
        self.report_thread = ReportThread(self.contact)
        # self.report_thread.okSignal.connect(lambda x: QDesktopServices.openUrl(QUrl("http://127.0.0.1:21314")))
        self.report_thread.start()
        QDesktopServices.openUrl(QUrl(f"http://127.0.0.1:21314/charts/{self.contact.wxid}"))

    def annual_report(self):
        date_range = None
        chat_calendar = msg_db.get_messages_calendar(self.contact.wxid)
        if chat_calendar:
            start_time = datetime.strptime(chat_calendar[0], "%Y-%m-%d")
            end_time = datetime.strptime(chat_calendar[-1], "%Y-%m-%d")
            date_range = (start_time.date(), end_time.date())
        self.time_range_view = TimeRangeDialog(date_range=date_range, parent=self)
        self.time_range_view.date_range_signal.connect(self.set_time_range)
        self.time_range_view.show()
        if 'room' in self.contact.wxid:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return

    def set_time_range(self, time_range):
        self.time_range = time_range
        self.contact.save_avatar()
        Me().save_avatar()
        self.report_thread = ReportThread(self.contact, time_range)
        self.report_thread.start()
        QDesktopServices.openUrl(QUrl(f"http://127.0.0.1:21314/christmas/{self.contact.wxid}"))

    def emotionale_Analysis(self):
        QDesktopServices.openUrl(QUrl("https://memotrace.cn/"))

    def back(self):
        """
        将userinfo界面设置为可见，其他界面设置为不可见
        """
        return

    def output(self):
        """
        导出聊天记录
        :return:
        """
        self.stackedWidget.setCurrentWidget(self.view_userinfo)
        if self.sender() == self.toDocxAct:
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='docx', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toCSVAct:
            # self.outputThread = Output(self.contact, type_=Output.CSV)
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='csv', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toHtmlAct:
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='html', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toTxtAct:
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='txt', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toAiTxtAct:
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='ai_txt', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toJsonAct:
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='json', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果

class ReportThread(QThread):
    okSignal = pyqtSignal(bool)

    def __init__(self, contact, time_range=None):
        super().__init__()
        self.contact = contact
        self.time_range = time_range

    def run(self):
        from app.web_ui import web
        web.contact = self.contact
        web.time_range = self.time_range
        web.run(port='21314')
        self.okSignal.emit(True)
