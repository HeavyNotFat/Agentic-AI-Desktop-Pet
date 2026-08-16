import glob
import os
import typing
from webbrowser import open as open_webpage
from socket import gethostbyname, gethostname

from .customize import function, constants, widgets

from PyQt5.Qt import QRect, Qt
from PyQt5.QtWidgets import QFrame
from qfluentwidgets import ComboBox, LineEdit, PrimaryPushButton, Slider, BodyLabel, PushButton


class General(QFrame):
    def __init__(self, intelligence_module, runtime_module, languages, configure, module_info, param_dict, **kwargs):
        super().__init__()
        self.intelligence_module = intelligence_module
        self.runtime_module = runtime_module
        self.languages = languages
        self.configure = configure
        self.module_info = module_info
        self.param_dict = param_dict
        self.kwargs = kwargs
        self.setObjectName("General")
        # 语言选择 Language selector
        BodyLabel(self.languages[131], self).setGeometry(QRect(5, 47, 80, 35))
        self.select_language = ComboBox(self)
        self.select_language.addItems(os.listdir("./resources/languages"))
        self.select_language.setCurrentText(self.configure['settings']['language'])
        self.select_language.setGeometry(QRect(100, 47, 230, 35))
        self.select_language.currentTextChanged.connect(self.change_language)
        # 宠物形象 Character Pet
        BodyLabel(self.languages[2], self).setGeometry(QRect(5, 87, 80, 35))
        self.select_character = ComboBox(self)
        self.select_character.addItems(os.listdir("./resources/model"))
        self.select_character.setCurrentText(self.configure['default'])
        self.select_character.setGeometry(QRect(100, 87, 230, 35))
        self.select_character.currentTextChanged.connect(self.change_character)
        # 宠物昵称 Pet Nickname
        self.input_pet_nickname = LineEdit(self)
        self.input_pet_nickname.setText(self.configure['name'])
        self.input_pet_nickname.setGeometry(QRect(340, 87, 230, 35))
        self.input_pet_nickname.setClearButtonEnabled(True)
        self.input_pet_nickname.textChanged.connect(
            lambda value: function.change_configure(
                value, "name", self.configure))
        # 成人选择 Adult Chose
        BodyLabel(self.languages[5], self).setGeometry(QRect(5, 127, 80, 35))
        self.select_adult_label = ComboBox(self)
        self.select_adult_label.addItems(
            list(self.configure['model'][self.configure['default']]['adult']['AdultDescribe'].values()))
        self.select_adult_label.setCurrentIndex(self.configure['adult_level'] - 1)
        if not self.configure['adult_level']:
            self.select_adult_label.setEnabled(False)
        self.select_adult_label.setGeometry(QRect(100, 127, 230, 35))
        self.select_adult_label.currentIndexChanged.connect(
            lambda value: function.change_configure(
                value + 1, "adult_level", self.configure))
        # AI发声 AI Speak
        BodyLabel(self.languages[6], self).setGeometry(QRect(5, 167, 80, 35))
        self.select_ai_speak = ComboBox(self)
        self.select_ai_speak.addItems(list(self.module_info.keys()))
        self.select_ai_speak.setCurrentText(self.configure['voice_model'])
        self.select_ai_speak.currentTextChanged.connect(self.change_reference)
        self.select_ai_speak.setGeometry(QRect(100, 167, 230, 35))
        self.input_reference_text = LineEdit(self)
        self.input_reference_text.setPlaceholderText("Reference Text here")
        self.input_reference_text.setClearButtonEnabled(True)
        self.input_reference_text.setGeometry(QRect(5, 207, 470, 35))
        self.click_play_reference = PrimaryPushButton(self.languages[7], self)
        self.click_play_reference.clicked.connect(
            lambda: self.kwargs.get("play")(self.input_reference_text.text()))
        self.click_play_reference.setGeometry(QRect(490, 207, 80, 35))
        # 水印 Watermark
        BodyLabel(self.languages[8], self).setGeometry(QRect(5, 247, 80, 35))
        self.select_watermark = ComboBox(self)
        self.select_watermark.addItems(list(self.param_dict.keys()))
        self.select_watermark.setCurrentText(self.configure['watermark'].split(";")[0])
        self.select_watermark.setGeometry(QRect(100, 247, 230, 35))
        self.select_watermark.currentTextChanged.connect(
            lambda value: self.change_watermark(value, "name"))
        self.scale_watermark = Slider(Qt.Horizontal, self)
        self.scale_watermark.setRange(0, 100)
        self.scale_watermark.setGeometry(QRect(340, 257, 230, 35))
        self.scale_watermark.valueChanged.connect(
            lambda value: self.change_watermark(value, "value"))
        # 透明度 Opacity
        BodyLabel(self.languages[9], self).setGeometry(QRect(5, 297, 80, 35))
        self.scale_opacity = Slider(Qt.Horizontal, self)
        self.scale_opacity.setRange(5, constants.OPACITY_PRECISION)
        self.scale_opacity.setGeometry(QRect(100, 302, 230, 35))
        self.scale_opacity.setValue(int(self.configure['settings']['transparency'] * constants.OPACITY_PRECISION))
        self.scale_opacity.valueChanged.connect(
            lambda value: function.change_configure(
                value / constants.OPACITY_PRECISION, "settings.transparency", self.configure))
        # 大小
        BodyLabel(self.languages[190], self).setGeometry(QRect(5, 337, 80, 35))
        self.scale_size = Slider(Qt.Horizontal, self)
        self.scale_size.setRange(20, 100)
        self.scale_size.setGeometry(QRect(100, 342, 230, 35))
        self.scale_size.setValue(int(self.configure['settings']['size'] * 100))
        self.scale_size.valueChanged.connect(
            lambda value: function.change_configure(
                value / 100, "settings.size", self.configure))
        # 旋转角度
        BodyLabel("旋转角度", self).setGeometry(QRect(5, 377, 80, 35))
        self.scale_angle = Slider(Qt.Horizontal, self)
        self.scale_angle.setRange(0, 360)
        self.scale_angle.setGeometry(QRect(100, 382, 360, 35))
        self.scale_angle.setValue(int(self.configure['settings']['angle']))
        self.scale_angle.valueChanged.connect(
            lambda value: function.change_configure(value, "settings.angle", self.configure))

        webui_url = PushButton(f"{self.languages[154]} http://{gethostbyname(gethostname())}:52013", self)
        webui_url.clicked.connect(lambda: open_webpage(f"http://{gethostbyname(gethostname())}:52013"))
        webui_url.setGeometry(QRect(0, 462, 400, 35))
        # 角色相关 Character Related
        self.click_add_character = PrimaryPushButton(self.languages[84], self)
        self.click_add_character.setGeometry(QRect(450, 462, 80, 35))
        self.click_add_character.clicked.connect(self.add_character)
        self.click_delete_character = PrimaryPushButton(self.languages[3], self)
        self.click_delete_character.setGeometry(QRect(550, 462, 80, 35))
        self.click_delete_character.clicked.connect(self.delete_character)

        self.fill_information()

    def add_another_one(self, model):
        self.select_character.addItem(model)

    def add_character(self):
        def check_if_live2d(path: str):
            exist_v3_over = glob.glob(f"{path}/*.model3.json")
            if exist_v3_over:
                return glob.glob(f"{path}/*.model3.json"), 3
            else:
                return glob.glob(f"{path}/*.model.json"), 2

        character_model_path = function.select_folder(self, self.languages[84])
        if character_model_path:
            live2d, arch = check_if_live2d(character_model_path)
            if not live2d:
                widgets.pop_error(self, self.languages[140], self.languages[141])
                return
            self.runtime_module.file.add_character(character_model_path)
            with open(f"./resources/model/{os.path.basename(character_model_path)}/{arch}", "w", encoding="utf-8") as f:
                f.write(f"This is a architecture explanation file\nYour architecture is {arch}")
                f.close()
            if self.kwargs.get("live2d").LIVE2D_VERSION == arch:
                self.select_character.addItem(character_model_path.split("/")[-1])
            else:
                widgets.pop_warning(self, self.languages[161], self.languages[162])

    def delete_character(self):
        if self.select_character.currentText() in ("Chocola", "kasumi2"):
            widgets.pop_error(self, self.languages[78], self.languages[66])
            return
        selected = self.select_character.currentText()
        self.change_character("Chocola")
        self.select_character.setCurrentText("Chocola")
        self.select_character.removeItem(os.listdir("./resources/model").index(selected))
        self.runtime_module.file.delete_character(self.configure, selected)

    def change_language(self, value):
        function.change_configure(value, "settings.language", self.configure)
        self.kwargs.get("reload")(value, "language")

    def change_character(self, value):
        function.change_configure(value, "default", self.configure)
        self.kwargs.get("reload")(value, "character")

    def change_reference(self):
        refer_text = self.module_info[self.select_ai_speak.currentText()][3]
        self.input_reference_text.clear()
        self.input_reference_text.setText(refer_text)
        function.change_configure(self.select_ai_speak.currentText(), "voice_model", self.configure)
        self.intelligence_module.voice.change_module(
            self.configure['voice_model'], self.module_info,
            self.runtime_module.parse_local_url(self.configure['settings']['local']['gsv']))
    
    def change_watermark(self, value, type_: typing.Literal['name', 'value']):
        if type_ == "name":
            self.scale_watermark.setRange(int(self.param_dict[value]['min'] * 10),
                                          int(self.param_dict[value]['max'] * 10))
            self.scale_watermark.setValue(int(float(self.configure['watermark'].split(";")[1]) * 10))
            function.change_configure(f"{value};{self.scale_watermark.value()}", "watermark", self.configure)
        else:
            function.change_configure(f"{self.select_watermark.currentText()};{value / 10}",
                                      "watermark", self.configure)

    def fill_information(self):
        if self.select_watermark.currentText() not in self.param_dict.keys():
            return
        self.scale_watermark.setRange(int(self.param_dict[self.select_watermark.currentText()]['min'] * 10),
                                      int(self.param_dict[self.select_watermark.currentText()]['max'] * 10))
        self.scale_watermark.setValue(int(float(self.configure['watermark'].split(";")[1]) * 10))
