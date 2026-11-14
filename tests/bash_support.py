"""Locate the local Bash used by offline workflow regressions."""

import shutil
import sys
from pathlib import Path


def find_bash():
    if sys.platform == "win32":
        # PATH may contain the WSL launcher. Use Git for Windows instead, whose
        # git.exe can live in cmd/, bin/, or an architecture's bin/ directory.
        git = shutil.which("git")
        if git:
            directory = Path(git).resolve().parent
            candidates = [
                root / relative
                for root in (directory.parent, directory.parent.parent)
                for relative in ("bin/bash.exe", "usr/bin/bash.exe")
            ]
        else:
            candidates = []
    else:
        bash = shutil.which("bash")
        candidates = [Path(bash)] if bash else []
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise AssertionError(
        "Offline workflow regressions require Bash (Git for Windows on Windows)"
    )
