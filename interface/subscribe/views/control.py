class Control:
    def __init__(self, config):
        self.config = config

    def HideConversationView(self):
        self.config['conversation'].hide()

    def ShowConversationView(self):
        self.config['conversation'].show()

    def MoveConversation(self, x: int, y: int):
        self.config['conversation'].move(x, y)

    def HideSettingView(self):
        self.config['setting'].hide()

    def ShowSettingView(self):
        self.config['setting'].show()

    def MoveSetting(self, x: int, y: int):
        self.config['setting'].move(x, y)

    def HideDesktop(self):
        self.config['desktop'].hide()

    def ShowDesktop(self):
        self.config['desktop'].show()

    def MoveDesktop(self, x: int, y: int):
        self.config['desktop'].move(x, y)
