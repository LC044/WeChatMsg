import os
import sys
import time
from datetime import datetime, timedelta
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDialog, QVBoxLayout, QCheckBox, QHBoxLayout, \
    QProgressBar, QLabel, QMessageBox, QComboBox

from app.DataBase import msg_db
from app.components import ScrollBar
from app.config import output_dir
from app.ui.menu.export_time_range import TimeRangeDialog
from .exportUi import Ui_Dialog
from app.DataBase.output import Output

types = {
    '文本': 1,
    '图片': 3,
    '语音': 34,
    '视频': 43,
    '表情包': 47,
    '音乐与音频': 4903,
    '文件': 4906,
    '分享卡片': 4905,
    '转账': 492000,
    '音视频通话': 50,
    '拍一拍等系统消息': 10000,
}
Stylesheet = """
"""
class EmittingStr(QObject):
    textWritten = pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))

class ExportDialog(QDialog, Ui_Dialog):
    def __init__(self, contact=None, title="选择导出的类型", file_type="csv", parent=None):
        super(ExportDialog, self).__init__(parent)
        self.select_all_flag = False
        self.setupUi(self)
        self.setStyleSheet(Stylesheet)
        # 下面将输出重定向到textBrowser中
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
        scroll_bar = ScrollBar()
        self.textBrowser.setVerticalScrollBar(scroll_bar)
        self.contact = contact
        if file_type == 'html':
            self.export_type = Output.HTML
            self.export_choices = {"文本": True, "图片": True, "语音": False, "视频": False, "表情包": False,
                                   '音乐与音频': False, '分享卡片': False, '文件': False,
                                   '拍一拍等系统消息': True}  # 定义导出的数据类型，默认全部选择
        elif file_type == 'csv':
            self.export_type = Output.CSV
            self.export_choices = {"文本": True, "图片": True, "视频": True, "表情包": True}  # 定义导出的数据类型，默认全部选择
        elif file_type == 'txt':
            self.export_type = Output.TXT
            self.export_choices = {"文本": True, "图片": True, "语音": True, "视频": True, "表情包": True,
                                   '音乐与音频': True, '分享卡片': True, '文件': True,
                                   '拍一拍等系统消息': True}  # 定义导出的数据类型，默认全部选择
        elif file_type == 'docx':
            self.export_type = Output.DOCX
            self.export_choices = {"文本": True, "图片": False, "语音": False, "视频": False,
                                   "表情包": False, '拍一拍等系统消息': True}  # 定义导出的数据类型，默认全部选择
        else:
            self.export_choices = {"文本": True, "图片": True, "视频": True, "表情包": True}  # 定义导出的数据类型，默认全部选择
        self.setWindowTitle(title)
        self.resize(400, 300)
        self.worker = None  # 导出线程

        for export_type, default_state in self.export_choices.items():
            checkbox = QCheckBox(export_type)
            checkbox.setChecked(default_state)
            self.verticalLayout_2.addWidget(checkbox)

        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_start.clicked.connect(self.export_data)
        self.btn_cancel.clicked.connect(self.reject)  # 使用reject关闭对话框
        self.comboBox_time.activated.connect(self.set_export_date)
        self.timer = QTimer(self)
        self.time = 0
        self.total_msg_num = 99999  # 总的消息个数
        self.num = 0  # 当前完成的消息个数
        self.timer.timeout.connect(self.update_elapsed_time)
        self.time_range = None

    def export_data(self):
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        # 在这里获取用户选择的导出数据类型
        selected_types = {types[export_type]: checkbox.isChecked() for export_type, checkbox in
                          zip(self.export_choices.keys(), self.findChildren(QCheckBox))}

        # 在这里根据用户选择的数据类型执行导出操作
        print("选择的数据类型:", selected_types)
        self.worker = Output(self.contact, type_=self.export_type, message_types=selected_types,
                             time_range=self.time_range)
        self.worker.progressSignal.connect(self.update_progress)
        self.worker.okSignal.connect(self.export_finished)
        self.worker.rangeSignal.connect(self.set_total_msg_num)
        self.worker.start()
        # 启动定时器，每1000毫秒更新一次任务进度
        self.timer.start(1000)
        self.start_time = time.time()
        # self.accept()  # 使用accept关闭对话框
    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()
    def set_export_date(self):
        date_range = self.comboBox_time.currentText()
        if date_range == '全部时间':
            pass
        elif date_range == '最近三个月':


            # 获取今天的日期和时间
            today = datetime.now()

            # 获取今天的日期
            today_date = today.date()

            # 获取今天的24:00:00的时间戳
            today_midnight = datetime.combine(today_date, datetime.min.time()) + timedelta(days=1)
            today_midnight_timestamp = int(today_midnight.timestamp())

            # 获取三个月前的日期
            three_months_ago = today - timedelta(days=90)

            # 获取三个月前的00:00:00的时间戳
            three_months_ago_date = three_months_ago.date()
            three_months_ago_midnight = datetime.combine(three_months_ago_date, datetime.min.time())
            three_months_ago_midnight_timestamp = int(three_months_ago_midnight.timestamp())
            self.time_range = (three_months_ago_midnight_timestamp, today_midnight_timestamp)

        elif date_range == '自定义时间':
            date_range = None
            chat_calendar = msg_db.get_messages_calendar(self.contact.wxid)
            if chat_calendar:
                start_time = datetime.strptime(chat_calendar[0], "%Y-%m-%d")
                end_time = datetime.strptime(chat_calendar[-1], "%Y-%m-%d")
                date_range = (start_time.date(),end_time.date())
            self.time_range_view = TimeRangeDialog(date_range=date_range,parent=self)
            self.time_range_view.date_range_signal.connect(self.set_time_range)
            self.time_range_view.show()
            self.comboBox_time.setCurrentIndex(0)
            # QMessageBox.warning(self,
            #                     "别急别急",
            #                     "马上就实现该功能"
            #                     )

    def set_time_range(self, time_range):
        self.time_range = time_range
        self.comboBox_time.setCurrentIndex(2)

    def set_total_msg_num(self, num):
        self.total_msg_num = num
        # b''+num +(1,1)

    def export_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        self.time = 0
        end_time = time.time()
        print(f'总耗时:{end_time - self.start_time}s')
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Information)
        reply.setWindowTitle('OK')
        reply.setText(f"导出聊天记录成功\n在{output_dir}目录下(跟exe文件在一起)\n{os.path.normpath(os.path.join(os.getcwd(),output_dir))}")
        reply.addButton("确认", QMessageBox.AcceptRole)
        reply.addButton("取消", QMessageBox.RejectRole)
        api = reply.exec_()
        # 在任务完成时重置sys.stdout
        sys.stdout = sys.__stdout__
        self.accept()

    def select_all(self):
        self.select_all_flag = not self.select_all_flag
        print('全选', self.select_all_flag)
        if self.select_all_flag:
            for checkbox in self.findChildren(QCheckBox):
                checkbox.setChecked(True)
            self.btn_select_all.setText('全不选')
        else:
            for checkbox in self.findChildren(QCheckBox):
                checkbox.setChecked(False)
            self.btn_select_all.setText('全选')

    def update_elapsed_time(self):
        self.time += 1
        self.label_time.setText(f"耗时: {self.time}s")

    def update_progress(self, progress_percentage):
        self.num += 1
        progress_percentage = int((self.num) / self.total_msg_num * 100)
        self.progressBar.setValue(progress_percentage)
        self.label_process.setText(f"导出进度: {progress_percentage}%")

    def close(self):
        sys.stdout = sys.__stdout__
        del self.worker
        super().close()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = ExportDialog()
    result = dialog.exec_()  # 使用exec_()获取用户的操作结果
    if result == QDialog.Accepted:
        print("用户点击了导出按钮")
    else:
        print("用户点击了取消按钮")
    sys.exit(app.exec_())
