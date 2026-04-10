from ollama import chat

import json
import re
import importlib
import pkgutil

from configs.model_cfg import (
    MODEL_NAME,
    SYSTEM_PROMPT_FILE,
    TEMPERATURE,
    CONTEXT_CHUNKS,
    TOP_PROBABILITY
)

import src.ollm.tools as tools_pkg

from src.ollm.classes import ToolResponse


class OllamaSession:
    def __init__(self, core=None):
        self.core = core
        self.model = MODEL_NAME

        self.tools = self._load_tools()

        self.messages = [
            {
                "role": "system",
                "content": self.make_sys_prompt()
            }
        ]

    def make_sys_prompt(self):
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt = f.read()

        return prompt.replace(
            "%ACCESSIBLE_TOOLS%",
            self._build_tools_prompt()
        )
    

    def _build_tools_prompt(self):
        blocks = []

        for tool_name, tool_data in self.tools.items():
            description = tool_data["description"].strip()

            block = (
                f"# {tool_name}\n"
                f"{'-' * (len(tool_name) + 2)}\n"
                f"{description}"
            )

            blocks.append(block)

        return "\n\n".join(blocks)

    @staticmethod
    def _load_tools():
        registry = {}

        for _, module_name, is_pkg in pkgutil.iter_modules(
            tools_pkg.__path__
        ):
            if is_pkg:
                continue

            module = importlib.import_module(
                f"{tools_pkg.__name__}.{module_name}"
            )

            if hasattr(module, "execute") and callable(module.execute):
                registry[module_name] = {
                    "execute": module.execute,
                    "description": getattr(
                        module,
                        "DESCRIPTION",
                        f"{module_name}\nNo description available."
                    )
                }

        return registry

    @staticmethod
    def _extract_json(text: str):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            return None

        try:
            return json.loads(match.group(0))

        except json.JSONDecodeError:
            return None

    def run_tool(self, tool_name, args):
        if tool_name not in self.tools:
            return ToolResponse(
                tool_output={},
                errors=f"Tool not found: {tool_name}"
            )

        fn = self.tools[tool_name]["execute"]

        try:
            return fn(self.core, **args)

        except Exception as e:
            return ToolResponse(
                tool_output={},
                errors=f"Tool execution failed: {str(e)}"
            )

    def handle_msg_stream(self, user_prompt: str):
        self.messages.append({
            "role": "user",
            "content": user_prompt
        })

        yield from self._process_response()


    def _process_response(self):
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

            response_data = self._extract_json(full_response)

            if response_data and "tool" in response_data:
                tool_name = response_data["tool"]
                args = response_data.get("args", {})

                result = self.run_tool(
                    tool_name=tool_name,
                    args=args
                ).to_json()

                self.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

                self.messages.append({
                    "role": "tool",
                    "content": result
                })

                yield from self._process_response()

                return

            self.messages.append({
                "role": "assistant",
                "content": full_response
            })
