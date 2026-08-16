class _Config:
    def __init__(self):
        self._config = {}

    def register(self, relative: str, value: callable):
        self._config[relative] = value

    def __getitem__(self, item):
        return self._config[item]
