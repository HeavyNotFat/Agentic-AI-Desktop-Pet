class ShowOnBoard:
    def __init__(self, config):
        self.config = config

    def ShowText(self, texts: str, duration: int = 3000) -> None:
        """
        通过文本描述对大语言模型进行一次对话
        :param texts:                String   -->   需要展示的文本~
        :param duration:             Int      -->   展示时间
        """
        self.config['conversation'].show()
        self.config['conversation'].input_answer.setVisible(True)
        self.config['conversation'].click_pop_answer.setVisible(True)
        self.config['conversation'].input_answer.setText(str(texts))
        self.config['conversation'].duration_disappear(duration)
