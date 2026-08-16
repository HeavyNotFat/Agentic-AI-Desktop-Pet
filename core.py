import glob
import time
import traceback
import typing
import shutil
import re
import random
import json
import subprocess
import threading
import math
from difflib import get_close_matches
from socket import gethostbyname, gethostname
import tempfile

# 运行时
import runtime
# 接口
import interface
# 着色器
import shader
# 日志
import logs
# 人工智能
import intelligence
# 引擎
import engine
from engine import webui
# 架构
import architecture

# WindowsAPI 和 系统
import os
import sys
import ctypes
import win32gui
import win32con
# 界面和OpenGL
from OpenGL import GL

from PyQt5.Qt import QIcon, QApplication, QTimer, Qt, QRect, QTimerEvent, QCursor, QGuiApplication, \
    QDropEvent, QColor, QLinearGradient, QPainter, QBrush, QPixmap, QFileDialog, QLocale
from PyQt5.QtCore import QCoreApplication, QPoint
from PyQt5.QtWidgets import QWidget, QLabel, QStackedWidget, QHBoxLayout, QMessageBox, QOpenGLWidget, \
    QSystemTrayIcon, QVBoxLayout
from qfluentwidgets import FluentIcon, NavigationItemPosition, FluentTranslator, \
    TextEdit, LineEdit, PrimaryToolButton, qrouter, NavigationInterface, RoundMenu, Action, \
    AvatarWidget, BodyLabel, CaptionLabel, SystemTrayMenu, ScrollArea, PushButton
from qframelesswindow import FramelessWindow, TitleBar

# 初始化变量常亮和配置
# 检测Python环境变量
try:
    subprocess.check_output(['python', '--version'], stderr=subprocess.STDOUT, text=True)
    IS_PYTHON_EXITS = True
except subprocess.CalledProcessError as e:
    IS_PYTHON_EXITS = False
PLUGIN_GLOBAL = {"print": typing.Any, "input": typing.Any, "interface": typing.Any}
GWL_EX_STYLE: int = -20
WS_EX_TRANSPARENT: int = 0x00000020
live2d_parameter: dict = {}
switches_configure: dict = runtime.file.load_switch()
configure, configure_default = runtime.file.load_configure(interface.subscribe)
rules = runtime.file.load_rules(configure_default)
api_config = runtime.file.load_api()
languages: list[str] = runtime.file.load_language(configure)
module_info: dict = intelligence.load_gpt_sovits(runtime.parse_local_url(configure['settings']['local']['gsv']))
intelligence.text.reload_memories(configure_default)
intelligence.text.reload_tools()
intelligence.reload_api(configure["settings"]['cloud']['xunfei']['id'], configure["settings"]['cloud']['xunfei']['key'],
                        configure["settings"]['cloud']['xunfei']['secret'], configure["settings"]['cloud']['aliyun'])
runtime.thread.reload_module(interface, intelligence, runtime, logs)
webui.reload_module(intelligence)
webui.reload_data(configure['settings']['intelligence'],
                          api_config, configure['language_mapping'][configure['settings']['language']],
                          runtime.parse_local_url(configure['settings']['local']['text'])
                          if configure['settings']['text']['way'] == "local" else None)
runtime.api_source = configure['api_source']
# 判断架构支持并重载
if os.path.exists(f"./resources/model/{configure_default}/2"):
    architecture.reload(2)
else:
    architecture.reload(3)


class PictureShow(QWidget):
    """展示绘画图片"""
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("PictureShow - Ai Desktop Pet")
        self.setWindowIcon(QIcon('logo.ico'))

        self.image_show = QLabel(self)

    def _save_as(self):
        select_save_folder = QFileDialog.getExistingDirectory(self)
        if select_save_folder:
            shutil.copy(self.image_path, select_save_folder)
            return True
        return False

    def _save_as_and_remove_origin(self):
        if self._save_as():
            os.remove(self.image_path)
            self.close()

    def open(self, file_path):
        self.image_path = file_path

        pixmap = QPixmap(self.image_path)
        try:
            pixmap = pixmap.scaled(pixmap.width() // 3, pixmap.height() // 3,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_show.setPixmap(pixmap)
        except Exception:
            self.image_show.setText(f"{traceback.format_exc()}\n"
                                    f"Failed to show\nGo {self.image_path}\nOr go ./logs/picture to see")

        self.resize(pixmap.width(), pixmap.height())
        self.image_show.setScaledContents(True)

    def contextMenuEvent(self, event):
        menu = RoundMenu("MENU", self)

        image_path = os.path.join(os.getcwd(), self.image_path)

        save_as_action = Action(FluentIcon.SAVE_AS, languages[142], self)
        save_as_action.triggered.connect(self._save_as)
        menu.addAction(save_as_action)

        save_as_and_remove_action = Action(FluentIcon.MOVE, languages[143], self)
        save_as_and_remove_action.triggered.connect(self._save_as_and_remove_origin)
        menu.addAction(save_as_and_remove_action)

        open_file_action = Action(FluentIcon.LINK, languages[144], self)
        open_file_action.triggered.connect(lambda: os.startfile(image_path))
        menu.addAction(open_file_action)

        open_folder_action = Action(FluentIcon.FOLDER, languages[145], self)
        open_folder_action.triggered.connect(lambda: os.startfile(os.path.dirname(image_path)))
        menu.addAction(open_folder_action)

        menu.exec_(event.globalPos())


class AudioVisualization(QWidget):
    """音频可视化"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.5)

        self.setWindowTitle("AudioVisualization - Ai Desktop Pet")
        self.setWindowIcon(QIcon('logo.ico'))
        self.setFixedSize(400, 200)
        self.rectangles = []

    def draw_rectangle(self, rms):
        if len(self.rectangles) >= 400 // 15:
            self.rectangles.pop(0)
        self.rectangles.append(int(rms))
        self.update()

    @staticmethod
    def get_rainbow_gradient(height):
        colors = [
            QColor(148, 0, 211),
            QColor(75, 0, 130),
            QColor(0, 0, 255),
            QColor(0, 255, 0),
            QColor(255, 255, 0),
            QColor(255, 127, 0),
            QColor(255, 0, 0)
        ]
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0.0, colors[0])
        gradient.setColorAt(0.15, colors[0])
        gradient.setColorAt(0.15, colors[1])
        gradient.setColorAt(0.3, colors[1])
        gradient.setColorAt(0.3, colors[2])
        gradient.setColorAt(0.45, colors[2])
        gradient.setColorAt(0.45, colors[3])
        gradient.setColorAt(0.6, colors[3])
        gradient.setColorAt(0.6, colors[4])
        gradient.setColorAt(0.75, colors[4])
        gradient.setColorAt(0.75, colors[5])
        gradient.setColorAt(0.9, colors[5])
        gradient.setColorAt(0.9, colors[6])
        gradient.setColorAt(1.0, colors[6])
        return gradient

    def paintEvent(self, event):
        painter = QPainter(self)
        x_offset = 0
        for width in self.rectangles:
            gradient = self.get_rainbow_gradient(width)
            brush = QBrush(gradient)
            painter.setBrush(brush)
            painter.drawRect(x_offset, 20, 15, width)
            x_offset += 15


# 编译插件过程
class CompileProgress(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowTitle("CompileProgress - Agentic AI")
        self.setGeometry(100, 100, 600, 400)
        self.select_attr = ""
        self.select_folder = ""

        # 图标选择
        BodyLabel(languages[194], self).setGeometry(10, 10, 480, 30)
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(self.container)
        self.scroll_area.setGeometry(10, 40, 340, 350)

        row = 0
        col = 0
        max_per_row = 4

        for attr_name in dir(FluentIcon):
            if attr_name.startswith("__") or attr_name in ("name", "value", "ICONS"):
                continue

            icon = getattr(FluentIcon, attr_name)
            card = interface.setting.customize.widgets.SimpleCard(icon, attr_name, self.container)
            card.clicked.connect(lambda i=icon: self.fill_information(str(i).split(".")[-1], 0))

            if col == 0:
                self.hbox = QHBoxLayout()
                self.hbox.setSpacing(10)
                self.hbox.setAlignment(Qt.AlignLeft)
                self.main_layout.addLayout(self.hbox)

            self.hbox.addWidget(card)
            col += 1

            if col >= max_per_row:
                col = 0
                row += 1
        # 输入名称
        BodyLabel(languages[195], self).setGeometry(360, 10, 480, 30)
        self.input_name = LineEdit(self)
        self.input_name.setGeometry(360, 50, 200, 30)
        self.input_name.setPlaceholderText(languages[196])
        self.input_name.textChanged.connect(lambda: self.fill_information(self.input_name.text(), 1))

        # 信息展示
        self.input_icon_show = LineEdit(self)
        self.input_icon_show.setPlaceholderText("Select Icon or Input")
        self.input_icon_show.setGeometry(360, 130, 200, 30)
        self.input_icon_show.textChanged.connect(lambda: self.fill_information(self.input_icon_show.text(), 0))
        self.input_name_show = LineEdit(self)
        self.input_name_show.setPlaceholderText("Input show name")
        self.input_name_show.setGeometry(360, 165, 200, 30)

        self.desc_show = TextEdit(self)
        self.desc_show.setLineWrapMode(0)
        self.desc_show.setGeometry(360, 205, 200, 140)

        # 编译
        self.click_compile = PushButton(languages[38], self)
        self.click_compile.clicked.connect(self.save)
        self.click_compile.setGeometry(360, 350, 200, 30)

    def fill_information(self, value, index):
        if index == 0:
            self.input_icon_show.setText(value)
        else:
            self.input_name.setText(value)
            self.input_name_show.setText(value)
        self.desc_show.setText(json.dumps({os.path.basename(self.select_folder): {
            "static": self.input_icon_show.text(),
            "name": self.input_name_show.text(),
            "attr": self.select_attr}}, ensure_ascii=False, indent=3))

    def set_attr(self, check_id):
        self.select_attr = check_id

    def set_folder(self, folder_path):
        self.select_folder = folder_path

    def save(self):
        with open("./plugin/desc.json", "r", encoding='utf-8') as rpf:
            desc = json.load(rpf)
            rpf.close()
        desc.update(json.loads(str(self.desc_show.toPlainText())))
        tempdir = f"{tempfile.gettempdir()}/{os.path.basename(self.select_folder)}"
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
        shutil.copytree(self.select_folder, tempdir)
        shutil.copytree(tempdir, f"./plugin/{os.path.basename(self.select_folder)}")
        with open("./plugin/desc.json", "w", encoding='utf-8') as wpf:
            wpf.write(json.dumps(desc, ensure_ascii=False, indent=3))
            wpf.close()


# 设置界面
class CustomTitleBar(TitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.icon_label, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.window().windowIconChanged.connect(self.setIcon)

        self.title_label = QLabel(self)
        self.hBoxLayout.insertWidget(2, self.title_label, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.title_label.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.title_label.setText(title)
        self.title_label.adjustSize()

    def setIcon(self, icon):
        self.icon_label.setPixmap(QIcon(icon).pixmap(18, 18))


class Setting(FramelessWindow):
    def __init__(self, display_x: int | None = None, display_y: int | None = None, point_index: int = 0):
        def change(value, relative):
            interface.setting.customize.function.change_configure(
                value, relative, configure
            )
            webui.reload_data(configure['settings']['intelligence'],
                              api_config, configure['language_mapping'][configure['settings']['language']],
                              runtime.parse_local_url(configure['settings']['local']['text'])
                              if configure['settings']['text']['way'] == "local" else None)

        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowTitle(languages[0])
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        self.resize(700, 530)

        self.hBoxLayout = QHBoxLayout(self)
        self.navigation_interface = NavigationInterface(
            self, showMenuButton=True, showReturnButton=True)
        self.stack_widget = QStackedWidget(self)

        # 移动
        available_position = QApplication.desktop().availableGeometry()
        w, h = available_position.width(), available_position.height()
        if display_x is not None and display_y is not None:
            self.move(display_x, display_y)
        else:
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.general_page = interface.setting.general.General(
            intelligence, runtime,
            languages, configure, module_info, live2d_parameter,
            play=self.reference, reload=self.reload_character, live2d=architecture.live2d
        )
        self.switches_page = interface.setting.sub_general.switches.Switches(
            languages, switches_configure, configure)
        self.storage_page = interface.setting.sub_general.storage.StorageManager(
            languages, configure, runtime)

        self.intelligence_page = interface.setting.intelligence.Intelligence(languages, configure, change)
        self.local_intelligence_page = interface.setting.sub_intelligence.local.IntelligenceLocale(
            languages, configure, api_config, change, desktop, self)
        self.cloud_intelligence_page = interface.setting.sub_intelligence.cloud.IntelligenceCloud(
            languages, configure, self.reload_intelligence)

        self.binding_page = interface.setting.binding.Binding(languages, configure, runtime, self.addSubInterface)
        self.character_sets_page = interface.setting.sub_binding.character.Character(
            languages, configure, api_config, intelligence, runtime
        )
        self.animation_binding_page = interface.setting.sub_binding.animation.AnimationBinding(
            languages, configure, desktop.model_json_path, architecture.addon,
            record=self.record_animation, live2d=architecture.live2d, desktop=desktop
        )
        self.rule_binding_page = interface.setting.sub_binding.rule.RuleBinding(
            languages, configure, rules, desktop.model_json_path, architecture.addon, runtime)
        self.tools_binding_page = interface.setting.sub_develop.tools.ToolsBinding(
            languages, configure, runtime, interface)
        self.plugin_binding_page = interface.setting.sub_develop.plugin.PluginBinding(
            interface, self.run_code_for_plugin, languages, configure, compile_plugin=self.compile)

        self.cloud_support_page = interface.setting.cloud.CloudDownload(languages, configure, runtime,
            self.general_page.add_another_one,
            self.addSubInterface)

        self.about_page = interface.setting.about.About(languages, runtime)
        self.record_timer = QTimer(self)

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigation_interface)
        self.hBoxLayout.addWidget(self.stack_widget)
        self.hBoxLayout.setStretchFactor(self.stack_widget, 1)

        self.titleBar.raise_()
        self.navigation_interface.displayModeChanged.connect(self.titleBar.raise_)

        self.addSubInterface(self.general_page, FluentIcon.SETTING, languages[1])
        self.addSubInterface(self.switches_page, FluentIcon.DEVELOPER_TOOLS, languages[10],
                             parent=self.general_page)
        self.addSubInterface(self.storage_page, FluentIcon.PIE_SINGLE, languages[211],
                             parent=self.general_page)

        self.addSubInterface(self.intelligence_page, FluentIcon.EDUCATION, languages[27])
        self.addSubInterface(self.cloud_intelligence_page, FluentIcon.CLOUD, languages[29],
                             parent=self.intelligence_page)
        self.addSubInterface(self.local_intelligence_page, FluentIcon.DOWN, languages[31],
                             parent=self.intelligence_page)

        self.addSubInterface(self.binding_page, FluentIcon.TRANSPARENT, languages[133])
        self.addSubInterface(self.character_sets_page, QIcon("logo.ico"),
                             languages[164], parent=self.binding_page)
        self.addSubInterface(self.animation_binding_page, FluentIcon.LIBRARY_FILL, languages[39],
                             parent=self.binding_page)
        self.addSubInterface(self.rule_binding_page, FluentIcon.ALIGNMENT, languages[49], parent=self.binding_page)

        self.addSubInterface(DeveloperOptions, FluentIcon.DEVELOPER_TOOLS, languages[101],
                             position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.tools_binding_page, FluentIcon.EMOJI_TAB_SYMBOLS, languages[36],
                             parent=DeveloperOptions)
        self.addSubInterface(self.plugin_binding_page, FluentIcon.IOT, languages[132], 
                             parent=DeveloperOptions)

        self.addSubInterface(self.about_page, FluentIcon.INFO, languages[130], position=NavigationItemPosition.BOTTOM)

        qrouter.setDefaultRouteKey(self.stack_widget, self.general_page.objectName())

        self.stack_widget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stack_widget.setCurrentIndex(point_index)

        # 注册 接口
        interface.subscribe.views.Register.register("program_self", self)
        interface.subscribe.views.Register.register("general", self.general_page)
        interface.subscribe.views.Register.register("intelligence", self.intelligence_page)
        interface.subscribe.views.Register.register("binding", self.binding_page)
        interface.subscribe.views.Register.register("dev", DeveloperOptions)
        interface.subscribe.views.Register.register("about", self.about_page)

    # 自定义
    def addSubInterface(self, widget, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        self.stack_widget.addWidget(widget)
        self.navigation_interface.addItem(
            parentRouteKey=None if parent is None else parent.objectName(),
            routeKey=widget.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(widget),
            position=position,
            tooltip=text
        )

    def switchTo(self, widget):
        self.stack_widget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stack_widget.widget(index)
        self.navigation_interface.setCurrentItem(widget.objectName())
        qrouter.push(self.stack_widget, widget.objectName())

    @staticmethod
    def reload_intelligence():
        intelligence.reload_api(configure["settings"]['cloud']['xunfei']['id'],
                                configure["settings"]['cloud']['xunfei']['key'],
                                configure["settings"]['cloud']['xunfei']['secret'],
                                configure["settings"]['cloud']['aliyun'])
        webui.reload_data(configure['settings']['intelligence'],
                                  api_config, configure['language_mapping'][configure['settings']['language']],
                                  runtime.parse_local_url(configure['settings']['local']['text'])
                                  if configure['settings']['text']['way'] == "local" else None)

    def reload_character(self, value, type_: typing.Literal['language', 'character']):
        global desktop, languages, configure_default, rules
        desktop.internal_record.stop()
        desktop.close()
        if type_ == "character":
            origin = configure_default
            configure_default = value
            # 判断架构支持并重载
            if os.path.exists(f"./resources/model/{configure_default}/2"):
                if architecture.live2d.LIVE2D_VERSION != 2:
                    if interface.setting.customize.widgets.pop_message(self, languages[161], languages[163]):
                        architecture.reload(2)
                    else:
                        configure_default = origin
                        desktop.internal_record.start()
                        desktop.show()
                        return
                else:
                    architecture.reload(2)
            else:
                if architecture.live2d.LIVE2D_VERSION != 3:
                    if interface.setting.customize.widgets.pop_message(self, languages[161], languages[163]):
                        architecture.reload(3)
                    else:
                        configure_default = origin
                        desktop.internal_record.start()
                        desktop.show()
                        return
                else:
                    architecture.reload(3)
            if configure_default not in configure['model'].keys():
                runtime.file.load_template_model(configure, value)
        elif type_ == "language":
            languages = runtime.file.load_language(configure)
        # 重载
        rules = runtime.file.load_rules(configure_default)
        interface.subscribe.hooks.Operate.GetConversationInterface().move(desktop.x(), desktop.y())
        desktop = DesktopPet(desktop.x(), desktop.y())
        desktop.show()
        interface.subscribe.RegisterAttribute.SetWindow(desktop)

        interface.subscribe.actions.Register.UnsetALL()
        self.close()
        self.__init__(self.x(), self.y(), self.stack_widget.currentIndex())
        self.show()
        interface.subscribe.hooks.Register.HookConversationInterface(conversation)

    # Function
    def record_animation(self):
        def recorder():
            self.animation_binding_page.refresh_position(*configure['record']['position'])
            if not configure['record']['position'].count(-1):
                self.record_timer.stop()
                configure['record']['enable_position'] = False
                runtime.file.save_configure(configure)

        if self.record_timer.isActive():
            self.record_timer.stop()
        else:
            configure['record']['position'] = [-1, -1, -1, -1]
            self.record_timer.timeout.connect(recorder)
            self.record_timer.start(50)

    def exception(self, e_msg):
        if e_msg == "pythonnotfound":
            interface.setting.customize.widgets.pop_error(self, languages[78], languages[249].replace("\\n", "\n"), 12000, Qt.Vertical)
            return
        print(e_msg)
        interface.setting.customize.widgets.pop_error(self, "TraceBack", e_msg, 5000, Qt.Vertical)

    def examine_and_run(self, to_be_run_codes, type_: typing.Literal['independent', 'enhancement'],
                        python_file: str | None = None):
        try:
            if runtime.PythonCodeExaminer(to_be_run_codes).optimize_infinite_loop:
                interface.setting.customize.widgets.pop_warning(self, languages[117], languages[118], 5000)
            safety_level = configure['settings']['safety']
            if safety_level != "shut":
                attr = getattr(runtime.PythonCodeExaminer(to_be_run_codes), f"is_{safety_level}")
                if attr:
                    interface.setting.customize.widgets.pop_warning(self, languages[125], languages[119], 5000)
                    return

        except Exception:
            self.exception(traceback.format_exc())
            return
        if type_ == 'enhancement':
            try:
                exec(to_be_run_codes, PLUGIN_GLOBAL)
            except Exception:
                self.exception(traceback.format_exc())

        elif type_ == 'independent':
            try:
                if IS_PYTHON_EXITS:
                    if python_file is None:
                        with open("./logs/plugin_cache_runner.py", "w", encoding="utf-8") as pf:
                            pf.write(to_be_run_codes)
                            pf.close()
                        execute_file = f"{os.getcwd()}/logs/plugin_cache_runner.py"
                    else:
                        execute_file = f"{python_file}"
                    thread_run = runtime.thread.RunPythonPlugin(
                        self, execute_file, PLUGIN_GLOBAL, configure['settings']['python'], IS_PYTHON_EXITS)
                    thread_run.attribute.connect(subprocess_running.append)
                    thread_run.error.connect(self.exception)
                    thread_run.start()
            except Exception:
                self.exception(traceback.format_exc())

    def run_code_for_plugin(self, to_be_ran_codes, run_type=-4, ban_independent: bool = False,
                            python_file: str | None = None):
        # 自动选择
        if run_type == -4:
            try:
                parsed = runtime.PythonCodeParser(to_be_ran_codes).has_subscribe
            except Exception:
                self.exception(traceback.format_exc())
                return
            if parsed:
                self.examine_and_run(to_be_ran_codes, 'enhancement', python_file)

            else:
                if not ban_independent:
                    self.examine_and_run(to_be_ran_codes, 'independent', python_file)

        # 程序增强
        elif run_type == -2:
            self.examine_and_run(to_be_ran_codes, 'enhancement', python_file)

        # 独立程序
        elif run_type == -3:
            if not ban_independent:
                self.examine_and_run(to_be_ran_codes, 'independent', python_file)

    # 测试语音合成组
    def reference(self, text):
        voice_generator = runtime.thread.VoiceGenerateThread(
            desktop, configure, module_info, text.split(":")[-1], text.split(":")[0])
        voice_generator.result.connect(self.play)
        voice_generator.error.connect(self.error)
        voice_generator.start()

    @staticmethod
    def play(audio_bytes):
        runtime.thread.SpeakThread(desktop, audio_bytes).start()

    def error(self, value):
        if value is False:
            interface.setting.customize.widgets.pop_error(self, languages[64], languages[64])

    @staticmethod
    def compile(check_id, folder_path):
        compile_progress.set_attr(check_id)
        compile_progress.set_folder(folder_path)
        compile_progress.show()

    def resizeEvent(self, a0):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


class Conversation(QWidget):
    """对话界面"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowTitle("Enter Conversation - Ai Desktop Pet")
        self.setFixedSize(desktop.width(), 600)

        self.input_answer = TextEdit(self)
        self.input_answer.setGeometry(QRect(0, 0, 370, 60))
        self.input_answer.setReadOnly(True)

        self.icon = "DOWN"
        self.click_pop_answer = PrimaryToolButton(self)
        self.click_pop_answer.setIcon(FluentIcon.ARROW_DOWN)
        self.click_pop_answer.setGeometry(QRect(370, 0, 30, 60))
        self.click_pop_answer.clicked.connect(self.pop_answer)

        self.click_send = PrimaryToolButton(self)
        self.click_send.setIcon(FluentIcon.SEND)
        self.click_send.setGeometry(QRect(340, 431, 60, 30))
        self.click_send.clicked.connect(self.send_question)

        self.click_take_photo = PrimaryToolButton(self)
        self.click_take_photo.setIcon(FluentIcon.CAMERA)
        self.click_take_photo.setGeometry(QRect(280, 431, 60, 30))
        self.click_take_photo.clicked.connect(desktop.capture_screen)
        self.input_question = LineEdit(self)
        self.input_question.setGeometry(QRect(0, 430, 281, 30))
        self.input_question.setPlaceholderText(languages[70])

        # 为发送绑定按键
        self.input_question.returnPressed.connect(self.click_send.click)
        # 不可见
        self.click_pop_answer.setVisible(False)
        self.input_question.setVisible(False)
        self.click_send.setVisible(False)
        self.click_take_photo.setVisible(False)
        self.input_answer.setVisible(False)

    def duration_disappear(self, duration: int):
        QTimer.singleShot(duration, lambda: self.hide())

    def pop_answer(self):
        """回复框的拉伸动画"""
        def wrapper():
            nonlocal height
            # 根据icon的值增加或减少height
            if icon == "UP":
                height += 20
            elif icon == "DOWN":
                height -= 20
            # 如果height超出范围，则停止计时器
            if (icon == "UP" and height > 400) or (icon == "DOWN" and height < 80):
                timer.stop()
            # 更新UI组件的几何形状
            self.click_pop_answer.setGeometry(QRect(370, 0, 30, height))
            self.input_answer.setGeometry(QRect(0, 0, 370, height))

        # 初始化height的值
        height = int(self.input_answer.height())
        # 根据当前的icon值来设置新的icon值和图标
        if self.icon == "DOWN":
            self.icon = icon = "UP"
            self.click_pop_answer.setIcon(FluentIcon.UP)
        else:
            self.icon = icon = "DOWN"
            self.click_pop_answer.setIcon(FluentIcon.ARROW_DOWN)
        # 创建并启动计时器，每2毫秒调用一次wrapper函数
        timer = QTimer(self)
        timer.timeout.connect(wrapper)
        timer.start(2)

    def send_question(self):
        self.input_question.setGeometry(QRect(0, 430, 400, 30))
        self.click_send.setVisible(False)
        self.click_take_photo.setVisible(False)
        desktop.have_conversation(self.input_question.text())


class ProfileCard(QWidget):
    def __init__(self, icon: str, model_name: str, name: str, description, parent=None):
        super().__init__(parent=parent)
        self.avatar = AvatarWidget(icon, self)
        self.model_name_label = BodyLabel(model_name, self)
        self.name_label = CaptionLabel(name, self)
        self.information_label = BodyLabel(description, self)


        self.name_label.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))

        self.setFixedSize(307, 82)
        self.avatar.setRadius(24)
        self.avatar.move(2, 6)
        self.model_name_label.move(64, 13)
        self.name_label.move(64, 32)
        self.information_label.move(52, 48)


class SystemTray(QSystemTrayIcon):
    """系统托盘"""
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon("logo.ico"))

        menu = SystemTrayMenu()
        menu.addActions([
            Action(FluentIcon.LINK, languages[200], self, triggered=desktop.save_change),
            Action(FluentIcon.SAVE_COPY, languages[192], self, triggered=self.delete_all),
            Action(FluentIcon.CLOSE, languages[20], self, triggered=desktop.exit_program),
        ])
        self.setContextMenu(menu)

    @staticmethod
    def delete_all():
        for pet in clone_pet_model:
            pet.close()


class ClonePet(QOpenGLWidget):
    """角色克隆类"""
    def __init__(self, direct_json_path: str | None = None):
        super().__init__()
        self.direct_json_path = direct_json_path
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 400)
        self.move(desktop.x() - 50, desktop.y())

        self.click_in_area = self.is_transparent_raise = False
        self.drag_position = self.is_movement = None
        self.pet_model: architecture.live2d.LAppModel | None = None

    def delete_cloned(self):
        self.close()

    @staticmethod
    def delete_all_cloned():
        for pet in clone_pet_model:
            pet.close()

    def set_mouse_transparent(self, is_transparent: bool):
        if self.is_transparent_raise:
            return
        window_handle = int(self.winId())
        try:
            current_ex_style = ctypes.windll.user32.GetWindowLongW(window_handle, GWL_EX_STYLE)
            if is_transparent:
                new_ex_style = current_ex_style | WS_EX_TRANSPARENT
            else:
                new_ex_style = current_ex_style & ~WS_EX_TRANSPARENT

            ctypes.windll.user32.SetWindowLongW(window_handle, GWL_EX_STYLE, new_ex_style)
        except:
            self.is_transparent_raise = True

    def is_in_live2d_area(self, click_x: int | None = None, click_y: int | None = None):
        if click_x is None:
            click_x = QCursor.pos().x() - self.x()
        if click_y is None:
            click_y = QCursor.pos().y() - self.y()
        h = self.height()
        try:
            alpha = GL.glReadPixels(click_x * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    (h - click_y) * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    1, 1, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)[3]
        except GL.error.GLError:
            alpha = 0
        return alpha > 0

    def contextMenuEvent(self, a0):
        menu = RoundMenu("CLONEMENU", self)

        icon_path = _i[0] if (_i := glob.glob(f"./resources/model/{configure_default}/*.png")) else "logo.ico"
        card = ProfileCard(icon_path, configure['name'], configure_default,
                           languages[181].format(name=configure['name']), menu)
        menu.addWidget(card, selectable=False)

        menu.addSeparator()

        delete_me = Action(FluentIcon.DELETE, languages[180], self)
        delete_me.triggered.connect(self.delete_cloned)
        menu.addAction(delete_me)

        delete_all = Action(FluentIcon.CLOSE, languages[192], self)
        delete_all.triggered.connect(self.delete_all_cloned)
        menu.addAction(delete_all)

        menu.exec_(a0.globalPos())

    def timerEvent(self, a0):
        if not self.isVisible():
            return

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        self.pet_model.Drag(local_x, local_y)

        self.pet_model.SetScale(configure['settings']['size'])

        if self.is_in_live2d_area(local_x, local_y):
            self.set_mouse_transparent(False)
            self.click_in_area = True
        else:
            self.set_mouse_transparent(True)
            self.click_in_area = False

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.is_movement = True
            if self.drag_position is not None:
                if self.click_in_area:
                    new_pos = event.globalPos() - self.drag_position
                    if configure['settings']['enable']['locktsk']:
                        new_pos.setY(max(desktop.screen_geometry.height() - self.height(), new_pos.y()))
                    self.move(new_pos)

                event.accept()

    def initializeGL(self):
        self.pet_model = architecture.live2d.LAppModel()
        if self.direct_json_path is None:
            self.pet_model.LoadModelJson(desktop.model_json_path)
        else:
            self.pet_model.LoadModelJson(self.direct_json_path)
        self.pet_model.SetScale(configure['settings']['size'])
        self.startTimer(1)

    def resizeGL(self, w, h):
        self.pet_model.Resize(w, h)

    def paintGL(self):
        architecture.live2d.clearBuffer()
        self.pet_model.Update()
        self.pet_model.Draw()


class DesktopPet(shader.ADPOpenGLCanvas):
    def __init__(self, display_x: int | None = None, display_y: int | None = None):
        super().__init__()
        # 设置标题
        self.setWindowTitle("AgenticCompanion - Character Mainloop")
        # 设置图标
        self.setWindowIcon(QIcon("logo.ico"))
        # 设置属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        # 调整大小
        self.setFixedSize(400, 400)

        # 变量初始化
        self.has_output_text: str = ""
        self.fps_refresh = int(1000 / 900)
        self.continuous_conversation = self.rms_volume = self.turn_count = self.expression_count = 0
        self.model_json_path: str = ""
        self.amount = self.click_in_area = self.click_x = self.click_y = -1
        self.speaking_lists: list[bool] = []
        self.is_playing_expression = self.is_penetration = self.is_playing_animation = self.is_movement = False
        self.physics_constant = None
        self.speech_recognition = self.enter_position = self.drag_position = self.drag_start_position = None
        self.last_time = self.last_hypotenuse = self.image_path = self.direction = self.last_pos = None
        self.pet_model: architecture.live2d.LAppModel | None = None
        self.is_suction = self.is_continuous = self.is_generating = self.is_transparent_raise = False
        # 物理模拟
        self.speed_centimeter = self.angle_theta = 0.0
        # 初始化部分
        self.internal_record = runtime.thread.StartInternalRecording(visualization, 0.002)
        self.recognition_thread = runtime.thread.RecognitionThread(self, configure)
        self.recognition_thread.result.connect(self.recognition_success)
        self.look_timer = QTimer(self)

        # 移动位置
        self.screen_geometry = QApplication.desktop().availableGeometry()
        if display_x is not None and display_y is not None:
            self.move(display_x, display_y)
        else:
            # 屏幕中心坐标
            x = (self.screen_geometry.width() - self.width()) // 2
            y = self.screen_geometry.height() - self.height()
            self.move(x, y + 15)

    # GUI功能性配置
    def set_mouse_transparent(self, is_transparent: bool):
        """设置鼠标穿透 (透明部分可以直接穿过)"""
        if self.is_transparent_raise:
            return
        window_handle = int(self.winId())
        try:
            current_ex_style = ctypes.windll.user32.GetWindowLongW(window_handle, GWL_EX_STYLE)
            if is_transparent:
                # 添加WS_EX_TRANSPARENT样式以启用鼠标穿透
                new_ex_style = current_ex_style | WS_EX_TRANSPARENT
            else:
                # 移除WS_EX_TRANSPARENT样式以禁用鼠标穿透
                new_ex_style = current_ex_style & ~WS_EX_TRANSPARENT

            # 应用新的样式
            ctypes.windll.user32.SetWindowLongW(window_handle, GWL_EX_STYLE, new_ex_style)
        except Exception as mte:
            self.is_transparent_raise = True
            QMessageBox.warning(self, languages[105], f"{type(e).__name__}: {mte}")

    def set_window_below_taskbar(self):
        """设置低于任务栏(高于其它除了任务栏的应用)"""
        hwnd = self.winId().__int__()
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)

        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        win32gui.SetWindowPos(hwnd, taskbar_hwnd, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

    def is_in_live2d_area(self, click_x: int | None = None, click_y: int | None = None):
        """检查是否在模型内 Check whether the mouse is in the model"""
        if click_x is None:
            click_x = QCursor.pos().x() - self.x()
        if click_y is None:
            click_y = QCursor.pos().y() - self.y()
        h = self.height()
        try:
            alpha = GL.glReadPixels(click_x * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    (h - click_y) * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    1, 1, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)[3]
        except GL.error.GLError:
            alpha = 0
        return alpha > 0

    # 拍照
    @staticmethod
    def capture_screen():
        if not configure['settings']['enable']['media']:
            return

        def capture_screen(self):
            if not configure['settings']['enable']['media']:
                return
            interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setText(
                str(interface.subscribe.hooks.Operate.GetConversationInterface().input_question.text()) + "$[图片]$")
            self.image_path = runtime.capture()

    # 语音识别
    def recognize(self):
        if not configure['settings']['enable']['rec']:
            return
        if self.recognition_thread.isRunning():
            self.recognition_thread.wait()
        self.recognition_thread.start()

    def recognition_success(self, result: str):
        self.speech_recognition.statued()

        for action_item in interface.subscribe.actions.Operate.GetRecognitionOutput():
            if action_item(result) == interface.subscribe.standards.STOP_EXECUTING_NEXT:
                return

        if configure['name'] in result or configure_default in result:
        # if self.is_continuous or (configure['name'] in result or configure_default in result):
            # if result.strip():
            #     self.is_continuous = True
            # else:
            #     self.is_continuous = False
            #     return
            interface.subscribe.hooks.Operate.GetConversationInterface().show()
            self.change_status_for_conversation("show")
            self.have_conversation(result, True)
        runtime.file.logger(f"子应用 - 语音识别 语音呼唤成功\n"
                            f"Sub-Application - Voice Recognition Success: {result}\n"
                            f"  Message: {result}\n\n"
                            f"  Origin: {json.dumps(result, indent=3, ensure_ascii=False)}", logs.API_PATH)

    @staticmethod
    def recognition_failure(error, code):
        configure['settings']['enable']['rec'] = False
        runtime.file.save_configure(configure)
        runtime.file.logger(f"子应用 - 语音识别 发生错误 {code}:{error}\n"
                            f"Sub-Application - Voice Recognition Error: {code}:{error}\n", logs.API_PATH)

    @staticmethod
    def recognition_closure():
        pass

    # 音频可视化
    def audio_visualization(self):
        def draw(wav_bytes: bytes):
            self.rms_volume = runtime.calculate_rms(wav_bytes)
            if self.rms_volume > 0.1:
                visualization.show()
                visualization.draw_rectangle(self.rms_volume)
            else:
                visualization.hide()

        self.internal_record = runtime.thread.StartInternalRecording(visualization, 0.002)
        self.internal_record.data.connect(draw)
        self.internal_record.start()

    # 聊天
    def open_close_conversation(self):
        if not interface.subscribe.hooks.Operate.GetConversationInterface().isHidden():
            try: self.change_status_for_conversation("hide")
            except AttributeError: pass
            interface.subscribe.hooks.Operate.GetConversationInterface().hide()
        else:
            interface.subscribe.hooks.Operate.GetConversationInterface().show()
            try: self.change_status_for_conversation("show")
            except AttributeError: pass

    @staticmethod
    def change_status_for_conversation(status: typing.Literal['hide', 'show'],
                                       enable_chat_box: bool = True):
        status = True if status == "show" else False
        interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setVisible(status)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_send.setVisible(status)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_take_photo.setVisible(status)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_pop_answer.setVisible(status)
        if enable_chat_box:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setVisible(status)

    def conversation_display(self, text: list, current_index: int, temp_action: bool = False):
        def __temp():
            _temp_timer.stop()
            if not self.is_generating:
                self.change_status_for_conversation("hide")
                interface.subscribe.hooks.Operate.GetConversationInterface().hide()

        if current_index != self.continuous_conversation:
            return

        if text is None and not temp_action:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setGeometry(QRect(0, 430, 281, 30))
            self.change_status_for_conversation("show", False)
            return

        if text[1]:
            self.is_generating = False
            markdown_images = re.findall(r'!\[.*?]\((.*?)\)', text[0])
            for markdown_image in markdown_images:
                picture.open(markdown_image)
                picture.show()
                picture.move(self.x() - self.width(), self.y())
            interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setGeometry(QRect(0, 430, 281, 30))
            if temp_action:
                _temp_timer = QTimer(self)
                _temp_timer.timeout.connect(__temp)
                _temp_timer.start(5000)
            else:
                self.change_status_for_conversation("show", False)
        new_add_text = text[0].replace(self.has_output_text, "")
        exits_element = {k: v for k, v in rules.items() if k in new_add_text}
        if exits_element:
            self.playAnimationEvent(exits_element[list(rules.keys())[0]], "expr")
        if ((module_info and configure['settings']['tts']['way'] == "local") or
                configure['settings']['tts']['way'] == "cloud") and configure['settings']['enable']['tts'] and \
                text[1]:
            if configure['settings']['enable']['tts']:
                voice_generator = runtime.thread.VoiceGenerateThread(
                    self, configure, module_info, text[0])
                voice_generator.result.connect(lambda wave_bytes: runtime.thread.SpeakThread(self, wave_bytes).start())
                voice_generator.start()
        else:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.clear()
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setVisible(True)
            if text[1]:
                interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setMarkdown(text[0])
                self.has_output_text = ""
            else:
                self.is_generating = True
                interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setMarkdown(text[0])
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.moveCursor(
                interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.textCursor().End)
            if text is not None:
                if text[0][-2:] in rules.keys():
                    self.playAnimationEvent(rules[text[0][-2:]], "expr")
        self.has_output_text = text[0]

    def have_conversation(self, text: str | None = None, temp_action: bool | None = False):
        """进行聊天 Send conversation"""
        chat_message = str(interface.subscribe.hooks.Operate.GetConversationInterface().input_question.text()) if text is None else text
        if not chat_message.strip():
            return
        # 临时隐藏控件
        if temp_action:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setVisible(False)
        elif temp_action is None:
            interface.subscribe.hooks.Operate.GetConversationInterface().show()
            self.change_status_for_conversation("show")
        interface.subscribe.hooks.Operate.GetConversationInterface().click_send.setVisible(False)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_take_photo.setVisible(False)
        interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setText(f"{configure['name']} {languages[137]}")

        if self.image_path is None and "$[图片]$" not in interface.subscribe.hooks.Operate.GetConversationInterface().input_question.text():
            text_generate = runtime.thread.TextGenerateThread(
                self, configure, api_config, chat_message,
                True if configure['settings']['enable']['online'] else False,
            )
        else:
            text_generate = runtime.thread.MediaUnderstandThread(
                self, api_config, configure, self.image_path, chat_message.replace("$[图片]$", ""),
                True if configure['settings']['enable']['online'] else False,
            )
            self.image_path = None
        self.is_generating = True
        text_generate.start()
        self.continuous_conversation += 1
        current = self.continuous_conversation
        text_generate.result.connect(lambda texts, current_index=current: self.conversation_display(
            texts, current_index, temp_action))

    @staticmethod
    def clone_pet(_=None, model=None):
        json_model = None
        if model is not None:
            json_file = get_close_matches(f"{model}.model.json", os.listdir(f"./resources/model/{model}"))
            json_model = f"./resources/model/{model}/{json_file[0]}"
        clone_pet_model.append(ClonePet(json_model))
        try:
            clone_pet_model[-1].show()
        except (KeyError, IndexError):
            pass

    def physics(self):
        def animate():
            if (-0.2 <= self.physics_constant.velocity_y <= 0.1 and
                    self.pos().y() >= self.screen_geometry.height() - self.height()) or self.is_movement:
                timer.stop()
                return

            self.physics_constant.velocity_y += self.physics_constant.acceleration * configure['settings']['size']
            new_x = self.x() + self.physics_constant.velocity_x
            new_y = self.y() + self.physics_constant.velocity_y

            if new_y >= self.screen_geometry.height() - self.height():
                new_y = self.screen_geometry.height() - self.height()
                if configure['settings']['physics']['bounce']:
                    self.physics_constant.velocity_y *= -self.physics_constant.restitution
                    if abs(self.physics_constant.velocity_y) < 0.5:
                        self.physics_constant.velocity_y = 0
                else:
                    self.physics_constant.velocity_y = 0

            if new_x <= 0 or new_x + self.width() >= self.screen_geometry.width():
                self.physics_constant.velocity_x *= -0.7

            conversation.move(round(new_x), round(new_y) - 60)
            visualization.move(round(new_x), round(new_y) - 20)
            self.move(round(new_x), round(new_y))

        self.physics_constant = engine.physics.BasePhysics()
        if (abs(self.speed_centimeter) >= 6 and 10 <= self.angle_theta <= 70 and
                configure['settings']['physics']['dumping']) and not configure['settings']['enable']['locktsk']:
            self.physics_constant.velocity_y = -7.0
            self.physics_constant.velocity_x = self.speed_centimeter
        timer = QTimer(self)
        timer.timeout.connect(animate)
        timer.start(16)

    # 自定义事件
    @staticmethod
    def clear_memories():
        """清除记忆 Clear memories"""
        if intelligence is None:
            return
        intelligence.text.clear_memories()
        interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.clear()

    # 动画事件
    def finishedAnimationEvent(self):
        self.is_playing_animation = False
        self.turn_count = 0
        self.resetDefaultValueEvent()

    # 重置默认值事件
    def resetDefaultValueEvent(self):
        for param, values in live2d_parameter.items():
            if param == configure['watermark'].split(";")[0]:
                continue
            self.pet_model.SetParameterValue(param, values['default'], 1)

    # 加载模型事件
    def loadModelEvent(self, model, is_info: bool = False):
        try:
            model_files = os.listdir(f"./resources/model/{model}")
            # 寻找最像模型json文件的那一个文件
            model_json_file = get_close_matches(f"{model}.model.json", model_files)[0]
            self.model_json_path = (f"./resources/model/{model}/"
                                    f"{model_json_file}")
            # 加载架构
            if model_json_file.split(".")[1] == "model3":
                if is_info:
                    return 3, self.model_json_path
                if architecture.live2d.LIVE2D_VERSION != 3:
                    architecture.reload(3)
            elif model_json_file.split(".")[1] == "model":
                if is_info:
                    return 2, self.model_json_path
                if architecture.live2d.LIVE2D_VERSION != 2:
                    architecture.reload(2)
            else:
                raise FileNotFoundError()

            self.pet_model.LoadModelJson(self.model_json_path)
        except (KeyError, FileNotFoundError):
            configure['default'] = 'kasumi2'
            runtime.file.save_configure(configure)
            QMessageBox.critical(self, languages[71], languages[72])
            if QMessageBox.question(self, languages[71], languages[73]) == QMessageBox.Yes:
                runtime.file.load_template_model(configure, 'kasumi2')
                QMessageBox.information(self, languages[71], languages[74])
                runtime.file.save_configure(configure)
            self.exit_program()

    # 播放动画事件
    def playAnimationEvent(self, animation_name: str,
                           play_type: typing.Literal['expr', 'anime', 'event'] = 'event'):
        self.is_playing_expression = True
        if play_type != 'event':
            if play_type == 'expr':
                self.pet_model.SetExpression(animation_name)
            else:
                self.pet_model.StartMotion(
                    animation_name.split(":")[0], int(animation_name.split(":")[1]),
                    architecture.live2d.MotionPriority.FORCE, onFinishMotionHandler=self.finishedAnimationEvent)
            return
        if (exp := runtime.file.get_configure_actions(
                configure, configure_default,
                "nor" if "Touch" in animation_name or "Click" in animation_name else "spec")[
            animation_name]['expression'].strip()) != "":
            self.pet_model.SetExpression(exp)
        else:
            group, _, index = runtime.file.get_configure_actions(
                configure, configure_default,
                "nor" if "Touch" in animation_name or "Click" in animation_name else "spec")[
                animation_name]['motion'].split(":")
            self.pet_model.StartMotion(group, int(index), architecture.live2d.MotionPriority.FORCE,
                                       onFinishMotionHandler=self.finishedAnimationEvent)

    # 事件 Events
    # 右键菜单事件 Right-click menu events
    def contextMenuEvent(self, event):
        def show_setting_logics():
            if interface.subscribe.hooks.Operate.GetSettingInterface().isHidden():
                interface.subscribe.hooks.Operate.GetSettingInterface().show()
            else:
                interface.subscribe.hooks.Operate.GetSettingInterface().showNormal()
            hwnd = win32gui.FindWindow(None, languages[0])
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)

        def run_plugin(code, plugin_folder_, plugin_name_):
            interface.setting.customize.widgets.pop_notification(f"{plugin_name_}启动中……",
                                                                 "初始化", "warning", 1500)
            setting.run_code_for_plugin(
                code, -3, python_file=f"{os.getcwd()}/plugin/{plugin_folder_}/main.py")

        content_menu = RoundMenu("MENU", parent=self)

        icon_path = _i[0] if (_i := glob.glob(f"./resources/model/{configure_default}/*.png")) else "logo.ico"
        card = ProfileCard(icon_path, configure['name'], configure_default,
                           languages[182].format(name=configure['name']), content_menu)
        content_menu.addWidget(card, selectable=False)

        content_menu.addSeparator()

        settings_action = Action(FluentIcon.SETTING, languages[129], self)
        settings_action.triggered.connect(show_setting_logics)
        content_menu.addAction(settings_action)

        content_menu.addSeparator()

        conversation_action = Action(FluentIcon.HELP, languages[51], self)
        conversation_action.triggered.connect(self.open_close_conversation)
        content_menu.addAction(conversation_action)

        # 分割线
        content_menu.addSeparator()

        clone_action = Action(FluentIcon.COPY, languages[179], self)
        clone_action.triggered.connect(self.clone_pet)
        content_menu.addAction(clone_action)

        # 其他角色克隆
        as_another_clone_action = RoundMenu(languages[191], self)
        as_another_clone_action.setIcon(FluentIcon.SAVE_COPY)
        content_menu.addMenu(as_another_clone_action)
        for model in os.listdir("./resources/model"):
            if os.path.exists(f"./resources/model/{model}/{architecture.live2d.LIVE2D_VERSION}"):
                clone_model = Action(model, self)
                clone_model.triggered.connect(lambda _, m=model: self.clone_pet(_, m))
                as_another_clone_action.addAction(clone_model)

        # 插件启动
        for independent_plugin_list in independent_plugin_lists:
            if not os.path.exists(f"./plugin/{independent_plugin_list}/main.py"):
                continue
            with open(f"./plugin/{independent_plugin_list}/main.py", "r", encoding="utf-8") as pf:
                plugin_codes = pf.read()
                pf.close()
            try:
                if hasattr(FluentIcon, plugin_requirements[independent_plugin_list]['static']):
                    icon = getattr(FluentIcon, plugin_requirements[independent_plugin_list]['static'])
                else:
                    if os.path.exists(plugin_requirements[independent_plugin_list]['static']):
                        icon = QIcon(plugin_requirements[independent_plugin_list]['static'])
                    else:
                        icon = QIcon("./resources/static/extension.png")
                _run_python_plugin_action = Action(icon,
                                                   plugin_requirements[independent_plugin_list]['name'],
                                                   self)
                _run_python_plugin_action.triggered.connect(
                    lambda _, p=plugin_codes,
                           ipf=independent_plugin_list,
                           npf=plugin_requirements[independent_plugin_list]['name']: run_plugin(p, ipf, npf))
                content_menu.addAction(_run_python_plugin_action)
            except KeyError:
                continue

        # 插件的内置interface
        for views_item in interface.subscribe.views.Operate.GetContentMenu():
            if isinstance(views_item, RoundMenu):
                views_item.setParent(self)
                content_menu.addMenu(views_item)
            elif isinstance(views_item, Action):
                views_item.setParent(self)
                views_item.setText("1")
                content_menu.addAction(views_item)

        content_menu.addSeparator()

        exit_action = Action(FluentIcon.CLOSE, languages[20], self)
        exit_action.triggered.connect(self.exit_program)
        content_menu.addAction(exit_action)

        content_menu.exec_(self.mapToGlobal(event.pos()))

    def save_change(self):
        self.is_penetration = False
        # 刷新设置的缓存文件
        switches_configure['Advanced']['penetration'] = "shut"
        runtime.file.save_switch(switches_configure)
        self.set_mouse_transparent(False)
        self.setCanvasOpacity(configure['settings']['transparency'])

    # 定时器事件 Timer events
    def timerEvent(self, a0: QTimerEvent | None) -> None:
        def check_mouse_pressed(left_condition: str, right_condition: str):
            if not MouseListener.isListening:
                MouseListener.start_listening()
            if switches_configure['Advanced']['penetration'] == left_condition:
                pressed = MouseListener.is_left_button_pressed
            elif switches_configure['Advanced']['penetration'] == right_condition:
                pressed = MouseListener.is_right_button_pressed
            else:
                pressed = False
            if not MouseListener.isListening:
                MouseListener.start_listening()
            return pressed

        if not self.isVisible():
            return
        # 设置旋转交
        self.setRotationAngle(configure['settings']['angle'])
        # 设置大小
        self.pet_model.SetScale(configure['settings']['size'])
        # 设置透明度
        self.setCanvasOpacity(configure['settings']['transparency'])
        # 判断兼容性
        if configure["settings"]["compatibility"] is False and self.amount == 100:
            # 判断顺序是否低于任务栏
            hwnd = self.winId().__int__()
            taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
            if win32gui.GetWindowRect(hwnd)[1] < win32gui.GetWindowRect(taskbar_hwnd)[1]:
                self.set_window_below_taskbar()

        # 检查识别器
        if not self.recognition_thread.isRunning() and configure['settings']['enable']['rec']:
            self.recognize()
        elif self.speech_recognition is not None and not configure['settings']['enable']['rec']:
            self.speech_recognition.closed()

        # 定时器检查
        if not configure['settings']['enable']['media']:
            if self.look_timer.isActive():
                self.look_timer.stop()
        else:
            if not self.look_timer.isActive():
                self.look_timer.start(random.randint(
                    configure['settings']['understand']['min'],
                    configure['settings']['understand']['max']) * 1000)
        if configure['settings']['enable']['realtimeAPI'] and not RealtimeServer.running:
            RealtimeServer.start()
        elif not configure['settings']['enable']['realtimeAPI']:
            RealtimeServer.stop()
        # 释放资源
        # 检查说话列表的可用性
        if len(self.speaking_lists) == self.speaking_lists.count(False) and not self.speaking_lists:
            # 清除缓存
            self.speaking_lists.clear()

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        if configure['settings']['live2d']['enable']['AutoDrag']:
            self.pet_model.Drag(local_x, local_y)
        # 检查是否开启全局鼠标穿透
        if False:
        # if switches_configure['Advanced']['penetration'] != "shut":
            self.setCanvasOpacity(0.4)
            self.set_mouse_transparent(True)
            self.is_penetration = True
            # 如果start有以下几种情况，则取消全局鼠标穿透
            # 下次启动时取消全局鼠标穿透
            if switches_configure['Advanced']['penetration'] == "next" and self.amount == -1:
                self.save_change()
            # 鼠标左键或右键在顶部按下时取消全局鼠标穿透
            elif switches_configure['Advanced']['penetration'] in ('left-top', 'right-top'):
                if self.is_in_live2d_area(local_x, local_y) and check_mouse_pressed('left-top', 'right-top') and \
                        80 / configure['settings']['size'] > local_y > 0:
                    MouseListener.stop_listening()
                    self.save_change()
            # 鼠标左键或右键在底部按下时取消全局鼠标穿透
            elif switches_configure['Advanced']['penetration'] in ('left-bottom', 'right-bottom'):
                if self.is_in_live2d_area(local_x, local_y) and check_mouse_pressed('left-bottom',
                                                                                    'right-bottom') and \
                        self.height() > local_y > (self.height() - 80) * configure['settings']['size']:
                    MouseListener.stop_listening()
                    self.vsave_change()
        # elif switches_configure['Advanced']['penetration'] == "shut" and self.amount == 0:
        #     self.save_change()

        # 检查是否开启音频可视化
        if configure['settings']['enable']['visualization']:
            if not self.internal_record.isRunning():
                visualization.show()
                self.audio_visualization()
        else:
            self.internal_record.stop()
            visualization.hide()

        # 检查表情
        if self.expression_count >= 300 * self.fps_refresh:
            self.is_playing_expression = False
            self.pet_model.ResetExpression()
        if self.is_playing_expression:
            self.expression_count += self.fps_refresh
        else:
            self.expression_count = 0
        # 检查点击区域
        if self.is_in_live2d_area(local_x, local_y) and not self.is_penetration:
            self.set_mouse_transparent(False)
            self.click_in_area = True
        elif not self.is_penetration:
            self.set_mouse_transparent(True)
            self.turn_count = 0
            self.click_in_area = False

        # 循环次数
        if self.amount > 100:
            self.amount = 0
        self.amount += 1

        self.update()

    # 过滤器事件 Filter events
    def eventFilter(self, obj, event):
        if obj is interface.subscribe.hooks.Operate.GetConversationInterface().input_question and event.type() == event.KeyPress:
            # 是否按下 Shift + Enter
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if event.modifiers() & Qt.ShiftModifier and interface.subscribe.hooks.Operate.GetConversationInterface().click_send.isVisible():
                    interface.subscribe.hooks.Operate.GetConversationInterface().click_send.click()
                    return True
                else:
                    return False
        return super().eventFilter(obj, event)

    # 鼠标拖动事件
    def mousePressEvent(self, event):
        x, y = event.globalPos().x(), event.globalPos().y()
        if self.is_in_live2d_area(QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()):
            self.click_in_area = True
            self.click_x, self.click_y = x, y

        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.drag_start_position = QPoint(event.globalPos().x(), event.globalPos().y())
        event.accept()

    def mouseMoveEvent(self, event):
        def checker(parameter: str, turn_count: int) -> bool:
            """检查是否满足框内要求"""
            x_min, x_max, y_min, y_max = runtime.file.get_configure_actions(
                configure, configure_default)[parameter]['position']
            return (
                    x_min <= current_x <= x_max and y_min <= current_y <= y_max and
                    not self.is_playing_animation and self.turn_count >= turn_count and self.click_in_area
            )

        x, y = QCursor.pos().x() - self.x(), QCursor.pos().y()
        current_pos = event.pos()
        current_x = current_pos.x()
        current_y = current_pos.y()
        current_time = time.time()

        # 算改变方向
        if self.last_pos is not None:
            last_x, last_y = self.last_pos.x(), self.last_pos.y()

            # 状态
            if current_x > last_x:
                new_direction = 'right'
            elif current_x < last_x:
                new_direction = 'left'
            else:
                new_direction = self.direction

            # 检查方向是否改变
            if self.direction is not None and new_direction != self.direction:
                self.turn_count += 1

            self.direction = new_direction

        self.last_pos = current_pos

        # 接触式
        if event.buttons() & Qt.LeftButton and self.drag_position is not None:
            # 算物理模拟部分
            # 距离原点的变化量
            delta_x = QCursor.pos().x() - self.drag_start_position.x()
            delta_y = QCursor.pos().y() - self.drag_start_position.y()
            hypotenuse = math.sqrt(abs(delta_x) ** 2 + abs(delta_y) ** 2)
            if delta_x != 0:
                # 根据直角边由三角函数算出角度
                self.angle_theta = math.degrees(math.atan(abs(delta_y) / abs(delta_x)))
                if self.last_time is None:
                    self.last_time = current_time
                    self.last_hypotenuse = hypotenuse
                else:
                    time_difference = current_time - self.last_time
                    if time_difference > 0:
                        speed_pixel = hypotenuse / time_difference
                        self.speed_centimeter = (speed_pixel * 2.54 / DPI_SCALE_NORMAL) * time_difference
                        if self.direction == 'left':
                            self.speed_centimeter = -self.speed_centimeter

                    self.last_time = current_time
                    self.last_hypotenuse = hypotenuse

            self.is_movement = True
            if self.click_in_area:
                cv_new_pos = event.globalPos() - self.drag_position
                new_pos = event.globalPos() - self.drag_position
                if configure['settings']['enable']['locktsk']:
                    new_pos.setY(max(self.screen_geometry.height() - self.height(), new_pos.y()))
                    cv_new_pos.setY(max(self.screen_geometry.height() - self.height() - 60, new_pos.y() - 60))
                else:
                    cv_new_pos.setY(new_pos.y() - 60)
                self.move(new_pos)

                for action_item in interface.subscribe.actions.Operate.GetMouseDragAction():
                    action_item(x, y, self.x(), self.y())

                picture.move(self.x() - self.width(), self.y())
                interface.subscribe.hooks.Operate.GetConversationInterface().move(cv_new_pos)
                cv_new_pos.setY(cv_new_pos.y() + 40)
                visualization.move(cv_new_pos)
            event.accept()

        # 非接触悬浮鼠标的互动
        elif self.enter_position and not event.buttons() & Qt.LeftButton:
            # 处理互动事件/动画
            # 互动事件/动画
            if self.click_in_area and not self.is_movement:
                # 摸头互动
                if checker('ActionTouchHead', 4):
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, 'ActionTouchHead')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    # 播放动画
                    self.playAnimationEvent('ActionTouchHead')
                # 摸腿互动
                if checker('ActionTouchLeg', 4):
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, 'ActionTouchLeg')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    self.playAnimationEvent('ActionTouchLeg')
                # 自定义互动
                if checker('ActionTouchCustom', 4):
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, 'ActionTouchCustom')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    self.playAnimationEvent('ActionTouchCustom')

        for action_item in interface.subscribe.actions.Operate.GetMouseMoveAction():
            action_item()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        def checker(parameter_action: str):
            """检查点击位置是否符合标准 Check whether the click position meets the standards"""
            x_min, x_max, y_min, y_max = runtime.file.get_configure_actions(
                configure, configure_default)[parameter_action]['position']
            return x_min <= click_x <= x_max and y_min <= click_y <= y_max \
                and not self.is_playing_animation

        click_x, click_y = event.globalPos().x() - self.x(), event.globalPos().y() - self.y()
        if event.button() == Qt.LeftButton and self.click_in_area:
            # 记录位置
            if configure['record']['enable_position']:
                if configure['record']['position'][:2].count(-1) == len(configure['record']['position'][:2]):
                    configure['record']['position'][:2] = [click_x, click_y]
                else:
                    configure['record']['position'][2:] = [click_x, click_y]
                    configure['record']['enable_position'] = False

            # 点击事件/动画
            # 胸部点击行为
            if checker("ActionClickChest"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickChest')
                if configure['adult_level'] > 0:
                    dir_, voice_list = engine.adult.AdultEngine(configure).voice()
                    runtime.thread.SpeakThread(self,
                                               f"./resources/adult/{configure_default}/voice/{dir_}/"
                                               f"{random.choice(voice_list)}").start()
                else:
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, "ActionClickChest")).start()
            # 帽点击行为
            elif checker("ActionClickCap"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickCap')
                runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, "ActionClickCap")).start()
            elif checker("ActionClickCustom"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickCustom')
                runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, "ActionClickCustom")).start()

            for action_item in interface.subscribe.actions.Operate.GetClckAction():
                try:
                    action_item()
                except Exception as me:
                    interface.setting.customize.widgets.pop_error(setting, 'Error', str(me))
            event.accept()
        if not self.is_movement and event.button() == Qt.LeftButton:
            for action_item in interface.subscribe.actions.Operate.GetMouseReleaseAction():
                action_item()
        # 查看是否靠近右侧屏幕
        if self.x() + (self.width() // 2) > self.screen_geometry.width() - 50:
            # 旋转15度吸附
            self.is_suction = True
            self.move(self.screen_geometry.width() - (self.width() // 2) + 10, self.y())
            configure['settings']['angle'] = 15
        elif self.x() < -170:
            self.is_suction = True
            self.move(-200, self.y())
            configure['settings']['angle'] = -15
        else:
            if self.is_suction:
                self.is_suction = False
                configure['settings']['angle'] = 0

        self.is_movement = False
        if configure['settings']['physics']['total']:
            self.physics()

    # 鼠标进入事件 Mouse entry event
    def enterEvent(self, event):
        self.turn_count = 0
        self.enter_position = event.pos()
        for action_item in interface.subscribe.actions.Operate.GetMouseEnterAction():
            action_item()

    # 鼠标离开事件 Mouse leave event
    def leaveEvent(self, event):
        # self.is_movement = False
        self.enter_position = None
        self.is_playing_animation = False
        for action_item in interface.subscribe.actions.Operate.GetMouseLeaveAction():
            action_item()

    # 拖拽事件 Drag event
    def dragEnterEvent(self, event: QDropEvent):
        action = engine.actions.ActionsEngine(configure, languages, interface)
        action.analyze_action(event.mimeData().text())
        for action_item in interface.subscribe.actions.Operate.GetDragEnterAction():
            action_item(event, action.analyzed_action)
        event.accept()

    def dragLeaveEvent(self, event):
        for action_item in interface.subscribe.actions.Operate.GetDragLeaveAction():
            action_item(event, None)
        event.accept()

    def dragMoveEvent(self, event: QDropEvent):
        action = engine.actions.ActionsEngine(configure, languages, interface)
        action.analyze_action(event.mimeData().text())
        for action_item in interface.subscribe.actions.Operate.GetDragMoveAction():
            action_item(event, action.analyzed_action)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        action = engine.actions.ActionsEngine(configure, languages, interface)
        action.analyze_action(event.mimeData().text())
        for action_item in interface.subscribe.actions.Operate.GetDropAction():
            action_item(event, action.analyzed_action)
        action.accept_action()
        event.accept()

    # OpenGL 事件
    def on_init(self):
        architecture.live2d.glewInit()
        self.pet_model = architecture.live2d.LAppModel()
        desktop.loadModelEvent(configure_default)
        self.pet_model.SetScale(configure['settings']['size'])
        # 初始化载入
        self.playAnimationEvent("ActionLogin")
        runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
            configure, configure_default, "ActionLogin")).start()
        live2d_parameter.clear()

        for i in range(self.pet_model.GetParameterCount()):
            param = self.pet_model.GetParameter(i)
            live2d_parameter.update({str(param.id): {
                "value": param.value, "max": param.max, "min": param.min, "default": param.default,
            }})
        live2d_parameter.update({"Keep@NullParameter": {"value": 0.0, "max": 0.0, "min": 0.0, "default": 0.0}})
        interface.subscribe.RegisterAttribute.SetPet(self.pet_model)
        self.startTimer(self.fps_refresh)

    def on_resize(self, width, height):
        self.pet_model.Resize(width, height)

    def on_draw(self):
        architecture.live2d.clearBuffer()
        try:
            self.pet_model.Update()
            if "ParamMouthOpenY" in live2d_parameter.keys():
                self.pet_model.AddParameterValue("ParamMouthOpenY", min(
                    live2d_parameter["ParamMouthOpenY"]['max'], self.rms_volume / 100))
            # 清除水印
            try:
                watermark_param = configure['watermark'].split(";")[0]
                watermark_value = configure['watermark'].split(";")[1]
                self.pet_model.SetParameterValue(
                    watermark_param,
                    float(watermark_value) if "." in watermark_value else int(watermark_value), 1)
            except ValueError:
                pass
            # 加载Live2D开关
            self.pet_model.SetAutoBlinkEnable(
                configure['settings']['live2d']['enable']['AutoBlink'])
            self.pet_model.SetAutoBreathEnable(
                configure['settings']['live2d']['enable']['AutoBreath'])
            # 加载模型 Load Model
            self.pet_model.Draw()
        except SystemError:
            pass

    def exit_program(self):
        for proc in subprocess_running:
            proc.terminate()
            proc.wait()
        for action_item in interface.subscribe.hooks.Operate.GetHookCloseProgram():
            action_item()
        system_tray.hide()
        architecture.live2d.dispose()
        self.close()

        try:
            os.remove("./logs/backup/configure.json")
        except FileNotFoundError:
            pass
        shutil.copy2("./resources/configure.json", "./logs/backup/configure.json")
        runtime.file.logger("程序退出 Program exit", logs.HISTORY_PATH)
        runtime.file.write_file("./engine/static/scripts.js",
                                js_code.replace(f"http://{gethostbyname(gethostname())}:52013",
                                                "{PYTHON_UPLOAD_URL_ADDRESS}"))
        os.kill(os.getpid(), __import__("signal").SIGINT)


def realtime_api_started():
    interface.setting.customize.widgets.pop_notification("Realtime API", languages[212], "warning")


def realtime_api_stopped():
    interface.setting.customize.widgets.pop_notification("Realtime API", languages[213], "success")


def realtime_api_caller(calling, parameter):
    """Realtime API 实时 API获得参数的设定"""
    calling_blocks = calling.split(".")
    enum_call = getattr(interface, calling_blocks[0])
    for calling_block in calling_blocks:
        if calling_block == calling_blocks[0]:
            continue
        enum_call = getattr(enum_call, calling_block)
    if callable(enum_call):
        if isinstance(parameter, dict):
            return enum_call(**parameter)
        else:
            return enum_call(*parameter)
    else:
        return enum_call


clone_pet_model: list[ClonePet] = []
independent_plugin_lists: list = []
subprocess_running: list[subprocess.Popen] = []
MouseListener = runtime.MouseListener()
if __name__ != "__main__":
    # 前置
    with open('./engine/static/scripts.js', 'r', encoding='utf-8') as f:
        js_code = f.read().replace("{PYTHON_UPLOAD_URL_ADDRESS}", f"http://{gethostbyname(gethostname())}:52013")
        f.close()
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    runtime.file.write_file("./engine/static/scripts.js", js_code)
    app = QApplication(sys.argv)

    DPI_SCALE_NORMAL = app.primaryScreen().logicalDotsPerInch()
    # 实时API服务
    RealtimeServer = interface.realtime.UDPServer()
    RealtimeServer.calling.connect(realtime_api_caller)
    RealtimeServer.server_started.connect(realtime_api_started)
    RealtimeServer.server_stopped.connect(realtime_api_stopped)

    translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))
    app.installTranslator(translator)

    DeveloperOptions = interface.setting.dev.DeveloperOptions()
    PLUGIN_GLOBAL['interface'] = interface
    PLUGIN_GLOBAL['print'] = DeveloperOptions.print_
    PLUGIN_GLOBAL['input'] = DeveloperOptions.input_

    visualization = AudioVisualization()
    desktop = DesktopPet()
    desktop.show()
    setting = Setting()
    compile_progress = CompileProgress()
    conversation = Conversation()
    system_tray = SystemTray()

    # 注册接口
    interface.subscribe.interact.Register.SetLargeLanguageModel(
        lambda text: desktop.have_conversation(text, None)
    )
    interface.subscribe.hooks.Register.HookConversationInterface(conversation)
    interface.subscribe.RegisterAttribute.SetWindow(desktop)
    interface.subscribe.interact.Register.SetConversationInteraction(conversation)
    interface.subscribe.views.Register.register("desktop", desktop)
    interface.subscribe.views.Register.register("setting", setting)
    interface.subscribe.views.Register.register("conversation", conversation)
    interface.subscribe.hooks.Register.HookSettingInterface(setting)

    interface.subscribe.hooks.Operate.GetConversationInterface().move(desktop.x(), desktop.y() - 60)
    system_tray.show()
    visualization.move(desktop.x(), desktop.y() - 20)
    picture = PictureShow()

    # 启动插件
    with open("./plugin/desc.json", "r", encoding="utf-8") as f:
        plugin_requirements = json.load(f)
        f.close()
    for plugin_folder in os.listdir(f"./plugin"):
        if plugin_folder == "desc.json":
            continue
        with open(f"./plugin/{plugin_folder}/main.py", "r", encoding="utf-8") as f:
            codes = f.read()
            f.close()
        try:
            if plugin_requirements[plugin_folder]['attr'] in (-2, -4):
                setting.run_code_for_plugin(codes, plugin_requirements[plugin_folder]['attr'], True)
            else:
                independent_plugin_lists.append(plugin_folder)
        except KeyError:
            continue
    # 启动网页
    threading.Thread(target=webui.run).start()
else:
    print("?")
    sys.exit(0)
