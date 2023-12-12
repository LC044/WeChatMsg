from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDialog, QVBoxLayout, QCheckBox, QHBoxLayout, \
    QProgressBar, QLabel, QMessageBox

from app.DataBase.output_pc import Output

types = {
    '文本': 1,
    '图片': 3,
    '语音': 34,
    '视频': 43,
    '表情包': 47,
    '拍一拍等系统消息': 10000
}
Stylesheet = """
QPushButton{
    background-color: #ffffff;
}
QPushButton:hover { 
    background-color: lightgray;
}
"""

class ExportDialog(QDialog):
    def __init__(self, contact=None, title="选择导出的类型", file_type="csv", parent=None):
        super(ExportDialog, self).__init__(parent)
        self.setStyleSheet(Stylesheet)
        self.contact = contact
        if file_type == 'html':
            self.export_type = Output.HTML
            self.export_choices = {"文本": True, "图片": True, "语音": True, "视频": True, "表情包": True,
                                   '拍一拍等系统消息': True}  # 定义导出的数据类型，默认全部选择
        elif file_type == 'csv':
            self.export_type = Output.CSV
            self.export_choices = {"文本": True, "图片": True, "视频": True, "表情包": True}  # 定义导出的数据类型，默认全部选择
        elif file_type == 'txt':
            self.export_type = Output.TXT
            self.export_choices = {"文本": True, "图片": True, "视频": True, "表情包": True}  # 定义导出的数据类型，默认全部选择
        else:
            self.export_choices = {"文本": True, "图片": True, "视频": True, "表情包": True}  # 定义导出的数据类型，默认全部选择
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        self.resize(400, 300)
        self.worker = None  # 导出线程
        self.progress_bar = QProgressBar(self)
        self.progress_label = QLabel(self)
        for export_type, default_state in self.export_choices.items():
            checkbox = QCheckBox(export_type)
            checkbox.setChecked(default_state)
            layout.addWidget(checkbox)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        hlayout = QHBoxLayout(self)
        self.export_button = QPushButton("导出")
        self.export_button.clicked.connect(self.export_data)
        hlayout.addWidget(self.export_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)  # 使用reject关闭对话框
        hlayout.addWidget(self.cancel_button)
        layout.addLayout(hlayout)
        self.setLayout(layout)

    def export_data(self):
        self.export_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        # 在这里获取用户选择的导出数据类型
        selected_types = {types[export_type]: checkbox.isChecked() for export_type, checkbox in
                          zip(self.export_choices.keys(), self.findChildren(QCheckBox))}

        # 在这里根据用户选择的数据类型执行导出操作
        print("选择的数据类型:", selected_types)
        self.worker = Output(self.contact, type_=self.export_type, message_types=selected_types)
        self.worker.progressSignal.connect(self.update_progress)
        self.worker.okSignal.connect(self.export_finished)
        self.worker.start()
        # self.accept()  # 使用accept关闭对话框

    def export_finished(self):
        self.export_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Information)
        reply.setWindowTitle('OK')
        reply.setText(f"导出聊天记录成功\n在./data/目录下(跟exe文件在一起)")
        reply.addButton("确认", QMessageBox.AcceptRole)
        reply.addButton("取消", QMessageBox.RejectRole)
        api = reply.exec_()
        self.accept()

    def update_progress(self, progress_percentage):
        self.progress_bar.setValue(progress_percentage)
        self.progress_label.setText(f"导出进度: {progress_percentage}%")


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
