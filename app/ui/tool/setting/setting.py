import json
import os.path
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox

from .settingUi import Ui_Form


class SettingControl(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super(SettingControl, self).__init__(parent)
        self.setupUi(self)
        self.btn_addstopword.clicked.connect(self.add_stopwords)
        self.read_data()

    def read_data(self):
        os.makedirs('./app/data', exist_ok=True)
        stopwords = ['裂开','苦涩','叹气','凋谢','让我看看','酷','奋斗','疑问','擦汗','抠鼻','鄙视','勾引','奸笑','嘿哈','捂脸','机智','加油','吃瓜','尴尬','炸弹','旺柴']
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
