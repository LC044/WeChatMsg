# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingUi.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(638, 696)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -20, 595, 728))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.widget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.widget.setStyleSheet("QWidget{\n"
"   background-color:rgb(251,251,251);\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    background-color: rgb(250,252,253);\n"
"    border-radius: 5px;\n"
"    padding: 8px;\n"
"    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */\n"
"    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */\n"
"    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */\n"
"    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */\n"
"}\n"
"QPushButton:hover { \n"
"    background-color: lightgray;\n"
"}")
        self.widget.setObjectName("widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.widget)
        self.plainTextEdit.setFrameShape(QtWidgets.QFrame.Box)
        self.plainTextEdit.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.horizontalLayout.addWidget(self.plainTextEdit)
        self.btn_addstopword = QtWidgets.QPushButton(self.widget)
        self.btn_addstopword.setObjectName("btn_addstopword")
        self.horizontalLayout.addWidget(self.btn_addstopword)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_3.addWidget(self.widget)
        self.widget_3 = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.widget_3.setStyleSheet("QWidget{\n"
"   background-color:rgb(251,251,251);\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    background-color: rgb(250,252,253);\n"
"    border-radius: 5px;\n"
"    padding: 8px;\n"
"    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */\n"
"    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */\n"
"    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */\n"
"    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */\n"
"}\n"
"QPushButton:hover { \n"
"    background-color: lightgray;\n"
"}")
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.widget_3)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.plainTextEdit_newword = QtWidgets.QPlainTextEdit(self.widget_3)
        self.plainTextEdit_newword.setFrameShape(QtWidgets.QFrame.Box)
        self.plainTextEdit_newword.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.plainTextEdit_newword.setPlainText("")
        self.plainTextEdit_newword.setObjectName("plainTextEdit_newword")
        self.horizontalLayout_3.addWidget(self.plainTextEdit_newword)
        self.btn_addnewword_2 = QtWidgets.QPushButton(self.widget_3)
        self.btn_addnewword_2.setObjectName("btn_addnewword_2")
        self.horizontalLayout_3.addWidget(self.btn_addnewword_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout_5.addLayout(self.verticalLayout_2)
        self.verticalLayout_3.addWidget(self.widget_3)
        self.widget_2 = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.widget_2.setStyleSheet("QWidget{\n"
"   background-color:rgb(251,251,251);\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    background-color: rgb(250,252,253);\n"
"    border-radius: 5px;\n"
"    padding: 8px;\n"
"    border-right: 2px solid #888888;  /* 按钮边框，2px宽，白色 */\n"
"    border-bottom: 2px solid #888888;  /* 按钮边框，2px宽，白色 */\n"
"    border-left: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */\n"
"    border-top: 1px solid #ffffff;  /* 按钮边框，2px宽，白色 */\n"
"}\n"
"QPushButton:hover { \n"
"    background-color: lightgray;\n"
"}")
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setContentsMargins(9, -1, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.commandLinkButton_send_error_log = QtWidgets.QCommandLinkButton(self.widget_2)
        self.commandLinkButton_send_error_log.setEnabled(True)
        self.commandLinkButton_send_error_log.setTabletTracking(False)
        self.commandLinkButton_send_error_log.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.commandLinkButton_send_error_log.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.commandLinkButton_send_error_log.setToolTipDuration(-1)
        self.commandLinkButton_send_error_log.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.commandLinkButton_send_error_log.setAutoFillBackground(False)
        self.commandLinkButton_send_error_log.setCheckable(False)
        self.commandLinkButton_send_error_log.setChecked(False)
        self.commandLinkButton_send_error_log.setAutoRepeat(False)
        self.commandLinkButton_send_error_log.setAutoExclusive(False)
        self.commandLinkButton_send_error_log.setAutoDefault(False)
        self.commandLinkButton_send_error_log.setDefault(False)
        self.commandLinkButton_send_error_log.setObjectName("commandLinkButton_send_error_log")
        self.horizontalLayout_2.addWidget(self.commandLinkButton_send_error_log)
        self.btn_send_error_log = QtWidgets.QPushButton(self.widget_2)
        self.btn_send_error_log.setObjectName("btn_send_error_log")
        self.horizontalLayout_2.addWidget(self.btn_send_error_log)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label_error_log = QtWidgets.QLabel(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_error_log.sizePolicy().hasHeightForWidth())
        self.label_error_log.setSizePolicy(sizePolicy)
        self.label_error_log.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_error_log.setObjectName("label_error_log")
        self.horizontalLayout_2.addWidget(self.label_error_log)
        self.checkBox_send_error_log = QtWidgets.QCheckBox(self.widget_2)
        self.checkBox_send_error_log.setText("")
        self.checkBox_send_error_log.setIconSize(QtCore.QSize(64, 64))
        self.checkBox_send_error_log.setChecked(True)
        self.checkBox_send_error_log.setObjectName("checkBox_send_error_log")
        self.horizontalLayout_2.addWidget(self.checkBox_send_error_log)
        self.verticalLayout_3.addWidget(self.widget_2)
        self.checkBox_2 = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.checkBox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_3.addWidget(self.checkBox)
        self.commandLinkButton_2 = QtWidgets.QCommandLinkButton(self.scrollAreaWidgetContents)
        self.commandLinkButton_2.setCheckable(True)
        self.commandLinkButton_2.setObjectName("commandLinkButton_2")
        self.verticalLayout_3.addWidget(self.commandLinkButton_2)
        self.radioButton = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout_3.addWidget(self.radioButton)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_6.addWidget(self.scrollArea)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "文本框里输入年度报告词云停用词，每个词之间用空格隔开"))
        self.plainTextEdit.setPlainText(_translate("Form", "哈哈哈 发呆"))
        self.btn_addstopword.setText(_translate("Form", "添加停用词"))
        self.label_2.setText(_translate("Form", "文本框里输入年度报告词云自定义词，每个词之间用空格隔开"))
        self.btn_addnewword_2.setText(_translate("Form", "添加自定义词"))
        self.commandLinkButton_send_error_log.setText(_translate("Form", "收集错误日志"))
        self.commandLinkButton_send_error_log.setDescription(_translate("Form", "收集错误信息以帮助改进"))
        self.btn_send_error_log.setText(_translate("Form", "手动发送"))
        self.label_error_log.setText(_translate("Form", "开"))
        self.checkBox_2.setText(_translate("Form", "CheckBox"))
        self.checkBox.setText(_translate("Form", "CheckBox"))
        self.commandLinkButton_2.setText(_translate("Form", "CommandLinkButton"))
        self.radioButton.setText(_translate("Form", "RadioButton"))
