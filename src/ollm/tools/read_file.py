from src.ollm.classes import ToolResponse


DESCRIPTION = "Reads the contents of a file and returns it as text."

PARAMETERS = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Path to the file to read"
        }
    },
    "required": ["path"]
}


def execute(core, path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return ToolResponse(
            tool_output={"content": content},
            errors=""
        )

    except Exception as e:
        return ToolResponse(
            tool_output={},
            errors=str(e)
        )
