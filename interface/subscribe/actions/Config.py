class Config:
    def __init__(self):
        self._config = {}

    def register(self, relative: str, value: str):
        if relative not in self._config.keys():
            self._config.update({relative: []})
        self._config[relative].append(value)

    def unregister(self, relative: str):
        try:
            self._config[relative].clear()
        except KeyError:
            pass

    def __getitem__(self, item):
        try:
            return self._config[item]
        except KeyError:
            return []
