from PyQt5.QtCore import pyqtSignal, QUrl, QThread
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QToolButton, QMessageBox, QDialog

from app.DataBase.output_pc import Output
from app.ui.Icon import Icon
from .contactInfoUi import Ui_Form
from .userinfo import userinfo
from ...person import ContactPC, MePC
from .export_dialog import ExportDialog


class ContactInfo(QWidget, Ui_Form):
    exitSignal = pyqtSignal()
    urlSignal = pyqtSignal(QUrl)

    # username = ''
    def __init__(self, contact, parent=None):
        super(ContactInfo, self).__init__(parent)
        self.setupUi(self)
        self.contact: ContactPC = contact
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
        self.toolButton_output.setPopupMode(QToolButton.MenuButtonPopup)
        self.toolButton_output.clicked.connect(self.toolButton_show)
        menu.addAction(self.toDocxAct)
        menu.addAction(self.toCSVAct)
        menu.addAction(self.toHtmlAct)
        menu.addAction(self.toTxtAct)
        self.toolButton_output.setMenu(menu)
        self.toolButton_output.setIcon(Icon.Output)
        # self.toolButton_output.addSeparator()
        self.toHtmlAct.triggered.connect(self.output)
        self.toDocxAct.triggered.connect(self.output)
        self.toCSVAct.triggered.connect(self.output)
        self.toTxtAct.triggered.connect(self.output)

    def toolButton_show(self):
        self.toolButton_output.showMenu()

    def analysis(self):
        QMessageBox.warning(self,
                            "别急别急",
                            "马上就实现该功能"
                            )
        return
        self.stackedWidget.setCurrentWidget(self.view_analysis)
        if 'room' in self.contact.wxid:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return
        self.view_analysis.start()

    def annual_report(self):
        if 'room' in self.contact.wxid:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return
        self.contact.save_avatar()
        MePC().save_avatar()
        self.report_thread = ReportThread(self.contact)
        self.report_thread.okSignal.connect(lambda x: QDesktopServices.openUrl(QUrl("http://127.0.0.1:21314")))
        self.report_thread.start()
        QDesktopServices.openUrl(QUrl("http://127.0.0.1:21314/christmas"))

    def emotionale_Analysis(self):
        if 'room' in self.contact.wxid:
            QMessageBox.warning(
                self, '警告',
                '暂不支持群组'
            )
            return
        QMessageBox.warning(self,
                            "别急别急",
                            "马上就实现该功能"
                            )
        return
        self.stackedWidget.setCurrentWidget(self.view_emotion)

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
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='docx', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toCSVAct:
            # self.outputThread = Output(self.contact, type_=Output.CSV)
            dialog = ExportDialog(self.contact,title='选择导出的消息类型', file_type='csv', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toHtmlAct:
            dialog = ExportDialog(self.contact,title='选择导出的消息类型', file_type='html', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果
        elif self.sender() == self.toTxtAct:
            dialog = ExportDialog(self.contact, title='选择导出的消息类型', file_type='txt', parent=self)
            result = dialog.exec_()  # 使用exec_()获取用户的操作结果

    def hide_progress_bar(self, int):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Information)
        reply.setWindowTitle('OK')
        reply.setText(f"导出聊天记录成功\n在./data/目录下(跟exe文件在一起)")
        reply.addButton("确认", QMessageBox.AcceptRole)
        reply.addButton("取消", QMessageBox.RejectRole)
        api = reply.exec_()
        self.view_userinfo.progressBar.setVisible(False)

    def output_progress(self, value):
        self.view_userinfo.progressBar.setProperty('value', value)

    def set_progressBar_range(self, value):
        self.view_userinfo.progressBar.setVisible(True)
        self.view_userinfo.progressBar.setRange(0, value)


class ReportThread(QThread):
    okSignal = pyqtSignal(bool)

    def __init__(self, contact):
        super().__init__()
        self.contact = contact

    def run(self):
        from app.web_ui import web
        web.contact = self.contact
        web.run(port='21314')
        self.okSignal.emit(True)
