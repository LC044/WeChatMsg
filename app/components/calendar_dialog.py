import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QCheckBox, QMessageBox, QCalendarWidget, QWidget, QVBoxLayout


class CalendarDialog(QDialog):
    selected_date_signal = pyqtSignal(int)

    def __init__(self, date_range=None, parent=None):
        """

        @param date_range: tuple[Union[QDate, datetime.date],Union[QDate, datetime.date]] #限定的可选择范围
        @param parent:
        """
        super().__init__(parent)
        self.setWindowTitle('选择日期')
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.onDateChanged)
        if date_range:
            self.calendar.setDateRange(*date_range)
        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)
        self.setLayout(layout)

    def onDateChanged(self):
        # 获取选择的日期
        selected_date = self.calendar.selectedDate()
        s_t = time.strptime(selected_date.toString("yyyy-MM-dd"), "%Y-%m-%d")  # 返回元祖
        mkt = int(time.mktime(s_t))
        timestamp = mkt
        self.selected_date_signal.emit(timestamp)
        print("Selected Date:", selected_date.toString("yyyy-MM-dd"), timestamp)
        self.close()


if __name__ == '__main__':
    import sys
    from datetime import datetime

    app = QApplication(sys.argv)
    # 设置日期范围
    start_date = datetime(2023, 12, 11)
    end_date = datetime(2024, 1, 9)
    date_range = (start_date.date(), end_date.date())
    ex = CalendarDialog(date_range=date_range)
    ex.show()
    sys.exit(app.exec_())
