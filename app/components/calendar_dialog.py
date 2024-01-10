import time

from datetime import datetime, timedelta
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QCheckBox, QMessageBox, QCalendarWidget, QWidget, QVBoxLayout, \
    QToolButton

from app.ui.Icon import Icon


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
        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        prev_btn.setIcon(Icon.Arrow_left_Icon)
        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        next_btn.setIcon(Icon.Arrow_right_Icon)
        self.date_range = date_range
        if date_range:
            self.calendar.setDateRange(*date_range)
            # 从第一天开始，依次添加日期到列表，直到该月的最后一天
            current_date = date_range[1]
            while (current_date + timedelta(days=1)).month == date_range[1].month:
                current_date += timedelta(days=1)
                range_format = self.calendar.dateTextFormat(current_date)
                range_format.setForeground(Qt.gray)
                self.calendar.setDateTextFormat(current_date, range_format)
            # 从第一天开始，依次添加日期到列表，直到该月的最后一天
            current_date = date_range[0]
            while (current_date - timedelta(days=1)).month == date_range[0].month:
                current_date -= timedelta(days=1)
                range_format = self.calendar.dateTextFormat(current_date)
                range_format.setForeground(Qt.gray)
                self.calendar.setDateTextFormat(current_date, range_format)
        layout = QVBoxLayout(self)
        layout.addWidget(self.calendar)
        self.setLayout(layout)

    def set_start_date(self):
        if self.date_range:
            self.calendar.setCurrentPage(self.date_range[0].year, self.date_range[0].month)
    def set_end_date(self):
        if self.date_range:
            self.calendar.setCurrentPage(self.date_range[1].year, self.date_range[1].month)
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
    from datetime import datetime, timedelta

    app = QApplication(sys.argv)
    # 设置日期范围
    start_date = datetime(2024, 1, 5)
    end_date = datetime(2024, 1, 9)
    date_range = (start_date.date(), end_date.date())
    ex = CalendarDialog(date_range=date_range)
    ex.show()
    sys.exit(app.exec_())
