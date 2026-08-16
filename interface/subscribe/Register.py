class Register:
    def __init__(self, config):
        self.config = config

    def SetCharacter(self, character):
        self.config.register("character", character)

    def SetVoiceModel(self, voice_model):
        self.config.register("voice_model", voice_model)

    def SetName(self, name):
        self.config.register("name", name)


class AttributeRegister:
    def __init__(self, config):
        self.config = config

    def SetWindow(self, window):
        self.config.register("_Window", window)

    def SetPet(self, pet: callable):
        self.config.register("_Pet", pet)
        