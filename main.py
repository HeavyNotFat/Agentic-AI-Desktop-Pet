import random
import sys
import os
import time
import traceback

from PyQt5.QtWidgets import (
    QApplication, QSplashScreen, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt5.QtGui import (
    QPixmap, QFont, QPainter, QColor, QLinearGradient, QBrush
)


class SplashWindow(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(700, 413)
        pixmap.fill(Qt.transparent)
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)

        if not os.path.exists("./resources/static/startup.png"):
            image_pixmap = QPixmap(250, 412)
            image_pixmap.fill(QColor(200, 200, 200))
            painter = QPainter("./resources/static/startup.png")
            painter.setPen(QColor(100, 100, 100))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(image_pixmap.rect(), Qt.AlignCenter, "Image\nNot\nFound")
            painter.end()
        else:
            image_pixmap = QPixmap("./resources/static/startup.png")
            image_pixmap = image_pixmap.scaled(250, 412, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        image_label = QLabel(self)
        image_label.setPixmap(image_pixmap)
        image_label.setGeometry(700 - 250, 0, 250, 412)

        text_widget = QWidget(self)
        text_widget.setGeometry(0, 0, 700 - 250 - 20, 413)
        layout = QVBoxLayout(text_widget)
        layout.setContentsMargins(40, 60, 20, 60)
        layout.setSpacing(25)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(15)

        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.ico")
        logo_label.setPixmap(logo_pixmap)
        title_layout.addWidget(logo_label)

        app_name = QLabel("AI Desktop Pet")
        app_name.setFont(QFont("Arial", 20, QFont.Bold))
        app_name.setStyleSheet("color: #2C3E50;")
        title_layout.addWidget(app_name)

        title_layout.addStretch()
        layout.addLayout(title_layout)

        subtitle = QLabel(random.choice(['此应用程序免费，不要上当哦~', '陪伴 & 智能', '感谢您的使用！']))
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #7F8C8D;")
        layout.addWidget(subtitle)

        self.status_label = QLabel("正在启动应用程序...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #95A5A6;")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDC3C7;
                border-radius: 3px;
                background: #ECF0F1;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        copyright_label = QLabel("© 2024 - 2025 HeavyNotFat. All rights reserved.\nModel: <NekoPara猫娘乐园>")
        copyright_label.setFont(QFont("Arial", 9))
        copyright_label.setStyleSheet("color: #BDC3C7;")
        copyright_label.setAlignment(Qt.AlignRight)
        layout.addWidget(copyright_label)

        self.show()
        QTimer.singleShot(1, self.progress_updater)

    def progress_updater(self):
        self.update_progress(10, "正在加载资源...")
        time.sleep(0.2)
        self.update_progress(50, "正在初始化...")
        time.sleep(1)
        self.update_progress(100, "启动完成")

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(240, 245, 255))
        gradient.setColorAt(1, QColor(220, 230, 250))
        left_rect = self.rect()
        left_rect.setWidth(700 - 250)
        painter.fillRect(left_rect, QBrush(gradient))

        painter.setPen(QColor(200, 200, 200))
        painter.drawLine(700 - 250, 0, 700 - 250, self.height())

        super().paintEvent(event)

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        QApplication.processEvents()
        if value >= 100:
            QTimer.singleShot(500, self.hide)

    def finish(self, window):
        self.update_progress(100, "启动完成")
        QApplication.processEvents()

        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(600)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        fade_out.finished.connect(lambda: super(SplashWindow, self).finish(window))
        fade_out.start()


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.splash = None

    def create_splash_screen(self):
        self.splash = SplashWindow()

    def initialize_main_window(self):
        QTimer.singleShot(150, self._create_main_window)

    def _create_main_window(self):
        try:
            import core
        except:
            print(traceback.format_exc())
            if self.splash:
                self.splash.finish(None)

    def run(self):
        self.create_splash_screen()
        self.initialize_main_window()
        sys.exit(self.app.exec_())


def main():
    """主函数"""
    app = Application()
    app.run()


if __name__ == '__main__':
    main()