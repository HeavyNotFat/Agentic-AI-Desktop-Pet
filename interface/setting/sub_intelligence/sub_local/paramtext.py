from ...customize import function, constants

from PyQt5.Qt import QRect, Qt
from PyQt5.QtWidgets import QWidget

from qfluentwidgets import BodyLabel, Slider


class TextParameter(QWidget):
    def __init__(self, configure, parent=None):
        super().__init__(parent)
        self.configure = configure
        self.setObjectName("TextParameter")

        # top_k
        BodyLabel("top_k", self).setGeometry(QRect(10, 0, 60, 35))
        self.show_top_k = BodyLabel(top_k := str(configure['settings']['text']['top_k']), self)
        self.top_k = Slider(Qt.Horizontal, self)
        self.top_k.setRange(1, 100)
        self.top_k.setGeometry(QRect(100, 10, 300, 35))
        self.top_k.setValue(int(configure['settings']['text']['top_k']))
        self.top_k.setToolTip(top_k)
        self.top_k.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.text.top_k", self.top_k, self.show_top_k))
        self.show_top_k.setGeometry(QRect(420, 0, 60, 35))

        # top_p
        BodyLabel("top_p", self).setGeometry(QRect(10, 30, 60, 35))
        self.show_top_p = BodyLabel(top_p := str(configure['settings']['text']['top_p']), self)
        self.top_p = Slider(Qt.Horizontal, self)
        self.top_p.setRange(1, constants.TOP_P_PRECISION)
        self.top_p.setGeometry(QRect(100, 40, 300, 35))
        self.top_p.setValue(int(configure['settings']['text']['top_p'] * constants.TOP_P_PRECISION))
        self.top_p.setToolTip(top_p)
        self.top_p.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.text.top_p", self.top_p, self.show_top_p, constants.TOP_P_PRECISION))
        self.show_top_p.setGeometry(QRect(420, 30, 60, 35))

        # temperature
        BodyLabel("temperature", self).setGeometry(QRect(10, 60, 80, 35))
        self.show_temperature = BodyLabel(temperature := str(configure['settings']['text']['temperature']), self)
        self.temperature = Slider(Qt.Horizontal, self)
        self.temperature.setRange(1, constants.TEMPERATURE_PRECISION)
        self.temperature.setGeometry(QRect(100, 70, 300, 35))
        self.temperature.setValue(int(configure['settings']['text']['temperature'] * constants.TEMPERATURE_PRECISION))
        self.temperature.setToolTip(temperature)
        self.temperature.valueChanged.connect(
            lambda value: self.value_changed(
                value, "settings.text.temperature",
                self.temperature, self.show_temperature, constants.TEMPERATURE_PRECISION))
        self.show_temperature.setGeometry(QRect(420, 60, 60, 35))

    def value_changed(self, value, relative, slider_widget, label_widget, precision=1):
        # 判断是否是整数
        if value / precision % 1 == 0:
            result = int(value / precision)
        else:
            result = float(value / precision)

        label_widget.setText(str(result))
        slider_widget.setToolTip(str(result))
        function.change_configure(result, relative, self.configure)
