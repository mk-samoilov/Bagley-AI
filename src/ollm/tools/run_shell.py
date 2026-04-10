import shlex
import select
import subprocess

from src.ollm.classes import ToolResponse


DESCRIPTION = """
Runs a shell command and returns the output.

Usage example:
{
    "tool": "run_shell",
    "args": {
        "cmd": "ls -la"
    }
}
"""


def execute(core, cmd: str):
    parts = shlex.split(cmd)
    proc = subprocess.Popen(
        parts,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    combined: list[str] = []

    while proc.poll() is None:
        readable, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.1)
        for stream in readable:
            line = stream.readline().strip() # type: ignore
            if line:
                bucket = stdout_lines if stream == proc.stdout else stderr_lines
                bucket.append(line)
                combined.append(line)

    rest_out, rest_err = proc.communicate()

    for line in (rest_out or "").strip().splitlines():
        stdout_lines.append(line)
        combined.append(line)

    for line in (rest_err or "").strip().splitlines():
        stderr_lines.append(line)
        combined.append(line)

    return ToolResponse(
        tool_output={
            "output": "\n".join(combined),
            "returncode": proc.returncode
        },
        errors=""
    )
