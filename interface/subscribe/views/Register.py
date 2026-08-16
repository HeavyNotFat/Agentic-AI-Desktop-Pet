class Register:
    def __init__(self, config):
        self.config = config

    def register(self, relative, master):
        self.config.register(relative, master)
