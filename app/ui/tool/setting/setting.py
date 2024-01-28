import json
import os.path
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox

from .settingUi import Ui_Form

Stylesheet = """
QPushButton{
    background-color: rgb(250,252,253);
    border-radius: 5px;
    padding: 8px;
    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */
    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */
}
QPushButton:hover { 
    background-color: lightgray;
}
/*去掉item虚线边框*/
QListWidget, QListView, QTreeWidget, QTreeView {
    outline: 0px;
    border:none;
}
/*设置左侧选项的最小最大宽度,文字颜色和背景颜色*/
QListWidget {
    min-width: 400px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
    color: black;
    border:none;
}
QListWidget::item{
    min-width: 80px;
    max-width: 400px;
    min-height: 80px;
    max-height: 80px;
}
/*被选中时的背景颜色和左边框颜色*/
QListWidget::item:selected {
    border-left:none;
    color: black;
    font-weight: bold;
}
QCheckBox::indicator {
    background: rgb(251, 251, 251);
    Width:60px;
    Height:60px;
    border-radius: 10px;
}
QCheckBox::indicator:unchecked{
    Width:60px;
    Height:60px;
    image: url(:/icons/icons/按钮_关闭.svg);
}
QCheckBox::indicator:checked{
    Width:60px;
    Height:60px;
    image: url(:/icons/icons/按钮_开启.svg);
}

"""


class SettingControl(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super(SettingControl, self).__init__(parent)
        self.setStyleSheet(Stylesheet)
        self.setupUi(self)

        self.btn_addstopword.clicked.connect(self.add_stopwords)
        self.init_ui()
        self.read_data()

    def init_ui(self):
        self.checkBox.setText('是')
        self.checkBox_send_error_log.clicked.connect(self.set_error_log)

    def set_error_log(self):
        if self.checkBox_send_error_log.isChecked():
            self.label_error_log.setText('开')
        else:
            self.label_error_log.setText('关')

    def read_data(self):
        os.makedirs('./app/data', exist_ok=True)
        stopwords = ['裂开', '苦涩', '叹气', '凋谢', '让我看看', '酷', '奋斗', '疑问', '擦汗', '抠鼻', '鄙视', '勾引',
                     '奸笑', '嘿哈', '捂脸', '机智', '加油', '吃瓜', '尴尬', '炸弹', '旺柴']
        if os.path.exists('./app/data/stopwords.txt'):
            with open('./app/data/stopwords.txt', 'r', encoding='utf-8') as f:
                stopwords = set(f.read().splitlines())
                self.plainTextEdit.setPlainText(' '.join(stopwords))
        else:
            self.plainTextEdit.setPlainText(' '.join(stopwords))
            stopwords = '\n'.join(stopwords)
            with open('./app/data/stopwords.txt', 'w', encoding='utf-8') as f:
                f.write(stopwords)

    def add_stopwords(self):
        text = self.plainTextEdit.toPlainText()
        stopwords = '\n'.join(text.split())
        with open('./app/data/stopwords.txt', 'w', encoding='utf-8') as f:
            f.write(stopwords)
        QMessageBox.about(self, "添加成功", "停用词添加成功")
