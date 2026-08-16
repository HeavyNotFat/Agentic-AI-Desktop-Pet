class _Config:
    def __init__(self):
        self._config = {
            "content_menu": []
        }

    def register(self, relative: str, value):
        if relative not in self._config.keys():
            self._config.update({relative: ""})
        if isinstance(self._config[relative], str):
            self._config[relative] = value
        elif isinstance(self._config[relative], list):
            self._config[relative].append(value)
        else:
            self._config[relative] = value

    def unregister(self, relative, value):
        if relative in self._config.keys():
            if isinstance(self._config[relative], str):
                self._config[relative] = ""
            elif isinstance(self._config[relative], list):
                self._config[relative].remove(value)

    def __getitem__(self, item):
        return self._config[item]
