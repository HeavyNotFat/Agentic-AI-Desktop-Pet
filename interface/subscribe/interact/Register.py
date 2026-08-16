class _Register:
    def __init__(self, config):
        self.config = config

    def SetLargeLanguageModel(self, model: callable):
        self.config.register("llm", model)

    def SetConversationInteraction(self, interaction: callable):
        self.config.register("conversation", interaction)
