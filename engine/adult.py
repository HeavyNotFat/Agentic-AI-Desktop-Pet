import re

from . import basic


class AdultEngine(basic.BaseEngine):
    """成人内容加载引擎 Adult content loading engine"""
    def __init__(self, configure):
        self.configure = configure

    def voice(self) -> tuple:
        keywords = re.findall(r'\b[a-zA-Z]+\b', self.configure['model'][self.configure[
            'default']]['adult']['AdultDescribe'][str(self.configure['adult_level'])])
        keywords = ''.join(keywords)
        return keywords.lower(), self.configure['model'][self.configure['default']]['adult']['voice'][f"Voice{keywords}"]
