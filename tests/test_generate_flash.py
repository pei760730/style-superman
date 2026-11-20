import pytest

from scripts import collect_raw_signals as collector
from scripts import generate_flash as flash


def _signal(**overrides):
    signal = {
        "source_id": "hypebeast",
        "region": "global",
        "published": "2026-08-18",
        "title": "Brand launches a new jacket",
        "url": "https://example.com/news/jacket",
        "summary": "Price is $200 and release date is Friday.",
    }
    signal.update(overrides)
    return signal


def test_slug_clip_and_recent_window_normalize_input():
    assert flash._slug("https://example.com/A-Story/?utm=x#top") == "a-story"
    assert flash._clip("  A   B submitted by bot [link] ") == "A B"
    assert flash._clip("abcdef", limit=3) == "abc…"
    assert flash._recent_window("2026-08-18", 2) == {"2026-08-18", "2026-08-17"}
    assert flash._recent_window("not-a-date", 2) == {"not-a-date"}


def test_extract_filters_by_semantics_and_deduplicates_within_region():
    signals = [
        _signal(),
        _signal(title="Duplicate translation"),
        _signal(title="The best jacket guide", url="https://example.com/guide"),
        _signal(title="NBA finals jacket", url="https://example.com/noise"),
        _signal(source_id="not-whitelisted", url="https://example.com/other"),
        _signal(published="2026-08-15", url="https://example.com/old"),
        _signal(region="jp", source_id="fashionsnap", title="日本発売", summary="", url=""),
    ]

    text = flash.extract(signals, "2026-08-18")

    assert "🌐 全球（1 則）" in text
    assert "🇯🇵 日本（1 則）" in text
    assert "Brand launches a new jacket" in text
    assert "Duplicate translation" not in text
    assert "best jacket guide" not in text
    assert "NBA finals" not in text
    assert "速報收集：7 則原始訊號、覆蓋未知" in text


def _observed(source_id="hypebeast", region="global", status="ok"):
    return {"source_id": source_id, "region": region, "status": status}


def test_extract_distinguishes_quiet_from_all_missing():
    quiet = flash.extract([], "2026-08-18", coverage=[_observed()])
    down = flash.extract([], "2026-08-18", coverage=[_observed(status="unavailable")])

    assert "無符合速報條件" in quiet
    assert "都未查到" in down and "不能判定有無消息" in down
    assert "無符合速報條件" not in down


@pytest.mark.parametrize("coverage", [None, [], [_observed(), _observed(status="unavailable")],
                                      [_observed(status="not-a-status")], "bad"])
def test_legacy_missing_or_inconsistent_coverage_is_unknown_not_quiet(coverage):
    result = flash.extract([], "2026-08-18", coverage=coverage)
    assert "白名單來源覆蓋未知" in result
    assert "無符合速報條件" not in result


def test_load_signals_and_missing_yaml(tmp_path, monkeypatch):
    path = tmp_path / "signals.yml"
    path.write_text("signals:\n  - title: Example\n", encoding="utf-8")
    assert flash._load_signals(str(path)) == ([{"title": "Example"}], None)

    monkeypatch.setattr(flash, "yaml", None)
    try:
        flash._load_signals(str(path))
    except SystemExit as exc:
        assert "pyyaml" in str(exc)
    else:
        raise AssertionError("missing YAML support must terminate with guidance")


def test_collect_live_reports_each_warning(monkeypatch, capsys):
    class FakeCollector:
        @staticmethod
        def rss_sources():
            return [{"id": "hypebeast"}, {"id": "outside"}]

        @staticmethod
        def collect(sources, *, coverage):
            assert sources == [{"id": "hypebeast"}]
            coverage.append(_observed())
            return ([{"title": "x"}], ["one notice", "two notice"])

    monkeypatch.setitem(flash.sys.modules, "collect_raw_signals", FakeCollector)
    signals, coverage = flash._collect_live()

    assert signals == [{"title": "x"}]
    assert coverage == [_observed()]
    err = capsys.readouterr().err
    assert "one notice" in err and "two notice" in err


def test_main_offline_writes_requested_file(tmp_path, monkeypatch, capsys):
    signal_path = tmp_path / "signals.yml"
    signal_path.write_text("signals: []\n", encoding="utf-8")
    out = tmp_path / "nested" / "flash.md"
    monkeypatch.setattr(
        flash.sys,
        "argv",
        ["prog", "--date", "2026-08-18", "--signals-in", str(signal_path), "--out", str(out)],
    )

    flash.main()

    report = out.read_text(encoding="utf-8")
    assert report.startswith("# ⚡ Style 速報 — 2026-08-18")
    assert "白名單來源覆蓋未知" in report and "無符合速報條件" not in report
    assert "速報已產出" in capsys.readouterr().out


def test_clip_and_region_cap_hold_at_their_exact_boundaries():
    """兩個邊界的零測試點（2026-08-29 突變測試找到）。

    - `_clip` 的省略號：長度**剛好等於** limit 時不該加「…」——加了等於騙讀者說內容被截斷。
      既有測試只驗 `abcdef` 截到 3（超過的情況），等長那一格沒人踩。
    - 每區則數上限：`rows[:MAX_PER_REGION]` 的 off-by-one 沒有守衛，多印一則不會有測試變紅。
    """
    assert flash._clip("abc", limit=3) == "abc"      # 剛好等長 → 不加省略號
    assert flash._clip("abcd", limit=3) == "abc…"    # 超過才加

    over = [
        _signal(title=f"Item {i}", url=f"https://example.com/news/item-{i}")
        for i in range(flash.MAX_PER_REGION + 3)
    ]
    text = flash.extract(over, "2026-08-18")
    assert f"🌐 全球（{flash.MAX_PER_REGION} 則）" in text
    assert f"Item {flash.MAX_PER_REGION}" not in text


def test_recent_window_never_returns_empty_even_for_zero_days():
    """`--days 0` 是合法 CLI 輸入（argparse `type=int` 不擋負數與 0）。

    視窗的 `max(days, 1)` 是 fail-safe：至少收今天。下限若被改成 0，`--days 0` 會回空集合
    → 速報永遠 0 則，而且會走進「市場安靜」那條敘述、被讀成「今天沒事發生」。
    """
    assert flash._recent_window("2026-08-18", 0) == {"2026-08-18"}
    assert flash._recent_window("2026-08-18", 1) == {"2026-08-18"}


def test_live_and_replayed_rss_keep_partial_coverage_visible_with_positive_news(tmp_path, monkeypatch):
    providers = [
        {"id": "fashionsnap", "region": "jp", "rss": "jp-fixture"},
        {"id": "hypebeast-jp", "region": "jp", "rss": "jp-empty-fixture"},
        {"id": "wwd", "region": "us-eu", "rss": "http-failure-fixture"},
        {"id": "sneakernews", "region": "us-eu", "rss": "waf-fixture"},
        {"id": "hypebeast-kr", "region": "kr", "rss": "bad-xml-fixture"},
        {"id": "not-whitelisted", "region": "global", "rss": "skip-fixture"},
    ]
    responses = {
        "jp-fixture": "<rss><channel><item><title>New jacket</title><link>https://example.test/jacket</link>"
                      "<pubDate>Tue, 18 Aug 2026 09:00:00 GMT</pubDate></item></channel></rss>",
        "jp-empty-fixture": '<feed xmlns="http://www.w3.org/2005/Atom"><title>Empty news</title></feed>',
        "http-failure-fixture": None,
        "waf-fixture": "<html><body>Blocked</body></html>",
        "bad-xml-fixture": "<rss><channel>",
    }
    class FakeCollector:
        @staticmethod
        def rss_sources():
            return providers

        @staticmethod
        def collect(sources, *, coverage):
            return collector.collect(sources, coverage=coverage, fetcher=responses.__getitem__)

    monkeypatch.setitem(flash.sys.modules, "collect_raw_signals", FakeCollector)
    rows, coverage = flash._collect_live()
    assert coverage == [_observed("fashionsnap", "jp"), _observed("hypebeast-jp", "jp"),
                        _observed("wwd", "us-eu", "unavailable"),
                        _observed("sneakernews", "us-eu", "invalid_feed"),
                        _observed("hypebeast-kr", "kr", "invalid_feed")]
    path = tmp_path / "raw.yml"
    path.write_text(collector.to_yaml(rows, coverage=coverage), encoding="utf-8")
    replay_rows, replay_coverage = flash._load_signals(str(path))
    report = flash.extract(rows, "2026-08-18", coverage=coverage)
    assert report == flash.extract(replay_rows, "2026-08-18", coverage=replay_coverage)
    assert "New jacket" in report and "3 個白名單來源未查到" in report
    assert "日本 2/2" in report and "歐美 0/2" in report and "韓國 0/1" in report
    assert "未涵蓋：🌐 全球" in report


def test_empty_feed_and_excluded_rows_are_valid_observations_not_failed_sources(monkeypatch):
    sources = [
        {"id": "hypebeast", "region": "global", "rss": "empty"},
        {"id": "fashionsnap", "region": "jp", "rss": "filtered", "type": "community"},
        {"id": "not-whitelisted", "region": "kr", "rss": "unavailable"},
    ]
    entry = ("<rss><channel><item><title>Definitely spam</title>"
             "<pubDate>Tue, 18 Aug 2026 09:00:00 GMT</pubDate></item></channel></rss>")
    payload = {"empty": "<rss><channel><title>Empty</title></channel></rss>",
               "filtered": entry, "unavailable": None}
    monkeypatch.setattr(collector, "is_spam", lambda *_: True)
    coverage = []
    rows, warnings = collector.collect(sources, coverage=coverage, fetcher=payload.__getitem__)
    assert not rows and len(warnings) == 2
    assert [r["status"] for r in coverage] == ["ok", "ok", "unavailable"]
    report = flash.extract(rows, "2026-08-18", coverage=coverage)
    assert "無符合速報條件" in report and "⚠️" not in report


def test_offline_cli_does_not_turn_recorded_total_outage_into_quiet_market(tmp_path, monkeypatch):
    path = tmp_path / "outage.yml"
    path.write_text("signals: []\ncoverage:\n- source_id: wwd\n  region: us-eu\n  status: unavailable\n",
                    encoding="utf-8")
    out = tmp_path / "report.md"
    monkeypatch.setattr(flash.sys, "argv", ["flash", "--signals-in", str(path), "--out", str(out)])
    flash.main()
    report = out.read_text(encoding="utf-8")
    assert "都未查到" in report and "無符合速報條件" not in report
