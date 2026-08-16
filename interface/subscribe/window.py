
class Window:
    def __init__(self, config):
        self.config = config

    def GetWindowPosition(self) -> tuple:
        """
        获得桌宠的窗口数据
        :return: Tuple --> (宽度，高度，x坐标，y坐标)
        """
        return (self.config['_Window'].width(), self.config['_Window'].height(),
                self.config['_Window'].x(), self.config['_Window'].y())

