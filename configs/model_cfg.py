import os


MODEL_NAME: str = "qwen3.5:9b" # mistral:7b qwen3.5:9b glm-4.7-flash:latest

TEMPERATURE: float = 0.3
TOP_PROBABILITY: float = 0.8

CONTEXT_CHUNKS: int = 8192

SYSTEM_PROMPT_FILE: str = "configs/system-prompt.txt"

WORK_DIR: str = os.environ.get("BAGLEY_WORK_DIR", os.getcwd())
