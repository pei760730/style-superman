import datetime as dt
import io
import socket
import urllib.error

from scripts import repo_health as health


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_living_files_exclude_archives_reports_and_virtualenv(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    _write(tmp_path / "README.md", "live")
    _write(tmp_path / "CHANGELOG.md", "archive")
    _write(tmp_path / "reports" / "x.md", "report")
    _write(tmp_path / ".venv" / "x.md", "venv")

    assert [path.name for path in health.living_md_files()] == ["README.md"]


def test_scripts_documented_orphans_and_path_references(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    _write(tmp_path / "scripts" / "README.md", "documented.py and guide.md")
    _write(tmp_path / "scripts" / "documented.py", "")
    _write(tmp_path / "scripts" / "missing.py", "")
    _write(tmp_path / "docs" / "guide.md", "See scripts/gone.py")
    _write(tmp_path / "docs" / "orphan.md", "no references")
    _write(tmp_path / "README.md", "docs/guide.md")

    documented = health.check_scripts_documented()
    assert len(documented) == 1
    assert "missing.py" in documented[0].message

    orphans = health.check_orphans()
    assert any("docs/orphan.md" in finding.message for finding in orphans)
    assert not any("docs/guide.md" in finding.message for finding in orphans)

    paths = health.check_path_references()
    assert any("scripts/gone.py" in finding.message for finding in paths)


def test_workflow_and_decision_guards_find_only_scoped_live_violations(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    _write(tmp_path / ".github" / "workflows" / "ci.yml", "run: python scripts/gone.py\n")
    workflow = health.check_workflow_scripts()
    assert len(workflow) == 1
    assert "scripts/gone.py" in workflow[0].message

    _write(
        tmp_path / "data" / "decision_guards.yml",
        "guards:\n  - id: D1\n    decision: no-zombie\n    pattern: forbidden-token\n"
        "    scope: [docs]\n    exclude: [docs/excluded.md]\n    reason: retired\n",
    )
    _write(tmp_path / "docs" / "bad.md", "forbidden-token")
    _write(tmp_path / "docs" / "excluded.md", "forbidden-token")
    findings = health.check_decision_guards()
    assert len(findings) == 1
    assert "docs/bad.md:1" in findings[0].message


def test_weekly_freshness_handles_empty_recent_and_cross_year(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    (tmp_path / "reports" / "buy_shortlist").mkdir(parents=True)
    assert "尚無週挑" in health.check_weekly_picks_freshness(dt.date(2026, 1, 1))[0].message

    _write(tmp_path / "reports" / "buy_shortlist" / "2025-W52.md", "# week")
    stale = health.check_weekly_picks_freshness(dt.date(2026, 1, 12))[0]
    assert stale.level == "info"
    assert "落後 3 週" in stale.message

    _write(tmp_path / "reports" / "buy_shortlist" / "2026-W02.md", "# week")
    assert "落後 0 週內" in health.check_weekly_picks_freshness(dt.date(2026, 1, 5))[0].message


def test_monthly_freshness_respects_launch_date_grace_and_existing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    monthly_dir = tmp_path / "reports" / "monthly"
    monthly_dir.mkdir(parents=True)
    monkeypatch.setattr(
        health,
        "MONTHLY_REGION_SINCE",
        {"eu": dt.date(2026, 6, 1), "jp": dt.date(2026, 7, 1)},
    )
    assert health.check_monthly_freshness(dt.date(2026, 6, 2)) == []

    findings = health.check_monthly_freshness(dt.date(2026, 7, 4))
    assert len(findings) == 2
    assert all(finding.level == "warn" for finding in findings)

    _write(monthly_dir / "2026-07-jp.md", "# report")
    findings = health.check_monthly_freshness(dt.date(2026, 7, 4))
    assert any("已存在" in finding.message for finding in findings)


def test_lyst_staleness_handles_missing_invalid_current_and_overdue(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    ranking = tmp_path / "data" / "rankings" / "lyst-index.yml"

    assert health.check_lyst_staleness(dt.date(2026, 8, 18))[0].level == "error"
    _write(ranking, "snapshots:\n  - period: unknown\n")
    assert "沒有可解析" in health.check_lyst_staleness(dt.date(2026, 8, 18))[0].message

    _write(ranking, "snapshots:\n  - period: 2026-Q2\n")
    current = health.check_lyst_staleness(dt.date(2026, 8, 18))[0]
    assert current.level == "info"
    assert "寬限內" in current.message

    _write(ranking, "snapshots:\n  - period: 2025-Q4\n")
    overdue = health.check_lyst_staleness(dt.date(2026, 8, 18))[0]
    assert overdue.level == "warn"
    assert "已發布逾" in overdue.message


def test_output_contract_reports_missing_required_banned_and_stale_placeholders(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    _write(
        tmp_path / "reports" / "daily" / "2026-08-17.md",
        "# report\n可拍選題\n{{unfinished}}",
    )
    _write(
        tmp_path / "reports" / "monthly" / "2026-08-eu.md",
        "# report\n## 🛒 本月挑買方向",
    )

    findings = health.check_output_contract(dt.date(2026, 8, 18))

    assert len(findings) == 1
    assert "缺必有段落" in findings[0].message
    assert "可拍選題" in findings[0].message
    assert "骨架未填內容" in findings[0].message


def test_rss_coverage_uses_only_structurally_rssable_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    _write(
        tmp_path / "data" / "sources.yml",
        "sources:\n"
        "  - {type: media, rss: feed}\n"
        "  - {type: community}\n"
        "  - {type: ranking}\n",
    )
    finding = health.check_rss_coverage()[0]
    assert finding.level == "info"
    assert "1/2" in finding.message
    assert "另 1 個" in finding.message


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.body


def test_probe_rss_classifies_content_http_dns_and_transport(monkeypatch):
    feed = b"<rss><channel><item><title>x</title></item></channel></rss>"
    monkeypatch.setattr(health.urllib.request, "urlopen", lambda request, timeout: FakeResponse(feed))
    assert health._probe_rss("https://example.com") == ("ok", 200)

    monkeypatch.setattr(
        health.urllib.request,
        "urlopen",
        lambda request, timeout: FakeResponse(b"<rss><channel/></rss>"),
    )
    assert health._probe_rss("https://example.com") == ("empty", 200)

    for code, expected in ((429, "ratelimited"), (403, "blocked"), (404, "gone"), (500, "unreachable")):
        def http_error(request, timeout, code=code):
            raise urllib.error.HTTPError(request.full_url, code, "error", {}, io.BytesIO())

        monkeypatch.setattr(health.urllib.request, "urlopen", http_error)
        assert health._probe_rss("https://example.com") == (expected, code)

    dns = urllib.error.URLError(socket.gaierror("missing"))
    monkeypatch.setattr(health.urllib.request, "urlopen", lambda request, timeout: (_ for _ in ()).throw(dns))
    assert health._probe_rss("https://example.com") == ("nxdomain", 0)

    monkeypatch.setattr(health.urllib.request, "urlopen", lambda request, timeout: 1 / 0)
    assert health._probe_rss("https://example.com") == ("unreachable", 0)


def test_source_liveness_retries_non_live_and_preserves_classification(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    _write(
        tmp_path / "data" / "sources.yml",
        "sources:\n"
        "  - {id: ok, rss: ok}\n"
        "  - {id: gone, rss: gone}\n"
        "  - {id: blocked, rss: blocked}\n"
        "  - {id: limited, rss: limited}\n",
    )
    calls = []

    def probe(url):
        calls.append(url)
        return {
            "ok": ("ok", 200),
            "gone": ("gone", 404),
            "blocked": ("blocked", 403),
            "limited": ("ratelimited", 429),
        }[url]

    findings = health.check_source_liveness(probe=probe, retry_delay=0)

    assert calls.count("gone") == 2
    assert calls.count("blocked") == 2
    assert calls.count("limited") == 1
    assert "1 死源候補" in findings[0].message
    assert any("死源候補：gone" in finding.message for finding in findings)
    assert any("疑遭阻擋" in finding.message for finding in findings)
    assert any("限速（非死源）" in finding.message for finding in findings)


def test_analysis_contract_and_run_checks_aggregation(tmp_path, monkeypatch):
    monkeypatch.setattr(health, "ROOT", tmp_path)
    _write(tmp_path / "reports" / "analysis" / "bad.md", "no h1\nContent Hooks")
    _write(tmp_path / "reports" / "analysis" / "ignore.draft.md", "bad")
    findings = health.check_analysis_outputs()
    assert len(findings) == 1
    assert "缺 H1" in findings[0].message
    assert "Content Hooks" in findings[0].message

    marker = health.Finding("info", "marker")
    for name in (
        "check_scripts_documented",
        "check_orphans",
        "check_path_references",
        "check_workflow_scripts",
        "check_decision_guards",
        "check_analysis_outputs",
    ):
        monkeypatch.setattr(health, name, lambda marker=marker: [marker])
    assert len(health.run_checks(dt.date(2026, 8, 18), consistency_only=True)) == 6


def test_lyst_behind_count_is_signed_correctly_and_grace_boundary_is_derived(tmp_path, monkeypatch):
    """Lyst 季度數學的兩個零測試點：`behind` 的數值本身，以及發布寬限的邊界那一天。

    2026-08-29 突變測試顯示這兩處原本完全沒被蓋到——把 `behind` 正負反轉會印出
    「落後 -1 季」、當季 index 少一個 `+ 1` 會印「落後 0 季」，兩者都不會有任何測試變紅。
    既有 lyst 測試只斷言 level 與「寬限內 / 已發布逾」字串，從不看那個數字。
    """
    monkeypatch.setattr(health, "ROOT", tmp_path)
    ranking = tmp_path / "data" / "rankings" / "lyst-index.yml"

    # 2026-08 落在 Q3、手上最新是 Q2 → behind 必須是正的 1。
    _write(ranking, "snapshots:\n  - period: 2026-Q2\n")
    assert "落後 1 季" in health.check_lyst_staleness(dt.date(2026, 8, 29))[0].message

    # 寬限邊界：上一季（2026-Q2）季末 6/30，要「嚴格晚於」季末 + lag 才算新一季可 ingest。
    # 天數從常數推導、不寫死——調 LYST_PUBLISH_LAG_DAYS 是調參，不該讓測試變紅；
    # 但「邊界當天仍在寬限內、隔天才警」這條語意必須釘死（季末算法錯一天就會漂掉）。
    boundary = dt.date(2026, 6, 30) + dt.timedelta(days=health.LYST_PUBLISH_LAG_DAYS)
    _write(ranking, "snapshots:\n  - period: 2026-Q1\n")
    assert health.check_lyst_staleness(boundary)[0].level == "info"
    assert "落後 2 季" in health.check_lyst_staleness(boundary)[0].message
    assert health.check_lyst_staleness(boundary + dt.timedelta(days=1))[0].level == "warn"


def test_weekly_behind_uses_iso_week_arithmetic_not_approximate_division(tmp_path, monkeypatch):
    """週差必須是「ISO 週一日期相減 // 7」。

    6 週差是 `// 7` 與 `// 6` 的第一個分歧點（42 // 7 == 6、42 // 6 == 7）；既有測試最遠只到
    3 週，落在兩者結果相同的區間裡，把除數改掉不會有任何測試變紅。
    """
    monkeypatch.setattr(health, "ROOT", tmp_path)
    (tmp_path / "reports" / "buy_shortlist").mkdir(parents=True)
    _write(tmp_path / "reports" / "buy_shortlist" / "2026-W20.md", "# week")

    finding = health.check_weekly_picks_freshness(dt.date.fromisocalendar(2026, 26, 1))[0]
    assert "落後 6 週" in finding.message
