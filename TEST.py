# -*- coding: utf-8 -*-
"""
Created on Sat May  9 17:14:37 2020

@author: Giyn
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextBrowser, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon


class Simple_Window(QWidget):
    def __init__(self):
        super(Simple_Window, self).__init__()  # 使用super函数可以实现子类使用父类的方法
        self.setWindowTitle("记事本")
        self.setWindowIcon(QIcon('NoteBook.png'))  # 设置窗口图标
        self.resize(412, 412)
        self.text_browser = QTextBrowser(self)  # 实例化一个QTextBrowser对象
        # self.text_browser.setText("<h1>Hello World!</h1>")  # 设置编辑框初始化时显示的文本
        # self.text_browser.setReadOnly(False) # 调用setReadOnly方法并传入False参数即可编辑文本浏览框（编辑框也可以变成只读）

        self.save_button = QPushButton("Save", self)
        self.clear_button = QPushButton("Clear", self)
        self.add_button = QPushButton("Add", self)

        self.save_button.clicked.connect(lambda: self.button_slot(self.save_button))
        self.clear_button.clicked.connect(lambda: self.button_slot(self.clear_button))
        self.add_button.clicked.connect(self.add_text)

        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        self.h_layout.addWidget(self.save_button)
        self.h_layout.addWidget(self.clear_button)
        self.h_layout.addWidget(self.add_button)
        self.v_layout.addWidget(self.text_browser)
        self.v_layout.addLayout(self.h_layout)

        self.setLayout(self.v_layout)

    def button_slot(self, button):
        if button == self.save_button:
            choice = QMessageBox.question(self, "Question", "Do you want to save it?", QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                with open('Second text.txt', 'w') as f:
                    f.write(self.text_browser.toPlainText())
                self.close()
            elif choice == QMessageBox.No:
                self.close()
        elif button == self.clear_button:
            self.text_browser.clear()

    def add_text(self):
        # self.text_browser.append("<h1>Hello World!</h1>")  # 调用append方法可以向文本浏览框中添加文本
        html = """
            <div class="user-group" style="padding: 6px;
     display: flex;
     display: -webkit-flex;
	 justify-content: flex-end;
     -webkit-justify-content: flex-end; 
	 ">
          <div class="user-msg" style="text-align: right;
		  width: 75%;
     position: relative;">
                <span class="user-reply" style="display: inline-block;
				padding: 8px;
				border-radius: 4px;
				margin:0 15px 12px;
				text-align: left;
				background-color: #9EEA6A;
				box-shadow: 0px 0px 2px #bbb;
				">我要抢楼</span>
                <i style="width: 0;
				height: 0;
				position: absolute;
				top: 10px;
			display: inline-block;
				border-top: 10px solid transparent;
				border-bottom: 10px solid transparent;
				right: 4px;
         border-left: 12px solid #9EEA6A;"></i>
          </div>
           <img class="user-img" src="./app/data/avatar/2a/42/user_2a427a26f96058921da245444ab542f5.png" width="45px" height="45px";/>
     </div>
        """
        self.text_browser.insertHtml(html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Simple_Window()
    window.show()
    sys.exit(app.exec())
