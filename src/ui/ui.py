class MainUI:
    def __init__(self, core):
        self.core = core

    def render_frame(self):
        prompt = input("> ")
        if prompt in ("exit", "quit"):
            self.core.cleanup()

        for part in self.core.ai.handle_msg_stream(prompt):
            print(part, end="", flush=True)

        print()
