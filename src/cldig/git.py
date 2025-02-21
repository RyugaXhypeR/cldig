import os
import pathlib
import subprocess


def git_command(
    subcommand: str, *args: str, cwd: pathlib.Path | str | None = None
) -> subprocess.CompletedProcess[bytes]:
    if cwd is None:
        cwd = os.getcwd()

    command = "git", subcommand, *args

    return subprocess.run(command, cwd=cwd, check=True, capture_output=True)
