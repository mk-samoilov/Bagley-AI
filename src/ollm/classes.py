from dataclasses import dataclass, asdict
import json


@dataclass
class ToolResponse:
    tool_output: dict
    errors: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
