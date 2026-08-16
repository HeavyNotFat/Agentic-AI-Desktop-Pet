class Character:
    def __init__(self, config):
        self.config = config
    
    def GetCharacter(self) -> str:
        """
        获得角色的模型名字
        :return: String -->  名字
        """
        return self.config['character']

    def GetName(self) -> str:
        """
        获得角色的别名
        :return: String -->  别名
        """
        return self.config['name']
