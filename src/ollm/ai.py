from ollama import chat

import json
import re
import inspect

from configs.model_cfg import (
    MODEL_NAME,
    SYSTEM_PROMPT_FILE,
    TEMPERATURE,
    CONTEXT_CHUNKS,
    TOP_PROBABILITY
)

import src.ollm.tools as tools


class OllamaSession:
    def __init__(self, core=None):
        self.core = core
        self.model = MODEL_NAME

        self.tools = self._load_tools()

        self.messages = [
            {
                "role": "system",
                "content": self.get_sys_prompt()
            }
        ]

    # -------------------------
    # SYSTEM PROMPT
    # -------------------------
    @staticmethod
    def get_sys_prompt():
        with open(SYSTEM_PROMPT_FILE, "r") as f:
            return f.read()

    # -------------------------
    # TOOL REGISTRY
    # -------------------------
    def _load_tools(self):
        registry = {}

        for name in dir(tools):
            fn = getattr(tools, name)

            if inspect.isfunction(fn):
                registry[name] = fn

        return registry

    # -------------------------
    # CLEAN JSON (ВАЖНО ДЛЯ 7B)
    # -------------------------
    def _extract_json(self, text: str):
        # убираем markdown
        text = text.replace("```json", "")
        text = text.replace("```", "")

        # ищем JSON объект
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    # -------------------------
    # TOOL RUNNER
    # -------------------------
    def _run_tool(self, tool_name, args):
        if tool_name not in self.tools:
            return f"[error] tool not allowed: {tool_name}"

        fn = self.tools[tool_name]

        try:
            return fn(self.core, **args)
        except Exception as e:
            return f"[tool error] {str(e)}"

    # -------------------------
    # STREAM MAIN
    # -------------------------
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
            part = chunk["message"]["content"]
            full_response += part
            yield part

        # -------------------------
        # TOOL CHECK
        # -------------------------
        data = self._extract_json(full_response)

        if data and "tool" in data:
            tool_name = data["tool"]
            args = data.get("args", {})

            result = self._run_tool(tool_name, args)

            self.messages.append({
                "role": "assistant",
                "content": full_response
            })

            self.messages.append({
                "role": "tool",
                "content": str(result)
            })

            # второй проход (ответ с результатом tool)
            yield from self.handle_msg_stream(
                f"Tool result: {result}\nContinue answer naturally."
            )
            return

        # -------------------------
        # NORMAL FINISH
        # -------------------------
        self.messages.append({
            "role": "assistant",
            "content": full_response
        })
