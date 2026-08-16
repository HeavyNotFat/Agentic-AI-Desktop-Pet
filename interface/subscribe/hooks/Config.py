class Config:
    def __init__(self):
        self._config = {}

    def register(self, relative: str, value):
        if relative not in self._config:
            self._config.update({relative: callable})
        self._config[relative] = value

    def unregister(self, relative):
        self._config[relative] = ""

    def __getitem__(self, item):
        return self._config[item]
