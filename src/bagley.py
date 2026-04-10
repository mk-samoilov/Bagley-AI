from src.ollm.ai import OllamaSession
from src.ui.ui import MainUI


class ConsoleBagleyAI:
    def __init__(self):
        self.ai = OllamaSession()

        self.ui = MainUI(core=self)

        self.handling = True

    def loop(self):
        self.ui.render_frame()

    def startup(self):
        while self.handling:
            self.loop()

    def cleanup(self):
        self.handling = False
