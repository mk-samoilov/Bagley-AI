from ollama import chat

from configs.model_cfg import (
    MODEL_NAME,
    SYSTEM_PROMPT_FILE,
    TEMPERATURE,
    CONTEXT_CHUNKS,
    TOP_PROBABILITY
)


class OllamaSession:
    def __init__(self):
        self.model = MODEL_NAME

        self.messages = [
            {
                "role": "system",
                "content": self.get_sys_prompt()
            }
        ]

    @staticmethod
    def get_sys_prompt():
        with open(file=SYSTEM_PROMPT_FILE, mode="r") as file:
            return file.read()

    def handle_msg_stream(self, user_prompt: str):
        self.messages.append({
            "role": "user",
            "content": user_prompt
        })

        full_response = ""

        for chunk in chat(
            model=self.model,
            messages=self.messages,
            stream=True,
            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_PROBABILITY,
                "num_ctx": CONTEXT_CHUNKS
            }
        ):
            chunk_msg = chunk["message"]["content"]
            full_response += chunk_msg

            yield chunk_msg

        self.messages.append({
            "role": "assistant",
            "content": full_response
        })
