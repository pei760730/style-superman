"""Shell discovery must work from both PowerShell and Git Bash."""

import bash_support
import pytest


@pytest.mark.parametrize(
    "git_relative",
    [
        "cmd/git.exe",
        "bin/git.exe",
        "mingw64/bin/git.exe",
        "mingw32/bin/git.exe",
        "ucrt64/bin/git.exe",
        "usr/bin/git.exe",
    ],
)
@pytest.mark.parametrize("bash_relative", ["bin/bash.exe", "usr/bin/bash.exe"])
def test_windows_git_layouts_ignore_wsl_launcher(
    tmp_path, monkeypatch, git_relative, bash_relative
):
    root = tmp_path / "Git With Spaces"
    git = root / git_relative
    bash = root / bash_relative
    wsl = tmp_path / "Windows/System32/bash.exe"
    for path in (git, bash, wsl):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    monkeypatch.setattr(bash_support.sys, "platform", "win32")
    monkeypatch.setattr(
        bash_support.shutil, "which", lambda name: str(git if name == "git" else wsl)
    )

    assert bash_support.find_bash() == str(bash)


@pytest.mark.parametrize("git_present", [False, True])
def test_windows_without_git_bash_fails_instead_of_using_wsl(
    tmp_path, monkeypatch, git_present
):
    git = tmp_path / "Git/cmd/git.exe"
    wsl = tmp_path / "Windows/System32/bash.exe"
    for path in (git, wsl):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    monkeypatch.setattr(bash_support.sys, "platform", "win32")
    monkeypatch.setattr(
        bash_support.shutil,
        "which",
        lambda name: (str(git) if git_present else None) if name == "git" else str(wsl),
    )

    with pytest.raises(AssertionError, match="Git for Windows"):
        bash_support.find_bash()


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_non_windows_uses_path_bash(tmp_path, monkeypatch, platform):
    bash = tmp_path / "bash"
    bash.touch()
    monkeypatch.setattr(bash_support.sys, "platform", platform)
    monkeypatch.setattr(bash_support.shutil, "which", lambda name: str(bash))

    assert bash_support.find_bash() == str(bash)


@pytest.mark.parametrize("bash", [None, "missing-bash"])
def test_non_windows_missing_bash_fails(monkeypatch, bash):
    monkeypatch.setattr(bash_support.sys, "platform", "linux")
    monkeypatch.setattr(bash_support.shutil, "which", lambda name: bash)

    with pytest.raises(AssertionError, match="require Bash"):
        bash_support.find_bash()
