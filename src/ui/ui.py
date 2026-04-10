class ChatUI:
    def __init__(self, core):
        self.core = core

        self.answer_stream = None

        self._generating_answer = False
        self._waiting_input = True
        self._running = True

    @property
    def generating_answer(self):
        return self._generating_answer

    def stop(self):
        self._running = False
        self.core.cleanup()

    def submit_prompt(self, prompt: str):
        if prompt == "":
            return

        if prompt in ("/exit", "/quit", "/q"):
            self.stop()
            return

        self._generating_answer = True
        self._waiting_input = False

        self.answer_stream = self.core.ai.handle_msg_stream(prompt)

    def take_input(self):
        try:
            prompt = input(f"{self.core.ai.model} > ").strip()
            self.submit_prompt(prompt)

        except KeyboardInterrupt:
            print("\n\nExiting...\n")
            self.stop()

    def print_answer(self):
        try:
            if self.answer_stream:
                part = next(self.answer_stream)
                print(part, end="", flush=True)

        except StopIteration:
            print()

            self._generating_answer = False
            self._waiting_input = True
            self.answer_stream = None

        except KeyboardInterrupt:
            print("\n\nGeneration corrupted.\n")

            self._generating_answer = False
            self._waiting_input = True
            self.answer_stream = None


class MainUI:
    def __init__(self, core):
        self.core = core

        self.chat = ChatUI(core=self.core)

    def render_frame(self):
        if not self.chat._running:
            return False

        try:
            if self.chat._waiting_input:
                self.chat.take_input()

            if self.chat.generating_answer and self.chat.answer_stream:
                self.chat.print_answer()

        except KeyboardInterrupt:
            print("\n")

            self.chat.stop()
            return False

        return True
