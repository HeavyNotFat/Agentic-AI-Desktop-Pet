from .customize import function

from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QWidget

from qfluentwidgets import ExpandLayout, FluentIcon, ScrollArea, \
    qconfig, QConfig, OptionsConfigItem, OptionsSettingCard, OptionsValidator, SettingCardGroup


class Config(QConfig):
    text_output = OptionsConfigItem(
        "Inference", "text_output", "cloud",
        OptionsValidator(["cloud", "local"]), restart=True)
    voice = OptionsConfigItem(
        "Inference", "voice", "cloud",
        OptionsValidator(["cloud", "local"]), restart=True)
    media = OptionsConfigItem(
        "Inference", "media", "cloud",
        OptionsValidator(["cloud", "local"]), restart=True)
    recognition = OptionsConfigItem(
        "Inference", "recognition", "cloud",
        OptionsValidator(["cloud", "local"]), restart=True)


class Intelligence(ScrollArea):
    def __init__(self, languages, configure, reload):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.setObjectName("Intelligence")

        self.scroll_widgets = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widgets)
        qconfig.load("./interface/setting/sub_general/intelligence.json", Config)

        self.inference_group = SettingCardGroup(self.languages[28], self.scroll_widgets)
        # 文本输出 Text Output
        self.card_text_output = OptionsSettingCard(
            Config.text_output,
            FluentIcon.EDIT,
            self.languages[56],
            "",
            [self.languages[33], self.languages[34]],
            self.inference_group)
        self.card_text_output.optionChanged.connect(lambda value: reload(value.value, "settings.text.way"))
        self.inference_group.addSettingCard(self.card_text_output)
        # 语音输出 Voice Output
        self.card_voice_output = OptionsSettingCard(
            Config.voice,
            FluentIcon.SPEAKERS,
            self.languages[14],
            "",
            [self.languages[33], self.languages[34]],
            self.inference_group)
        self.card_voice_output.optionChanged.connect(
            lambda value: function.change_configure(
                value.value, "settings.tts.way", self.configure
            )
        )
        self.inference_group.addSettingCard(self.card_voice_output)
        # 媒体理解 Media Understanding
        self.card_media_understanding = OptionsSettingCard(
            Config.media,
            FluentIcon.PHOTO,
            self.languages[18],
            "",
            [self.languages[33], self.languages[34]],
            self.inference_group)
        self.card_media_understanding.optionChanged.connect(
            lambda value: function.change_configure(
                value.value, "settings.understand.way", self.configure
            )
        )
        self.inference_group.addSettingCard(self.card_media_understanding)
        # 语音识别 Voice Recognition
        self.card_recognition = OptionsSettingCard(
            Config.recognition,
            FluentIcon.MICROPHONE,
            self.languages[13],
            "",
            [self.languages[33], self.languages[34]],
            self.inference_group)
        self.card_recognition.optionChanged.connect(
            lambda value: function.change_configure(
                value.value, "settings.rec.way", self.configure
            )
        )
        self.inference_group.addSettingCard(self.card_recognition)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(36, 52, 36, 0)
        self.expand_layout.addWidget(self.inference_group)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.scroll_widgets)
        self.scroll_widgets.setObjectName('ScrollWidget')
        self.setObjectName("Intelligence")


Config = Config()
