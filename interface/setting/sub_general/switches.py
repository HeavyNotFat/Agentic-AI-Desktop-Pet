import subprocess
import os
import typing

from ..customize import function, constants

from PyQt5.Qt import Qt, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from qfluentwidgets import SettingCardGroup, SwitchSettingCard, OptionsSettingCard, \
    OptionsConfigItem, QConfig, qconfig, OptionsValidator, ExpandLayout, ComboBoxSettingCard, \
    FluentIcon, ScrollArea, InfoBar, InfoBarPosition, ExpandGroupSettingCard, BodyLabel, SwitchButton, \
    IndicatorPosition, \
    ComboBox, LineEdit

env = os.environ.copy()
python_path = subprocess.check_output(["where", "python"], env=env).decode().replace(
    "\r", "").split("\n")

class Config(QConfig):
    penetration = OptionsConfigItem(
        "Advanced", "penetration", "shut",
        OptionsValidator(["shut", "next", "left-bottom", "left-top", "right-bottom", "right-top"]), restart=True)
    safety_examine = OptionsConfigItem(
        "Advanced", "safety", "shut",
        OptionsValidator(["shut", "l1", "l2", "l3", "l4", "l5"]), restart=True)
    local_python_path = OptionsConfigItem(
        "Advanced", "python", python_path[0], OptionsValidator(python_path), restart=True)


class TranslateCard(ExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(FluentIcon.LANGUAGE, parent.languages[16], parent.languages[93], parent)
        self.parent = parent
        self.enable_label = BodyLabel(parent.languages[233], self)
        self.enable_switch_button = SwitchButton("关", self, IndicatorPosition.RIGHT)
        self.enable_switch_button.setChecked(parent.configure['settings']['enable']['trans'])
        self.enable_switch_button.setOnText("开")
        self.enable_switch_button.setFixedWidth(135)
        self.enable_switch_button.checkedChanged.connect(
            lambda value: function.change_configure(
                value, "settings.enable.trans", parent.configure
            ))
        self.add(self.enable_label, self.enable_switch_button)

        self.target_label = BodyLabel(parent.languages[234], self)
        self.target_combo_box = ComboBox(self)
        self.target_combo_box.addItems([
            parent.languages[235],
            parent.languages[236],
            parent.languages[237],
            parent.languages[238],
        ])
        if parent.configure['settings']['trans_lang'] == "zh-Hans":
            self.target_combo_box.setCurrentText(parent.languages[235])
        elif parent.configure['settings']['trans_lang'] == "en":
            self.target_combo_box.setCurrentText(parent.languages[236])
        elif parent.configure['settings']['trans_lang'] == "ja":
            self.target_combo_box.setCurrentText(parent.languages[237])
        elif parent.configure['settings']['trans_lang'] == "ko":
            self.target_combo_box.setCurrentText(parent.languages[238])
        self.target_combo_box.currentTextChanged.connect(self.change_language)
        self.target_combo_box.setFixedWidth(200)
        self.add(self.target_label, self.target_combo_box)

        self.engine_label = BodyLabel(parent.languages[239], self)
        self.select_translation_engine = ComboBox(self)
        self.select_translation_engine.addItems([parent.languages[80], parent.languages[82]])
        self.tool_label = BodyLabel(parent.languages[4], self)
        self.select_translation_tool = ComboBox(self)
        if (translate := parent.configure['settings']['translate'].split('.'))[0] == "ai":
            self.select_translation_engine.setCurrentText(parent.languages[80])
            self.select_translation_tool.addItems([parent.languages[81]])
        elif translate[0] == "spider":
            self.select_translation_engine.setCurrentText(parent.languages[82])
            self.select_translation_tool.addItems([parent.languages[83]])
        self.select_translation_engine.currentTextChanged.connect(
            lambda value: self.change_translation(value, "object"))
        self.select_translation_tool.currentTextChanged.connect(
            lambda value: self.change_translation(value, "method"))
        self.add(self.engine_label, self.select_translation_engine)
        self.add(self.tool_label, self.select_translation_tool)

    def change_translation(self, value, type_: typing.Literal['object', 'method']):
        if type_ == "object":
            self.select_translation_tool.clear()
            if value == self.parent.languages[80]:
                self.select_translation_tool.addItems([self.parent.languages[81]])
            elif value == self.parent.languages[82]:
                self.select_translation_tool.addItems([self.parent.languages[83]])
            function.change_configure(f"{value.replace(' ', '').split('-')[1]}."
                                      f"{self.select_translation_tool.currentText().replace(' ', '').split('-')[1]}",
                                      "settings.translate", self.parent.configure)
        else:
            function.change_configure(f"{self.select_translation_engine.currentText().replace(' ', '').split('-')[1]}."
                                      f"{value.replace(' ', '').split('-')[1]}",
                                      "settings.translate", self.parent.configure)

    def change_language(self, text):
        if text == self.parent.languages[235]:
            function.change_configure(
                "zh-Hans", "settings.trans_lang", self.parent.configure
            )
        elif text == self.parent.languages[236]:
            function.change_configure(
                "en", "settings.trans_lang", self.parent.configure
            )
        elif text == self.parent.languages[237]:
            function.change_configure(
                "ja", "settings.trans_lang", self.parent.configure
            )
        elif text == self.parent.languages[238]:
            function.change_configure(
                "ko", "settings.trans_lang", self.parent.configure
            )

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        self.addGroupWidget(w)


class SourceCard(ExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(FluentIcon.APPLICATION, "源地址", "云端功能源地址（URL）", parent)
        self.entry = LineEdit(self)
        self.entry.setFixedWidth(200)
        self.entry.setText(parent.configure['api_source'])
        self.entry.textChanged.connect(
            lambda value: function.change_configure(value, "api_source", parent.configure)
        )
        self.add(BodyLabel("地址", self), self.entry)

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        self.addGroupWidget(w)


class Switches(ScrollArea):
    def __init__(self, languages, cache_config, configure):
        super().__init__()
        self.setObjectName("SwitchesG")
        self.cache_config = cache_config
        self.languages = languages
        self.configure = configure

        self.scroll_widgets = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widgets)
        qconfig.load("./interface/setting/sub_general/switch.json", Config)
        # 常规设置
        self.general_group = SettingCardGroup(self.languages[11], self.scroll_widgets)
        self.card_compatible_capture = SwitchSettingCard(
            icon=FluentIcon.FIT_PAGE,
            title=self.languages[12],
            content=self.languages[85],
            parent=self.general_group,
        )
        self.card_compatible_capture.setChecked(configure['settings']['compatibility'])
        self.card_compatible_capture.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.compatibility",
            ))
        self.general_group.addSettingCard(self.card_compatible_capture)
        self.card_adult = SwitchSettingCard(
            icon=FluentIcon.HEART,
            title=self.languages[5],
            content=self.languages[87],
            parent=self.general_group
        )
        self.card_adult.setChecked(bool(configure['adult_level']))
        self.card_adult.checkedChanged.connect(
            lambda value: self.pop_success(
                self.languages[88], self.languages[89],
                function.change_configure, 1 if value else 0, "adult_level", self.configure))
        self.general_group.addSettingCard(self.card_adult)
        self.card_recognition = SwitchSettingCard(
            icon=FluentIcon.MICROPHONE,
            title=self.languages[13],
            content=self.languages[90],
            parent=self.general_group
        )
        self.card_recognition.setChecked(configure['settings']['enable']['rec'])
        self.card_recognition.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.rec",
            ))
        self.general_group.addSettingCard(self.card_recognition)
        self.card_speaker = SwitchSettingCard(
            icon=FluentIcon.SPEAKERS,
            title=self.languages[14],
            content=self.languages[91],
            parent=self.general_group
        )
        self.card_speaker.setChecked(configure['settings']['enable']['tts'])
        self.card_speaker.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.tts",
            ))
        self.general_group.addSettingCard(self.card_speaker)
        self.card_search = SwitchSettingCard(
            icon=FluentIcon.SEARCH,
            title=self.languages[15],
            content=self.languages[92],
            parent=self.general_group
        )
        self.card_search.setChecked(configure['settings']['enable']['online'])
        self.card_search.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.online",
            ))
        self.general_group.addSettingCard(self.card_search)
        self.card_translate = TranslateCard(
            self
        )
        # self.card_translate = SwitchSettingCard(
        #     configItem=Config.translate,
        #     static=FluentIcon.LANGUAGE,
        #     title=self.languages[16],
        #     content=self.languages[93],
        #     parent=self.general_group
        # )
        # self.card_translate.checkedChanged.connect(
        #     lambda value: self.change_configure(
        #         value, "settings.enable.trans",
        #         value, "General.translate"
        #     ))
        self.general_group.addSettingCard(self.card_translate)

        # 高级设置
        self.advanced_group = SettingCardGroup(self.languages[17], self.scroll_widgets)
        self.media_understanding = SwitchSettingCard(
            icon=FluentIcon.PHOTO,
            title=self.languages[18],
            content=self.languages[86],
            parent=self.advanced_group
        )
        self.media_understanding.setChecked(configure['settings']['enable']['media'])
        self.media_understanding.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.media",
            ))
        self.advanced_group.addSettingCard(self.media_understanding)
        self.card_mouse_penetration = OptionsSettingCard(
            configItem=Config.penetration,
            icon=FluentIcon.TRANSPARENT,
            title=self.languages[19],
            content=self.languages[59],
            texts=[self.languages[20], self.languages[21], self.languages[22],
                   self.languages[23], self.languages[24], self.languages[25]],
            parent=self.advanced_group
        )
        self.card_mouse_penetration.optionChanged.connect(
            lambda value: function.change_configure(
                value.value, "Advanced.penetration", cache_config, constants.CACHE_CONFIGURE_PATH))
        self.advanced_group.addSettingCard(self.card_mouse_penetration)
        self.card_realtime_api = SwitchSettingCard(
            icon=QIcon("./resources/static/realtime.png"),
            title=self.languages[198],
            content=self.languages[199],
            parent=self.advanced_group
        )
        self.card_realtime_api.setChecked(configure['settings']['enable']['realtimeAPI'])
        self.card_realtime_api.setIconSize(18, 18)
        self.card_realtime_api.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.realtimeAPI",
            ))
        self.advanced_group.addSettingCard(self.card_realtime_api)

        self.card_taskbar_lock = SwitchSettingCard(
            icon=FluentIcon.PIN,
            title=self.languages[26],
            content=self.languages[60],
            parent=self.advanced_group
        )
        self.card_taskbar_lock.setChecked(configure['settings']['enable']['locktsk'])
        self.card_taskbar_lock.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.locktsk",
            ))
        self.advanced_group.addSettingCard(self.card_taskbar_lock)

        self.card_safety_examine = OptionsSettingCard(
            configItem=Config.safety_examine,
            icon=FluentIcon.VPN,
            title=self.languages[126],
            content=self.languages[125],
            texts=[self.languages[20], self.languages[120], self.languages[121],
                   self.languages[122], self.languages[123], self.languages[124]],
            parent=self.advanced_group
        )
        self.card_safety_examine.setValue(configure['settings']['safety'])
        self.card_safety_examine.optionChanged.connect(
            lambda value: self.change_configure(
                value.value, "settings.safety"
            ))
        self.card_audio_visualization = SwitchSettingCard(
            icon=FluentIcon.MUSIC,
            title=self.languages[138],
            content=self.languages[139],
            parent=self.advanced_group
        )
        self.card_audio_visualization.setChecked(configure['settings']['enable']['visualization'])
        self.card_audio_visualization.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.enable.visualization"
            ))
        self.advanced_group.addSettingCard(self.card_audio_visualization)
        self.advanced_group.addSettingCard(self.card_safety_examine)
        self.local_python_path_card = ComboBoxSettingCard(
            configItem=Config.local_python_path,
            icon=FluentIcon.CODE,
            title=self.languages[214],
            content=self.languages[215],
            parent=self.advanced_group,
            texts=python_path
        )
        Config.local_python_path.valueChanged.connect(
            lambda value: self.change_configure(
                value, "settings.python",
                value, "Advanced.python"
            ))
        self.advanced_group.addSettingCard(self.local_python_path_card)
        self.source_card = SourceCard(self)
        self.advanced_group.addSettingCard(self.source_card)

        # Live2D 设置
        self.live2d_group = SettingCardGroup(f"Live2D {self.languages[10]}", self.scroll_widgets)
        self.card_auto_blink = SwitchSettingCard(
            icon=FluentIcon.VIEW,
            title=self.languages[53],
            content=self.languages[53],
            parent=self.live2d_group
        )
        self.card_auto_blink.setChecked(configure['settings']['live2d']['enable']['AutoBlink'])
        self.card_auto_blink.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.live2d.enable.AutoBlink",
            ))
        self.live2d_group.addSettingCard(self.card_auto_blink)
        self.card_auto_breath = SwitchSettingCard(
            icon=FluentIcon.SYNC,
            title=self.languages[54],
            content=self.languages[54],
            parent=self.live2d_group
        )
        self.card_auto_breath.setChecked(configure['settings']['live2d']['enable']['AutoBreath'])
        self.card_auto_breath.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.live2d.enable.AutoBreath",
            ))
        self.live2d_group.addSettingCard(self.card_auto_breath)
        self.card_auto_drag = SwitchSettingCard(
            icon=FluentIcon.MOVE,
            title=self.languages[55],
            content=self.languages[55],
            parent=self.live2d_group
        )
        self.card_auto_drag.setChecked(configure['settings']['live2d']['enable']['AutoDrag'])
        self.card_auto_drag.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.live2d.enable.AutoDrag",
            ))
        self.live2d_group.addSettingCard(self.card_auto_drag)

        # 物理模拟
        self.physics_group = SettingCardGroup(self.languages[183], self.scroll_widgets)
        self.total_switch = SwitchSettingCard(
            icon=QIcon("./resources/static/physics.png"),
            title=self.languages[184],
            content=self.languages[185],
            parent=self.physics_group
        )
        self.total_switch.setChecked(configure['settings']['physics']['total'])
        self.total_switch.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.physics.total",
            ))
        self.total_switch.setIconSize(20, 20)
        self.physics_group.addSettingCard(self.total_switch)
        self.bounce_switch = SwitchSettingCard(
            icon=QIcon("./resources/static/bounce.png"),
            title=self.languages[186],
            content=self.languages[187],
            parent=self.physics_group
        )
        self.bounce_switch.setChecked(configure['settings']['physics']['bounce'])
        self.bounce_switch.setIconSize(20, 20)
        self.bounce_switch.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.physics.bounce",
            ))
        self.physics_group.addSettingCard(self.bounce_switch)
        self.dumping_motion_switch = SwitchSettingCard(
            icon=QIcon("./resources/static/dumping.png"),
            title=self.languages[188],
            content=self.languages[189],
            parent=self.physics_group
        )
        self.dumping_motion_switch.setChecked(configure['settings']['physics']['dumping'])
        self.dumping_motion_switch.setIconSize(20, 20)
        self.dumping_motion_switch.checkedChanged.connect(
            lambda value: self.change_configure(
                value, "settings.physics.dumping",
            ))
        self.physics_group.addSettingCard(self.dumping_motion_switch)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(36, 52, 36, 0)
        self.expand_layout.addWidget(self.general_group)
        self.expand_layout.addWidget(self.advanced_group)
        self.expand_layout.addWidget(self.live2d_group)
        self.expand_layout.addWidget(self.physics_group)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.scroll_widgets)
        self.scroll_widgets.setObjectName('ScrollWidget')

    def change_configure(self, value, relative, cav=None, car=None):
        if cav and car:
            function.change_configure(cav, car, self.cache_config, constants.CACHE_CONFIGURE_PATH)
        function.change_configure(value, relative, self.configure)

    def pop_success(self, title, content, func, *args):
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1200,
            parent=self
        )
        func(*args)


Config = Config()
