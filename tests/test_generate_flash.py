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
    assert "速報收集：7 則原始訊號、0 來源降級" in text


def test_extract_distinguishes_quiet_market_from_collection_failure():
    quiet = flash.extract([], "2026-08-18")
    degraded = flash.extract([], "2026-08-18", degraded=3)

    assert "無符合速報條件" in quiet
    assert "可能是收集端問題而非市場安靜" in degraded
    assert "3 個來源收集失敗/降級" in degraded


def test_load_signals_and_missing_yaml(tmp_path, monkeypatch):
    path = tmp_path / "signals.yml"
    path.write_text("signals:\n  - title: Example\n", encoding="utf-8")
    assert flash._load_signals(str(path)) == [{"title": "Example"}]

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
            return [{"id": "one"}]

        @staticmethod
        def collect(sources):
            assert sources == [{"id": "one"}]
            return ([{"title": "x"}], ["one failed", "two failed"])

    monkeypatch.setitem(flash.sys.modules, "collect_raw_signals", FakeCollector)
    signals, degraded = flash._collect_live()

    assert signals == [{"title": "x"}]
    assert degraded == 2
    assert "one failed" in capsys.readouterr().err


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

    assert out.read_text(encoding="utf-8").startswith("# ⚡ Style 速報 — 2026-08-18")
    assert "速報已產出" in capsys.readouterr().out
