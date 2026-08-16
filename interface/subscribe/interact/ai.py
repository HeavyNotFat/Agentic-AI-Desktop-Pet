class LargeLanguageModel:
    def __init__(self, config):
        self.config = config

    def HaveOnceConversation(self, prompt: str) -> None:
        """
        通过文本描述对大语言模型进行一次对话
        :param prompt:                String   -->   用户输入的文本
        :return:                      String   -->   大语言模型的返回
        """
        return self.config['llm'](prompt)
