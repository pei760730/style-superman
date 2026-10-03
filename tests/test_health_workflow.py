"""Offline probe -> real report -> actual workflow shell regressions."""

import contextlib
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts import repo_health as health


@pytest.fixture(autouse=True)
def _block_external_io(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("External I/O forbidden in workflow regression")

    monkeypatch.setattr(health.urllib.request, "urlopen", blocked)
    monkeypatch.setattr(health.socket.socket, "connect", blocked)
    monkeypatch.setattr(health.socket, "getaddrinfo", blocked)


def _steps():
    workflow = yaml.safe_load(
        (health.ROOT / ".github/workflows/health.yml").read_text(encoding="utf-8")
    )
    return workflow["jobs"]["patrol"]["steps"]


def _render(tmp_path, monkeypatch, statuses):
    """Run the real liveness aggregator and CLI renderer, with synthetic sources."""
    source_dir = tmp_path / "data"
    source_dir.mkdir(exist_ok=True)
    sources = [
        {"id": f"source-{i}", "rss": f"https://synthetic.invalid/{i}"}
        for i in range(len(statuses))
    ]
    (source_dir / "sources.yml").write_text(
        yaml.safe_dump({"sources": sources}), encoding="utf-8"
    )
    aggregate = health.check_source_liveness
    output = io.StringIO()
    with monkeypatch.context() as local:
        local.setattr(health, "ROOT", tmp_path)
        local.setattr(sys, "argv", ["repo_health.py", "--liveness"])
        local.setattr(
            health,
            "check_source_liveness",
            lambda: aggregate(
                probe=lambda url: statuses[int(url.rsplit("/", 1)[1])], retry_delay=0
            ),
        )
        with contextlib.redirect_stdout(output), pytest.raises(SystemExit) as result:
            health.main()
    return output.getvalue(), result.value.code


def _shell(
    tmp_path,
    script,
    *,
    report="",
    probe_exit=0,
    listed="999",
    list_exit=0,
    close_exit=0,
):
    bash = shutil.which("bash")
    if sys.platform == "win32":
        git = shutil.which("git")
        bash = str(Path(git).resolve().parent.parent / "bin/bash.exe") if git else None
    assert bash and Path(bash).is_file(), (
        "Actual workflow shell regression requires Bash"
    )
    if report is not None:
        (tmp_path / "health-liveness.txt").write_text(report, encoding="utf-8")
        (tmp_path / "probe-input.txt").write_text(report, encoding="utf-8")
    (tmp_path / "health-report.txt").write_text(
        "synthetic strict report\n", encoding="utf-8"
    )
    # Empty PATH and BASH_ENV prevent accidental gh/network execution. Only these
    # explicit local utilities and fake GitHub operations are available.
    stubs = r"""
grep() { /usr/bin/grep "$@"; }
cat() { /usr/bin/cat "$@"; }
tee() { /usr/bin/tee "$@"; }
date() { printf '2026-10-03T00:00Z\n'; }
python() { /usr/bin/cat probe-input.txt; return "$PROBE_EXIT"; }
gh() {
  case "$1 $2" in
    "issue list") printf '%s' "$LISTED"; return "$LIST_EXIT" ;;
    "issue close") printf 'FAKE_CLOSE:%s\n' "$3" >&2; return "$CLOSE_EXIT" ;;
    "issue comment") printf 'FAKE_COMMENT:%s\n' "$3" >&2 ;;
    "issue create") printf 'FAKE_CREATE\n' >&2 ;;
    "label create") printf 'FAKE_LABEL\n' >&2 ;;
    *) printf 'UNEXPECTED_GH\n' >&2; return 91 ;;
  esac
}
"""
    env = {
        "PATH": "",
        "BASH_ENV": "",
        "PROBE_EXIT": str(probe_exit),
        "LISTED": listed,
        "LIST_EXIT": str(list_exit),
        "CLOSE_EXIT": str(close_exit),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:/Windows"),
    }
    assert "${{" not in script
    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-e"],
        input=stubs + script,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        env=env,
        check=False,
    )
    assert "UNEXPECTED_GH" not in result.stderr
    return result


def _issue(tmp_path, *, health_outcome="success", liveness_outcome="success", **kwargs):
    script = next(
        s["run"] for s in _steps() if s["name"] == "File or update health issue"
    )
    script = script.replace("${{ steps.health.outcome }}", health_outcome)
    script = script.replace("${{ steps.liveness.outcome }}", liveness_outcome)
    return _shell(tmp_path, script, **kwargs)


@pytest.mark.parametrize(
    "statuses,dead",
    [
        ([("ok", 200)], False),
        ([("blocked", 403)], False),
        ([("empty", 200)], False),
        ([("unreachable", 0)], False),
        ([("ratelimited", 429)], False),
        ([("gone", 404)], True),
        ([("gone", 410)], True),
        ([("nxdomain", 0)], True),
        ([("ok", 200), ("blocked", 403), ("ratelimited", 429)], False),
        ([("ok", 200), ("gone", 404), ("blocked", 403)], True),
        ([], False),
    ],
)
def test_completed_reports_preserve_fail_soft_and_dead_sources(
    tmp_path, monkeypatch, statuses, dead
):
    report, exit_code = _render(tmp_path, monkeypatch, statuses)
    assert exit_code == 0  # Warnings remain fail-soft without --strict.
    assert "來源死活：" in report
    assert ("死源候補：" in report) == dead
    result = _issue(tmp_path, report=report)
    assert result.returncode == 0, result.stderr
    assert ("FAKE_CLOSE:999" in result.stderr) == (not dead)
    assert ("巡檢全綠、無死源。" in result.stdout) == (not dead)
    assert ("FAKE_COMMENT:999" in result.stderr) == dead
    if dead:
        body = (tmp_path / "issue-body.md").read_text(encoding="utf-8")
        assert report in body
        assert "先複核再處置" in body


@pytest.mark.parametrize(
    "outcome", ["success", "failure", "skipped", "cancelled", "", "unknown"]
)
def test_recovery_requires_liveness_success(tmp_path, monkeypatch, outcome):
    report, _ = _render(tmp_path, monkeypatch, [("ok", 200)])
    result = _issue(tmp_path, report=report, liveness_outcome=outcome)
    assert result.returncode == 0
    assert ("FAKE_CLOSE" in result.stderr) == (outcome == "success")
    assert ("巡檢全綠" in result.stdout) == (outcome == "success")


@pytest.mark.parametrize(
    "report",
    [
        None,
        "",
        "Repo Health · 2026-10-03\n",
        "malformed\n",
        "⚠️  缺 pyyaml，無法跑來源死活檢查\n",
        '{"warnings": [], "info": []}\n',
        "ℹ️  來源死活：1/1 個 RSS 實際收得到\n",
        "ℹ️  來源死活：unknown\n",
        "ℹ️  來源死活：1/1 個 RSS 實際收得到料 garbage\n",
        "⚠️  來源死活：0/1 個 RSS 實際收得到料，1 死源候補\n",
    ],
)
def test_recovery_requires_valid_no_dead_summary(tmp_path, report):
    result = _issue(tmp_path, report=report)
    assert result.returncode == 0
    assert "FAKE_" not in result.stderr
    assert "巡檢全綠" not in result.stdout


def test_worker_start_crash_cannot_recover(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/sources.yml").write_text(
        "sources:\n  - {id: fake, rss: 'https://synthetic.invalid/feed'}\n",
        encoding="utf-8",
    )
    output = io.StringIO()
    with monkeypatch.context() as local:
        local.setattr(health, "ROOT", tmp_path)
        local.setattr(sys, "argv", ["repo_health.py", "--liveness"])
        local.setattr(
            "threading.Thread.start",
            lambda self: (_ for _ in ()).throw(RuntimeError("worker-start")),
        )
        with (
            contextlib.redirect_stdout(output),
            pytest.raises(RuntimeError, match="worker-start"),
        ):
            health.main()
    assert output.getvalue() == ""
    probe = next(s for s in _steps() if s["name"].startswith("Probe source"))
    assert probe["id"] == "liveness"
    assert probe["continue-on-error"] is True
    pipeline = _shell(tmp_path, probe["run"], report=output.getvalue(), probe_exit=1)
    assert pipeline.returncode == 1, pipeline.stdout + pipeline.stderr
    result = _issue(tmp_path, report=output.getvalue(), liveness_outcome="failure")
    assert "FAKE_CLOSE" not in result.stderr
    assert "巡檢全綠" not in result.stdout


@pytest.mark.parametrize("exit_code", [0, 1, 124, 130, 143])
def test_probe_pipeline_preserves_failures_even_with_valid_report(
    tmp_path, monkeypatch, exit_code
):
    report, _ = _render(tmp_path, monkeypatch, [("ok", 200)])
    probe = next(s for s in _steps() if s["name"].startswith("Probe source"))
    result = _shell(tmp_path, probe["run"], report=report, probe_exit=exit_code)
    assert result.returncode == exit_code, result.stdout + result.stderr
    decision = _issue(
        tmp_path,
        report=report,
        liveness_outcome="success" if result.returncode == 0 else "failure",
    )
    assert ("FAKE_CLOSE" in decision.stderr) == (exit_code == 0)


def test_partial_worker_results_never_publish_recovery_evidence(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/sources.yml").write_text(
        "sources:\n  - {id: first, rss: first}\n  - {id: second, rss: second}\n",
        encoding="utf-8",
    )
    aggregate = health.check_source_liveness

    def partial(url):
        if url == "first":
            return "ok", 200
        raise RuntimeError("partial-worker")

    output = io.StringIO()
    with monkeypatch.context() as local:
        local.setattr(health, "ROOT", tmp_path)
        local.setattr(sys, "argv", ["repo_health.py", "--liveness"])
        local.setattr(
            health,
            "check_source_liveness",
            lambda: aggregate(probe=partial, retry_delay=0),
        )
        with (
            contextlib.redirect_stdout(output),
            pytest.raises(RuntimeError, match="partial-worker"),
        ):
            health.main()
    assert output.getvalue() == ""
    result = _issue(tmp_path, report=output.getvalue(), liveness_outcome="failure")
    assert "FAKE_" not in result.stderr


@pytest.mark.parametrize("outcome", ["failure", "skipped", "cancelled", "", "unknown"])
def test_strict_failure_and_incomplete_setup_preserve_pr244_guard(
    tmp_path, monkeypatch, outcome
):
    report, _ = _render(tmp_path, monkeypatch, [("ok", 200)])
    result = _issue(tmp_path, report=report, health_outcome=outcome)
    assert result.returncode == 0
    assert "FAKE_CLOSE" not in result.stderr
    assert ("FAKE_COMMENT:999" in result.stderr) == (outcome == "failure")


def test_dead_evidence_and_strict_failure_keep_existing_create_path(
    tmp_path, monkeypatch
):
    report, _ = _render(tmp_path, monkeypatch, [("gone", 404)])
    result = _issue(tmp_path, report=report, liveness_outcome="failure", listed="")
    assert result.returncode == 0
    assert "FAKE_CREATE" in result.stderr
    assert "FAKE_CLOSE" not in result.stderr
    result = _issue(
        tmp_path,
        report="",
        health_outcome="failure",
        liveness_outcome="failure",
        listed="",
    )
    assert result.returncode == 0
    assert "FAKE_CREATE" in result.stderr


def test_issue_list_error_and_stale_issue_events_are_unchanged(tmp_path, monkeypatch):
    report, _ = _render(tmp_path, monkeypatch, [("ok", 200)])
    # API failure without stdout is swallowed, so recovery does not close.
    result = _issue(tmp_path, report=report, listed="", list_exit=1)
    assert result.returncode == 0
    assert "FAKE_" not in result.stderr
    # A stale list can race with closure elsewhere; close failure aborts, no retry.
    result = _issue(tmp_path, report=report, close_exit=1)
    assert result.returncode == 1
    assert result.stderr.count("FAKE_CLOSE:999") == 1
    # Existing list-error behavior on the fault path can still create a duplicate.
    result = _issue(
        tmp_path, report=report, health_outcome="failure", listed="", list_exit=1
    )
    assert result.returncode == 0
    assert "FAKE_CREATE" in result.stderr
