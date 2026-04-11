import os

from src.ollm.classes import ToolResponse

from configs.model_cfg import WORK_DIR


DESCRIPTION = "Writes text content to a file. Creates the file if it does not exist, overwrites if it does."

PARAMETERS = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Path to the file to write"
        },
        "content": {
            "type": "string",
            "description": "Text content to write into the file"
        }
    },
    "required": ["path", "content"]
}


def execute(core, path: str, content: str):
    try:
        full_path = os.path.join(WORK_DIR, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return ToolResponse(
            tool_output={"written_bytes": len(content.encode("utf-8"))},
            errors=""
        )

    except Exception as e:
        return ToolResponse(
            tool_output={},
            errors=str(e)
        )
