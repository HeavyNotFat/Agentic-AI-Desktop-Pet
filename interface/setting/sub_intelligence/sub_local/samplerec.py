from ...customize import function, widgets

from PyQt5.Qt import QRect, Qt
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import Slider, BodyLabel, ComboBox, ProgressBar, PrimaryToolButton, FluentIcon


class SampleRecognition(QWidget):
    def __init__(self, configure, languages, main_pet, parent=None, setting_parent=None):
        super().__init__(parent)
        self.configure = configure
        self.languages = languages
        self.main_pet = main_pet
        self.setting_parent = setting_parent
        self.setObjectName("SampleRecognition")

        BodyLabel(self.languages[216], self).setGeometry(QRect(10, 10, 100, 30))
        self.show_sampling = BodyLabel("50", self)
        self.show_sampling.setGeometry(QRect(500, 10, 70, 30))
        self.scale_sampling = Slider(Qt.Horizontal, self)
        self.scale_sampling.setRange(10, 200)
        self.scale_sampling.setValue(50)
        self.scale_sampling.valueChanged.connect(lambda: self.show_sampling.setText(str(self.scale_sampling.value())))
        self.scale_sampling.setGeometry(QRect(90, 15, 400, 30))

        BodyLabel(self.languages[217], self).setGeometry(QRect(10, 40, 100, 30))
        self.select_algorithm = ComboBox(self)
        self.select_algorithm.addItems([self.languages[156], self.languages[157],
                                        self.languages[158], self.languages[159]])
        self.select_algorithm.setCurrentIndex(1)
        self.select_algorithm.setGeometry(QRect(90, 45, 400, 30))

        self.progress = ProgressBar(self)
        self.progress.setRange(0, 200)
        self.progress.setGeometry(QRect(0, 80, 400, 30))
        self.show_progress = BodyLabel("0%", self)
        self.show_progress.setGeometry(QRect(0, 80, 200, 30))
        self.show_sampling_value = BodyLabel(f"{self.languages[218]}: {self.configure['settings']['rec']['silence_threshold']}", self)
        self.show_sampling_value.setGeometry(QRect(140, 80, 250, 30))

        self.click_sample = PrimaryToolButton(FluentIcon.SEND_FILL, self)
        self.click_sample.clicked.connect(self.start)
        self.click_sample.setGeometry(QRect(410, 80, 60, 30))

    def update_progress(self, current_progress, current_value):
        self.progress.setValue(current_progress)
        self.show_progress.setText(f"{round(current_progress / self.scale_sampling.value() * 100, 2)}%")
        self.show_sampling_value.setText(f"{self.languages[218]}: {current_value}")

    def start(self):
        function.change_configure(None, "settings.setting.silence_threshold", self.configure)
        if self.main_pet.speech_recognition is not None:
            if not widgets.pop_message(self.setting_parent, self.languages[155], self.languages[160]):
                return
            self.progress.setRange(0, self.scale_sampling.value())
            self.progress.setValue(0)
            if hasattr(self.main_pet.speech_recognition, "compute_sample"):
                self.main_pet.speech_recognition.compute_sample(
                    self.select_algorithm.currentIndex(), self.update_progress, self.scale_sampling.value())
