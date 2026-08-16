class Operate:
    def __init__(self, config):
        self._config = config

    def GetContentMenu(self):
        return self._config['content_menu']
