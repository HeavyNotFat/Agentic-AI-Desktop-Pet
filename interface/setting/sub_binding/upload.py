import shutil
import os

from .. import customize

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QRect, QFileDialog, QThread, pyqtSignal
from qfluentwidgets import FluentIcon, BodyLabel, LineEdit, PrimaryPushButton, TextEdit, ComboBox


class Upload(QThread):
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent, type_, token, runtime_module):
        super().__init__(parent)
        self.parent = parent
        self.type = type_
        self.token = token
        self.runtime = runtime_module

    def process(self):
        sign = self.parent.input_sign.text().strip()
        if (sign.lower() == "adpofficial") or ("adp" in sign.lower() and "official" in sign.lower()):
            self.error.emit("请勿使用官方签名进行上传！")
            return None
        self.progress.emit("正在处理数据请稍后……")
        name = self.parent.input_upload_name.text().strip()
        folder_path = f"./logs/community/com_{name}"
        try:
            os.makedirs(folder_path, exist_ok=True)
            shutil.make_archive(f"{folder_path}/{name}", 'zip', self.parent.input_self_path.text().strip())
            self.progress.emit("压缩包制作完成！")
        except Exception as e:
            self.error.emit(f"发生错误：{type(e).__name__}: {e}")
            return None

        try:
            shutil.copyfile(self.parent.input_avatar_path.text().strip(), f"{folder_path}/{name}.png")
            self.progress.emit("图标完成！")
        except Exception as e:
            self.error.emit(f"发生错误：{type(e).__name__}: {e}")
            return None

        try:
            with open(f"{folder_path}/{name}.txt", "w", encoding="utf-8") as f:
                f.write(f"{self.parent.input_description.text().strip()}   -{sign}")
                f.close()
            self.progress.emit("描述完成！")
        except Exception as e:
            self.error.emit(f"发生错误：{type(e).__name__}: {e}")
            return None

        self.progress.emit("数据处理完成，正在上传……")
        return folder_path

    def run(self):
        if not self.parent.select_file_made.currentText().strip():
            for line_edit in filter(lambda v: "input_" in v, dir(self.parent)):
                if line_edit == "input_plugin_loader": continue
                if not getattr(self.parent, line_edit).text().strip():
                    self.error.emit("请填写所有必填项！")
                    self.finished.emit()
                    return
            folder_path = self.process()
            if folder_path is None: return
        else:
            folder_path = f"./logs/community/com_{self.parent.select_file_made.currentText()}"
        status, msg = self.runtime.upload_file(list(map(lambda v: f"{folder_path}/{v}", os.listdir(folder_path))), self.type, self.token)
        if not status: self.error.emit(msg)
        else: self.finished.emit()


class UploadExtensions(QWidget):
    def __init__(self, parent, languages, configure, runtime_module):
        super().__init__(parent)
        self.setObjectName("UploadExtensions")
        self.parent = parent
        self.languages = languages
        self.configure = configure
        self.runtime = runtime_module
        BodyLabel("名字：", self).setGeometry(QRect(5, 10, 90, 30))
        self.input_upload_name = LineEdit(self)
        self.input_upload_name.setPlaceholderText("不建议输入中文！")
        self.input_upload_name.setGeometry(QRect(60, 10, 500, 30))

        BodyLabel("图标：", self).setGeometry(QRect(5, 50, 90, 30))
        self.input_avatar_path = LineEdit(self)
        self.input_avatar_path.setGeometry(QRect(60, 50, 400, 30))
        click_select_path1 = PrimaryPushButton(FluentIcon.FOLDER, "选择", self)
        click_select_path1.clicked.connect(lambda: self.input_avatar_path.setText(QFileDialog.getOpenFileName(self, "选择头像", "", "*.png")[0]))
        click_select_path1.setGeometry(QRect(470, 50, 100, 30))

        BodyLabel("描述：", self).setGeometry(QRect(5, 90, 90, 30))
        self.input_description = LineEdit(self)
        self.input_description.setGeometry(QRect(60, 90, 220, 30))
        BodyLabel("签名：", self).setGeometry(QRect(290, 90, 90, 30))
        self.input_sign = LineEdit(self)
        self.input_sign.setGeometry(QRect(340, 90, 230, 30))

        BodyLabel("本体：", self).setGeometry(QRect(10, 130, 90, 30))
        self.input_self_path = LineEdit(self)
        self.input_self_path.setGeometry(QRect(60, 130, 400, 30))
        click_select_path2 = PrimaryPushButton(FluentIcon.FOLDER, "选择", self)
        click_select_path2.clicked.connect(lambda: self.input_self_path.setText(QFileDialog.getExistingDirectory(self, "选择插件", "")))
        click_select_path2.setGeometry(QRect(470, 130, 100, 30))

        # 插件加载器
        self.input_plugin_loader = TextEdit(self)
        self.input_plugin_loader.setGeometry(QRect(5, 170, 570, 200))

        self.input_upload_into_plugin = PrimaryPushButton("上传至插件", self)
        self.input_upload_into_plugin.setObjectName("plugin")
        self.input_upload_into_plugin.clicked.connect(self.upload)
        self.input_upload_into_plugin.setGeometry(QRect(5, 380, 100, 30))
        self.input_upload_into_model = PrimaryPushButton("上传至模型", self)
        self.input_upload_into_model.setObjectName("model")
        self.input_upload_into_model.clicked.connect(self.upload)
        self.input_upload_into_model.setGeometry(QRect(110, 380, 100, 30))

        BodyLabel("已制作文件上传：", self).setGeometry(QRect(230, 380, 120, 30))
        self.select_file_made = ComboBox(self)
        t = list(map(lambda v: v[4:], os.listdir("./logs/community")))
        t.insert(0, "")
        self.select_file_made.addItems(t)
        self.select_file_made.setCurrentText("")
        self.select_file_made.setGeometry(QRect(350, 380, 220, 30))


    def upload(self):
        type_ = str(self.sender().objectName())
        thread = Upload(self, type_, self.parent.login_parameter.token, self.runtime)
        thread.error.connect(self.error)
        thread.progress.connect(lambda msg: customize.widgets.pop_notification("社区功能", msg, "info"))
        thread.finished.connect(self.finished)
        thread.start()
        self.input_upload_into_model.setDisabled(True)
        self.input_upload_into_plugin.setDisabled(True)

    def finished(self, should_show_success: bool = True):
        if should_show_success: customize.widgets.pop_notification("社区功能", "上传成功！", "success")
        self.input_upload_into_model.setDisabled(False)
        self.input_upload_into_plugin.setDisabled(False)

    def error(self, msg):
        customize.widgets.pop_notification("社区功能", msg, "error")
        self.finished(False)