class Model:
    def __init__(self, config):
        self.config = config

    def GetVoiceModel(self) -> str:
        """
        获得语音模型名字
        :return: String  -->  语音模型
        """
        return self.config['voice_model']
    