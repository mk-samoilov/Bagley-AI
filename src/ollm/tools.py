import os
import subprocess


# -------------------------
# FILE SYSTEM TOOLS
# -------------------------
def read_file(core, path: str):
    with open(path, "r") as f:
        return f.read()


def write_file(core, path: str, content: str):
    with open(path, "w") as f:
        f.write(content)
    return f"[ok] written to {path}"


def list_dir(core, path: str = "."):
    return os.listdir(path)


# -------------------------
# SHELL TOOL (dangerous but useful)
# -------------------------
def run_shell(core, cmd: str):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr
