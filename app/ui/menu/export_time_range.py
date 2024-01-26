from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QDialog, QCheckBox, QMessageBox, QCalendarWidget, QWidget, QVBoxLayout, QLabel

from app.components.calendar_dialog import CalendarDialog
try:
    from .time_range import Ui_Dialog
except:
    from time_range import Ui_Dialog
Stylesheet = '''
QToolButton{
    color:#000000;
}
QCalendarWidget QAbstractItemView:disabled {

}
QCalendarWidget QAbstractItemView:enabled{
}
'''


class TimeRangeDialog(QDialog, Ui_Dialog):
    date_range_signal = pyqtSignal(tuple)

    def __init__(self, date_range=None, parent=None):
        """

        @param date_range: tuple[Union[QDate, datetime.date],Union[QDate, datetime.date]] 限定的可选择范围
        @param parent:
        """
        super().__init__(parent)
        self.calendar = None
        self.setupUi(self)
        self.setWindowTitle('选择日期范围')
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet(Stylesheet)
        self.toolButton_start_time.clicked.connect(self.select_date_start)
        self.toolButton_end_time.clicked.connect(self.select_date_end)
        self.calendar = CalendarDialog(date_range=date_range, parent=self)
        self.calendar.selected_date_signal.connect(self.set_date)
        self.btn_ok.clicked.connect(self.ok)
        self.btn_ok.setEnabled(False)
        self.btn_ok_num = 0
        self.btn_cancel.clicked.connect(lambda x: self.close())
        self.start_time_flag = True
        self.start_timestamp = 0
        self.end_timestamp = 0

    def set_date(self, timestamp):
        if self.start_time_flag:
            self.start_timestamp = timestamp
            date_object = datetime.fromtimestamp(timestamp)
            str_start = date_object.strftime("%Y-%m-%d")
            self.toolButton_start_time.setText(str_start)
            self.btn_ok_num += 1
        else:
            date_object = datetime.fromtimestamp(timestamp)
            str_start = date_object.strftime("%Y-%m-%d")
            self.end_timestamp = timestamp + 86399
            self.toolButton_end_time.setText(str_start)
            self.btn_ok_num += 1
        if self.btn_ok_num == 2:
            self.btn_ok.setEnabled(True)

    def ok(self):
        date_range = (self.start_timestamp, self.end_timestamp)
        self.date_range_signal.emit(date_range)
        self.close()

    def select_date_start(self):
        self.start_time_flag = True
        self.calendar.set_start_date()
        self.calendar.show()

    def select_date_end(self):
        self.start_time_flag = False
        self.calendar.set_end_date()
        self.calendar.show()

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        if self._tracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._startPos = QPoint(e.x(), e.y())
            self._tracking = True

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._tracking = False
            self._startPos = None
            self._endPos = None

if __name__ == '__main__':
    import sys
    from datetime import datetime

    app = QApplication(sys.argv)
    # 设置日期范围
    start_date = datetime(2023, 12, 11)
    end_date = datetime(2024, 1, 9)
    date_range = (start_date.date(), end_date.date())
    ex = TimeRangeDialog(date_range=date_range)
    ex.show()
    sys.exit(app.exec_())
