from ollama import chat

import importlib
import pkgutil
from typing import Any

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

        self.messages: list[Any] = [
            {
                "role": "system",
                "content": self._load_sys_prompt()
            }
        ]

    def _load_sys_prompt(self):
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _load_tools():
        registry = {}

        for _, module_name, is_pkg in pkgutil.iter_modules(tools_pkg.__path__):
            if is_pkg:
                continue

            module = importlib.import_module(f"{tools_pkg.__name__}.{module_name}")

            if hasattr(module, "execute") and callable(module.execute):
                registry[module_name] = {
                    "execute": module.execute,
                    "schema": {
                        "type": "function",
                        "function": {
                            "name": module_name,
                            "description": getattr(module, "DESCRIPTION", module_name),
                            "parameters": getattr(module, "PARAMETERS", {
                                "type": "object",
                                "properties": {}
                            })
                        }
                    }
                }

        return registry

    def _tools_list(self):
        return [data["schema"] for data in self.tools.values()]

    def run_tool(self, tool_name, args):
        if tool_name not in self.tools:
            return ToolResponse(
                tool_output={},
                errors=f"Tool not found: {tool_name}"
            )

        try:
            return self.tools[tool_name]["execute"](self.core, **args)

        except Exception as e:
            return ToolResponse(
                tool_output={},
                errors=f"Tool execution failed: {str(e)}"
            )

    def handle_msg_stream(self, user_prompt: str):
        self.messages.append({"role": "user", "content": user_prompt})
        yield from self._process_response()

    def _process_response(self):
        full_response = ""
        tool_calls = []

        for chunk in chat(
            model=self.model,
            messages=self.messages,
            stream=True,
            tools=self._tools_list(),
            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_PROBABILITY,
                "num_ctx": CONTEXT_CHUNKS
            }
        ):
            part = chunk.message.content or ""
            if part:
                full_response += part
                yield part

            if chunk.message.tool_calls:
                tool_calls = chunk.message.tool_calls

        if tool_calls:
            self.messages.append({
                "role": "assistant",
                "content": full_response,
                "tool_calls": tool_calls
            })

            for tool_call in tool_calls:
                name = tool_call.function.name
                args = tool_call.function.arguments

                props = "\n".join(f'  "{k}": "{v}"' for k, v in args.items())
                yield f"\nUsed tool '{name}':\n{props}\n\n"

                result = self.run_tool(name, args)

                self.messages.append({
                    "role": "tool",
                    "content": result.to_json()
                })

            yield from self._process_response()

        else:
            self.messages.append({
                "role": "assistant",
                "content": full_response
            })
