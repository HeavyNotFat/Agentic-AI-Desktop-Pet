import live2d.v2 as live2d


class Live2D:
    def __init__(self, config):
        self.config = config

    def GetLive2D(self) -> live2d.LAppModel:
        """
        获得Live2D属性
        :return: live2d.LAppModel  -->  属性
        """
        return self.config['_Pet']
