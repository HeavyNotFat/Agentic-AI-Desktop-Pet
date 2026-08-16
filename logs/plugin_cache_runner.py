import requests

from PyQt5.Qt import QThread, pyqtSignal


class CheckHands(QThread):
    detect = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        response = requests.get("http://127.0.0.1:5000/check_hands")
        self.detect.emit(response.json())


class Processor:
    @staticmethod
    def detect_result(result):
        print(result)


Processor = Processor()

# 启动单个线程
CheckHands = CheckHands()
CheckHands.detect.connect(Processor.detect_result)
CheckHands.start()
