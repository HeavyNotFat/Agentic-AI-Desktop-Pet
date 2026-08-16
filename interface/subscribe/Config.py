class _Config:
    def __init__(self):
        self._config = {}

    def register(self, relative: str, value: str):
        if relative not in self._config.keys():
            self._config.update({relative: ""})
        if isinstance(self._config[relative], str):
            self._config[relative] = value

    def __getitem__(self, item):
        return self._config[item]
