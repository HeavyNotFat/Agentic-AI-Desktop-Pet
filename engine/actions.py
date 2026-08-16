import os

from . import basic


class ActionsEngine(basic.BaseEngine):
    def __init__(self, configure, languages, interface):
        super().__init__()
        self.configure = configure
        self.languages = languages
        self.interface = interface
        self.analyzed_action = []

    def analyze_action(self, mimes: str):
        print("ACCEPT ACTION MIME TEXT: ", mimes)
        self.analyzed_action = []
        for mime in mimes.splitlines():
            mime_data = mime.split(":///")
            if mime_data[0] == "file":
                if os.path.isfile(mime_data[1]):
                    self.analyzed_action.append(("drag_file", mime_data[1]))
                else:
                    self.analyzed_action.append(("drag_folder", mime_data[1]))
            else:
                self.analyzed_action.append(("drag_pure_text", mime_data[0]))
        print("ANALYZE ACTION: ", self.analyzed_action)

    def accept_action(self):
        ...
