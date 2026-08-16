from urllib.parse import quote
import tempfile
from zipfile import ZipFile
import os
import shutil
import glob
import json

from .customize import widgets

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt, QThread, pyqtSignal, QUrl, QIcon, QObject, QRect
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtGui import QPixmap
from qfluentwidgets import FluentIcon, ScrollArea, ExpandLayout, SettingCardGroup, PrimaryPushSettingCard, ProgressBar, \
    BodyLabel


class PluginFill(QThread):
    plugin_signal = pyqtSignal(dict)

    def __init__(self, parent, runtime):
        super().__init__(parent)
        self.runtime = runtime

    def run(self):
        plugins = self.runtime.get_plugin()
        self.plugin_signal.emit(plugins)


class Fill(QThread):
    dict_signal = pyqtSignal(dict)

    def __init__(self, parent, runtime):
        super().__init__(parent)
        self.runtime = runtime

    def run(self):
        self.dict_signal.emit(self.runtime.get_shop_model())


class Download(QObject):
    finished = pyqtSignal(str)

    def __init__(self, parent, url, runtime, configure, index):
        super().__init__(parent)
        self.url = url
        self.runtime = runtime
        self.configure = configure
        self.index = index
        self.reply = None
        self.manager = QNetworkAccessManager(self)

    def start(self):
        self.parent().cards[self.index].button.setText(self.parent().languages[203])
        self.parent().cards[self.index].setEnabled(False)
        self.reply = self.manager.get(QNetworkRequest(QUrl(self.url)))
        self.reply.downloadProgress.connect(self.on_download_progress)
        self.reply.finished.connect(self.on_finished)

        widgets.pop_notification(self.parent().languages[207],
                                 self.parent().languages[208].format(name=self.url.split('/')[-1].split('.')[0]),
                                 "warning")

    def on_download_progress(self, bytesReceived, bytesTotal):
        self.parent().progress_bar.setMaximum(bytesTotal)
        self.parent().progress_bar.setValue(bytesReceived)

    def on_finished(self):
        def check_if_live2d(path: str):
            exist_v3_over = glob.glob(f"{path}/*.model3.json")
            if exist_v3_over:
                return glob.glob(f"{path}/*.model3.json"), 3
            else:
                return glob.glob(f"{path}/*.model.json"), 2

        if self.reply.error() != QNetworkReply.NoError:
            widgets.pop_notification(self.parent().languages[204], self.reply.errorString(), "error")
            return

        file_name = self.url.split('/')[-1]
        file_path = os.path.join(tempfile.gettempdir(), file_name)
        extract_folder = os.path.join(os.getcwd(), "resources", "model")

        # 保存下载的文件
        with open(file_path, 'wb') as f:
            f.write(self.reply.readAll().data())

        # 解压文件
        with ZipFile(file_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            zip_ref.extractall(extract_folder)

        model_name = file_name.split('.')[0]
        target_folder = os.path.join(extract_folder, model_name)

        # 简化文件移动逻辑
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)
            self._extract_and_move_files(zip_contents, extract_folder, target_folder)

        # 后续处理
        self.runtime.file.load_template_model(self.configure, model_name)
        live2d, arch = check_if_live2d(f"./resources/model/{model_name}")
        with open(f"./resources/model/{model_name}/{arch}", "w", encoding="utf-8") as f:
            f.write(f"This is a architecture explanation file\nYour architecture is {arch}")
        self.parent().cards[self.index].button.setText(self.parent().languages[205])
        widgets.pop_notification(self.parent().languages[209],
                                 f"{model_name} {self.parent().languages[209]}", "success")
        self.finished.emit(model_name)

    def _extract_and_move_files(self, zip_contents, extract_folder, target_folder):
        """
        简化版文件提取和移动逻辑
        """
        top_level_items = set(item.split('/')[0] for item in zip_contents)

        # 如果只有一个顶级目录，直接处理
        if len(top_level_items) == 1:
            possible_folder_name = list(top_level_items)[0]
            source_folder = os.path.join(extract_folder, possible_folder_name)

            if os.path.exists(source_folder) and os.path.isdir(source_folder):
                # 移动目录内容
                for item in os.listdir(source_folder):
                    src = os.path.join(source_folder, item)
                    dst = os.path.join(target_folder, item)
                    shutil.move(src, dst)
                os.rmdir(source_folder)
            elif os.path.exists(source_folder):
                # 直接移动文件
                shutil.move(source_folder, target_folder)
            else:
                # 处理zip中的文件结构
                self._move_zip_contents(zip_contents, extract_folder, target_folder)
        else:
            # 多个顶级项目，直接移动
            self._move_zip_contents(zip_contents, extract_folder, target_folder)

    def _move_zip_contents(self, zip_contents, extract_folder, target_folder):
        """
        移动zip内容到目标文件夹
        """
        for item in zip_contents:
            src = os.path.join(extract_folder, item)
            if os.path.exists(src):
                dst_dir = os.path.join(target_folder, os.path.dirname(item))
                dst = os.path.join(dst_dir, os.path.basename(item))
                os.makedirs(dst_dir, exist_ok=True)

                # 如果目标已存在，先删除
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                shutil.move(src, dst)


class PluginDownload(QObject):
    finished = pyqtSignal(str)

    def __init__(self, parent, url, config, runtime, configure, index):
        super().__init__(parent)
        self.url = url
        self.config = config
        self.runtime = runtime
        self.configure = configure
        self.index = index
        self.reply = None
        self.manager = QNetworkAccessManager(self)

    def start(self):
        self.parent().plugin_cards[self.index].button.setText(self.parent().languages[203])
        self.parent().plugin_cards[self.index].setEnabled(False)
        self.reply = self.manager.get(QNetworkRequest(QUrl(self.url)))
        self.reply.downloadProgress.connect(self.on_download_progress)
        self.reply.finished.connect(self.on_finished)

        widgets.pop_notification(self.parent().languages[207],
                                 self.parent().languages[208].format(name=self.url.split('/')[-1].split('.')[0]),
                                 "warning")

    def on_download_progress(self, bytesReceived, bytesTotal):
        self.parent().progress_bar.setMaximum(bytesTotal)
        self.parent().progress_bar.setValue(bytesReceived)

    def on_finished(self):
        print(self.index)
        if self.reply.error() != QNetworkReply.NoError:
            widgets.pop_notification(self.parent().languages[204], self.reply.errorString(), "error")
            return

        file_name = self.url.split('/')[-1]
        file_path = os.path.join(tempfile.gettempdir(), file_name)
        extract_folder = "./plugin"

        with open(file_path, 'wb') as f:
            f.write(self.reply.readAll().data())

        with ZipFile(file_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            zip_ref.extractall(extract_folder)

        plugin_name = file_name.split('.')[0]
        target_folder = os.path.join(extract_folder, plugin_name)

        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)

            top_level_items = set(item.split('/')[0] for item in zip_contents)

            if len(top_level_items) == 1:
                possible_folder_name = list(top_level_items)[0]
                extracted_folder = os.path.join(extract_folder, possible_folder_name)

                if os.path.exists(extracted_folder):
                    if os.path.isdir(extracted_folder):
                        for item in os.listdir(extracted_folder):
                            src = os.path.join(extracted_folder, item)
                            dst = os.path.join(target_folder, item)
                            shutil.move(src, dst)
                        os.rmdir(extracted_folder)
                    else:
                        shutil.move(extracted_folder, target_folder)
                else:
                    for item in zip_contents:
                        src = os.path.join(extract_folder, item)
                        dst_dir = os.path.join(target_folder, os.path.dirname(item))
                        dst = os.path.join(dst_dir, os.path.basename(item))

                        if os.path.exists(src):
                            os.makedirs(dst_dir, exist_ok=True)
                            if os.path.exists(dst):
                                if os.path.isdir(dst):
                                    shutil.rmtree(dst)
                                else:
                                    os.remove(dst)
                            shutil.move(src, dst)
            else:
                for item in zip_contents:
                    src = os.path.join(extract_folder, item)
                    dst_dir = os.path.join(target_folder, os.pathdirname(item))
                    dst = os.path.join(dst_dir, os.path.basename(item))

                    if os.path.exists(src):
                        os.makedirs(dst_dir, exist_ok=True)
                        if os.path.exists(dst):
                            if os.path.isdir(dst):
                                shutil.rmtree(dst)
                            else:
                                os.remove(dst)
                        shutil.move(src, dst)

        os.rename(f"./plugin/{plugin_name}", f"./plugin/"
                                             f"{list(self.config.keys())[0]}")
        self.parent().plugin_cards[self.index].button.setText(self.parent().languages[205])
        with open("./plugin/desc.json", "r", encoding="utf-8") as f:
            desc = json.load(f)
            f.close()
        desc.update(self.config)
        with open("./plugin/desc.json", "w", encoding="utf-8") as f:
            json.dump(desc, f, indent=3, ensure_ascii=False)
            f.close()
        widgets.pop_notification(self.parent().languages[209],
                                 f"{plugin_name} {self.parent().languages[209]}", "success")
        self.finished.emit(plugin_name)



class CloudDownload(ScrollArea):
    def __init__(self, languages, configure, runtime_module, add_function: callable, add_interface: callable):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.runtime = runtime_module
        self.add_function = add_function
        self.add_interface = add_interface
        self.setObjectName("CloudDownload")

        self.cards = []
        self.plugin_cards = []

        self.scroll_widgets = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widgets)

        self.progress_bar = ProgressBar(self)
        self.progress_bar.setMinimum(0)

        # 模型下载
        self.model_download_group = SettingCardGroup(self.languages[202], self.scroll_widgets)
        # 插件下载
        self.plugin_download_group = SettingCardGroup(self.languages[210], self.scroll_widgets)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(36, 52, 36, 0)

        self.expand_layout.addWidget(self.model_download_group)
        self.expand_layout.addWidget(self.plugin_download_group)
        self.progress_bar.setGeometry(QRect(10, 520, 620, 20))
        BodyLabel(self.languages[197], self).setGeometry(QRect(10, 500, 620, 20))

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.scroll_widgets)
        self.scroll_widgets.setObjectName('1ScrollWidget')

        fill = Fill(self, self.runtime)
        fill.dict_signal.connect(self.fill_information)
        fill.start()

        plugin_fill = PluginFill(self, self.runtime)
        plugin_fill.plugin_signal.connect(self.fill_plugins)
        plugin_fill.start()

    def fill_plugins(self, result):
        self.plugin_cards = [None] * len(result['static'])
        for index, icon in enumerate(result['static']):
            manager = QNetworkAccessManager(self)
            manager.finished.connect(lambda r, i=index, res=result: self.icon_finished(r, i, res, "plugin"))
            manager.get(QNetworkRequest(QUrl(quote(icon).replace("%3A", ":"))))

    def fill_information(self, result):
        self.cards = [None] * len(result['static'])
        for index, icon in enumerate(result['static']):
            manager = QNetworkAccessManager(self)
            manager.finished.connect(lambda r, i=index, res=result: self.icon_finished(r, i, res, "model"))
            manager.get(QNetworkRequest(QUrl(quote(icon).replace("%3A", ":"))))

    def icon_finished(self, reply, index, result, type_):
        if reply.error():
            return
        data = reply.readAll()

        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if pixmap.isNull():
            return

        if type_ == "model":
            match = result['name'][index]
            matches = os.listdir("./resources/model/")
        else:
            match = list(result['config'][index].keys())[0]
            matches = os.listdir("./plugin/")
        card = PrimaryPushSettingCard(
            icon=QIcon(pixmap),
            text=self.languages[205] if match in matches else self.languages[201],
            title=result['name'][index],
            content=result['description'][index]
        )
        card.setIconSize(40, 40)
        card.setEnabled(False if match in matches else True)
        if type_ == "model":
            self.cards[index] = card
            download = Download(self, result['url'][index], self.runtime, self.configure, index)
            download.finished.connect(self.add_function)
        else:
            self.plugin_cards[index] = card
            download = PluginDownload(self, result['url'][index], result['config'][index],
                                      self.runtime, self.configure, index)
        card.clicked.connect(download.start)
        if type_ == "model":
            self.model_download_group.addSettingCard(card)
        else:
            self.plugin_download_group.addSettingCard(card)
        self.add_interface(self, FluentIcon.CLOUD, self.languages[206])
