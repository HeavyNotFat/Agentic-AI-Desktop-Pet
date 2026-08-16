import json
import os
import shutil
import winreg

from ..customize import function, widgets

from PyQt5.Qt import QRect, QTimer, QFileDialog
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import BodyLabel, ComboBox, LineEdit, PrimaryPushButton


with open("./resources/template.json", "r", encoding="utf-8") as f:
    template = json.load(f)
    f.close()


class AnimationBinding(QWidget):
    def __init__(self, languages, configure, model_json_path, live2d_custom, **kwargs):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.kwargs = kwargs
        self.setObjectName("AnimationBinding")

        self.animation_escape_list = [
            self.languages[-7],
            self.languages[-6],
            self.languages[-5],
            self.languages[-4],
            self.languages[-3],
            self.languages[-2],
        ]
        self.special_animation_list = [
            self.languages[-1],
        ]
        self.motion_dict = live2d_custom.Live2DParameters(model_json_path).get_motions
        self.expression_lists = live2d_custom.Live2DParameters(model_json_path).get_expressions

        BodyLabel(self.languages[48], self).setGeometry(QRect(10, 52, 100, 30))
        self.select_actions = ComboBox(self)
        self.select_actions.setCurrentIndex(0)
        self.select_actions.addItems(self.animation_escape_list)
        self.select_actions.currentTextChanged.connect(self.change_action)
        self.select_actions.setGeometry(QRect(100, 52, 200, 30))

        self.select_special_actions = ComboBox(self)
        self.select_special_actions.addItems(self.special_animation_list)
        self.select_special_actions.setText("")
        self.select_special_actions.setCurrentIndex(-1)
        self.select_special_actions.currentTextChanged.connect(self.change_special_action)
        self.select_special_actions.setGeometry(QRect(310, 52, 200, 30))

        BodyLabel("min(X)", self).setGeometry(QRect(10, 92, 100, 30))
        self.input_min_y = LineEdit(self)
        self.input_min_y.setGeometry(QRect(10, 122, 80, 30))
        BodyLabel("min(Y)", self).setGeometry(QRect(270, 92, 100, 30))
        self.input_min_x = LineEdit(self)
        self.input_min_x.setGeometry(QRect(270, 122, 80, 30))
        BodyLabel("max(X)", self).setGeometry(QRect(140, 92, 100, 30))
        self.input_max_y = LineEdit(self)
        self.input_max_y.setGeometry(QRect(140, 122, 80, 30))
        BodyLabel("max(Y)", self).setGeometry(QRect(400, 92, 100, 30))
        self.input_max_x = LineEdit(self)
        self.input_max_x.setGeometry(QRect(400, 122, 80, 30))
        for index, attr in enumerate([self.input_min_x, self.input_min_y, self.input_max_x, self.input_max_y]):
            attr.setText(str(configure['record']['position'][index]))

        self.click_auto_record = PrimaryPushButton(self.languages[153], self)
        self.click_auto_record.clicked.connect(self.start_record)
        self.click_auto_record.setGeometry(QRect(500, 112, 100, 30))

        BodyLabel(self.languages[41], self).setGeometry(QRect(10, 172, 100, 30))
        self.select_motion_name = ComboBox(self)
        self.select_motion_name.addItems(
            self.motion_dict[list(self.motion_dict.keys())[0]])
        self.select_motion_name.setGeometry(QRect(260, 172, 300, 30))
        self.select_motion_name.currentTextChanged.connect(self.change_motion_name)
        self.select_motion_name.setToolTip(self.languages[91])
        BodyLabel(self.languages[42], self).setGeometry(QRect(260, 202, 100, 30))
        self.select_motion_group = ComboBox(self)
        self.select_motion_group.addItems(list(self.motion_dict.keys()))
        self.select_motion_group.setCurrentIndex(0)
        self.select_motion_group.currentTextChanged.connect(self.change_motion_group)
        self.select_motion_group.setGeometry(QRect(100, 172, 150, 30))
        self.select_motion_group.setToolTip(self.languages[90])
        BodyLabel(self.languages[43], self).setGeometry(QRect(100, 202, 100, 30))

        BodyLabel(self.languages[45], self).setGeometry(QRect(10, 232, 100, 30))
        self.select_expression_name = ComboBox(self)
        self.select_expression_name.addItems(self.expression_lists)
        self.select_expression_name.setCurrentText("")
        self.select_expression_name.setText("")
        self.select_expression_name.setGeometry(QRect(100, 232, 300, 30))
        self.select_expression_name.currentTextChanged.connect(self.change_expression_name)
        self.select_expression_name.setCurrentIndex(-1)

        BodyLabel(self.languages[136], self).setGeometry(QRect(10, 272, 100, 30))
        self.input_import_audio = LineEdit(self)
        self.input_import_audio.setGeometry(QRect(100, 272, 200, 30))
        self.select_save_folder = ComboBox(self)
        self.select_save_folder.addItems(list(template['voice'].keys()))
        self.select_save_folder.setGeometry(QRect(300, 272, 100, 30))
        self.click_choose_audio = PrimaryPushButton(self.languages[116], self)
        self.click_choose_audio.clicked.connect(
            lambda: function.select_file(self, self.languages[52], self.input_import_audio))
        self.click_choose_audio.setGeometry(QRect(400, 272, 100, 30))
        self.click_import_audio = PrimaryPushButton(self.languages[44], self)
        self.click_import_audio.clicked.connect(self.import_audio)
        self.click_import_audio.setGeometry(QRect(510, 272, 100, 30))

        BodyLabel(self.languages[46], self).setGeometry(QRect(10, 312, 100, 30))
        self.select_audio = ComboBox(self)
        self.select_audio.addItems(list(template['voice'].keys()))
        self.select_audio.setGeometry(QRect(100, 312, 300, 30))
        self.select_audio.currentTextChanged.connect(self.change_play_audio)

        BodyLabel(self.languages[47], self).setGeometry(QRect(10, 342, 100, 30))
        self.select_audio_play = ComboBox(self)
        vl = os.listdir(f"./resources/voice/{self.configure['default']}/{self.select_audio.currentText()}")
        vl.append("random")
        self.select_audio_play.addItems(vl)
        self.select_audio_play.setGeometry(QRect(100, 342, 300, 30))

        self.click_export_animation_configure = PrimaryPushButton(self.languages[245], self)
        self.click_export_animation_configure.clicked.connect(self.export_animation_configure)
        self.click_export_animation_configure.setGeometry(QRect(0, 412, 620, 30))
        self.click_import_animation_configure = PrimaryPushButton(self.languages[246], self)
        self.click_import_animation_configure.clicked.connect(self.import_animation_configure)
        self.click_import_animation_configure.setGeometry(QRect(0, 452, 620, 30))

        self.click_save_animation = PrimaryPushButton(self.languages[44], self)
        self.click_save_animation.clicked.connect(self.save_animation)
        self.click_save_animation.setGeometry(QRect(0, 492, 620, 30))

    def export_animation_configure(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
            winreg.CloseKey(key)
            desktop_path = os.path.expandvars(desktop_path)
        except:
            desktop_path = os.getcwd()
        config_animation = self.configure['model'][self.configure['default']]
        filename, _ = QFileDialog.getSaveFileName(self, "文件保存", os.path.join(desktop_path, "aniconf.json"),
                                                                "Json Config File (*.json)",
                                                                "Json Config File (*.json)"
                                                         )
        if not filename.strip():
            widgets.pop_error(self, "Error", self.languages[248])
            return

        with open(filename, "w", encoding="utf-8") as asf:
            asf.write(json.dumps(config_animation, indent=4, ensure_ascii=False))
            widgets.pop_success(self, "Success", self.languages[247])
            asf.close()

    def import_animation_configure(self):
        filename, _ = QFileDialog.getOpenFileName(self, "文件选择", os.getcwd(),
                                                                "Json Config File (*.json)",
                                                                "Json Config File (*.json)"
                                                         )
        if not filename.strip():
            widgets.pop_error(self, "Error", self.languages[248])
            return
        with open(filename, "r", encoding="utf-8") as asf:
            function.change_configure(json.load(asf), f"model.{self.configure['default']}", self.configure)
            asf.close()
        widgets.pop_success(self, "Success", self.languages[247])

    def import_audio(self):
        audio_basename = os.path.basename(self.input_import_audio.text())
        try:
            shutil.copyfile(self.input_import_audio.text(), f"./resources/voice/"
                                                            f"{self.configure['default']}/"
                                                            f"{self.select_save_folder.currentText()}/{audio_basename}")
            self.select_audio_play.clear()
            vl = os.listdir(f"./resources/voice/{self.configure['default']}/{self.select_audio.currentText()}")
            vl.append("random")
            self.select_audio_play.addItems(vl)

        except shutil.SameFileError:
            pass
        except FileNotFoundError:
            widgets.pop_error(self, "Error", self.languages[155])

    def save_animation(self):
        if self.select_actions.currentText().strip():
            key = "action"
            action = list(self.configure['model'][self.configure['default']]['action'].keys())[
                self.animation_escape_list.index(self.select_actions.currentText())]

            self.configure["model"][self.configure['default']][key][action]['position'] = [
                int(self.input_min_x.text()), int(self.input_max_x.text()),
                int(self.input_min_y.text()), int(self.input_max_y.text())]
        else:
            key = "special_action"
            action = list(self.configure['model'][self.configure['default']]['special_action'].keys())[
                self.special_animation_list.index(self.select_special_actions.currentText())]
        self.configure["model"][self.configure['default']][key][
            action]['motion'] = (f"{self.select_motion_group.currentText()}:"
                                 f"{self.select_motion_name.currentText()}:"
                                 f"{self.select_motion_name.currentIndex()}")
        self.configure["model"][self.configure['default']][key][action][
            'expression'] = self.select_expression_name.currentText()
        self.configure["model"][self.configure['default']][key][action][
            'play_type'] = self.select_audio_play.currentText()
        self.configure["model"][self.configure['default']][key][action]['play'] = self.select_audio.currentText()
        with open("./resources/configure.json", "w", encoding="utf-8") as sf:
            json.dump(self.configure, sf, indent=3, ensure_ascii=False)
            sf.close()

    def change_play_audio(self, text):
        self.select_audio_play.clear()
        vl = os.listdir(f"./resources/voice/{self.configure['default']}/{text}")
        vl.append("random")
        self.select_audio_play.addItems(vl)

    def change_special_action(self, text):
        # 设置另一个不可用
        self.select_actions.setText("")
        self.select_actions.setCurrentIndex(-1)
        self.click_auto_record.setEnabled(False)
        self.input_max_x.setEnabled(False)
        self.input_min_y.setEnabled(False)
        self.input_max_y.setEnabled(False)
        self.input_min_x.setEnabled(False)

    def change_action(self, text):
        # 设置另一个不可用
        self.select_special_actions.setText("")
        self.select_special_actions.setCurrentIndex(-1)
        self.click_auto_record.setEnabled(True)
        self.input_max_x.setEnabled(True)
        self.input_min_y.setEnabled(True)
        self.input_max_y.setEnabled(True)
        self.input_min_x.setEnabled(True)

        temp_config = self.configure['model'][self.configure['default']]['action'][
            list(self.configure['model'][self.configure['default']]['action'].keys())[
                self.animation_escape_list.index(text)]]
        self.input_min_x.setText(str(temp_config['position'][0]))
        self.input_max_x.setText(str(temp_config['position'][1]))
        self.input_min_y.setText(str(temp_config['position'][2]))
        self.input_max_y.setText(str(temp_config['position'][3]))

        self.select_motion_group.setCurrentText(temp_config['motion'].split(":")[0])
        self.select_motion_name.setCurrentText(temp_config['motion'].split(":")[1])

        self.select_expression_name.setCurrentText(temp_config['expression'])
        self.select_audio_play.setCurrentText(temp_config['play_type'])
        self.select_audio.setCurrentText(temp_config['play'])

    def change_expression_name(self, text):
        self.kwargs.get("desktop").pet_model.SetExpression(text)
        self.select_motion_name.setCurrentIndex(-1)
        self.select_motion_group.setCurrentIndex(-1)
        self.select_motion_name.setCurrentText("")
        self.select_motion_group.setCurrentText("")
        self.select_motion_name.setText("")
        self.select_motion_group.setText("")
        QTimer.singleShot(8000, lambda: self.kwargs.get("desktop").pet_model.ResetExpression())

    def change_motion_name(self, text):
        self.kwargs.get("desktop").pet_model.StartMotion(
            self.select_motion_group.currentText(),
            self.motion_dict[self.select_motion_group.currentText()].index(text),
            self.kwargs.get("live2d").MotionPriority.FORCE,
            onFinishMotionHandler=lambda: self.kwargs.get("desktop").finishedAnimationEvent())

    def change_motion_group(self, text):
        self.select_motion_name.clear()
        self.select_motion_name.addItems(self.motion_dict[text])
        self.kwargs.get("desktop").pet_model.StartMotion(
            text,
            self.motion_dict[text].index(self.select_motion_name.currentText()),
            self.kwargs.get("live2d").MotionPriority.FORCE)
        self.select_expression_name.setCurrentIndex(-1)
        self.select_expression_name.setCurrentText("")
        self.select_expression_name.setText("")

    def start_record(self):
        if widgets.pop_message(self, self.languages[49], self.languages[67], "OK👌"):
            function.change_configure(True, "record.enable_position", self.configure)
            self.kwargs.get("record")()

    def refresh_position(self, min_x, min_y, max_x, max_y):
        self.input_min_x.setText(str(min_x))
        self.input_max_x.setText(str(max_x))
        self.input_min_y.setText(str(min_y))
        self.input_max_y.setText(str(max_y))
