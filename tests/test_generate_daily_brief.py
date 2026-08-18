from scripts import generate_daily_brief as daily


def test_load_yaml_handles_missing_file_and_dependency(tmp_path, monkeypatch, capsys):
    assert daily.load_yaml(tmp_path / "missing.yml") == {}
    assert "找不到設定檔" in capsys.readouterr().out

    monkeypatch.setattr(daily, "yaml", None)
    assert daily.load_yaml(tmp_path / "missing.yml") == {}
    assert "未安裝 pyyaml" in capsys.readouterr().out


def test_summarize_sources_is_sorted_and_handles_empty():
    sources = [{"region": "jp"}, {"region": "global"}, {"region": "jp"}, {}]
    assert daily.summarize_sources(sources) == "?: 1 ｜ global: 1 ｜ jp: 2"
    assert daily.summarize_sources([]) == "（無來源設定）"


def test_build_brief_fills_metadata_and_preserves_editorial_slots(tmp_path, monkeypatch):
    template = tmp_path / "daily.md"
    template.write_text(
        "# {{date}}\n{{signal_strength}} {{signal_count}} {{headline_count}} {{trend_title}}",
        encoding="utf-8",
    )
    monkeypatch.setattr(daily, "TEMPLATE", template)
    monkeypatch.setattr(daily, "load_yaml", lambda path: {"sources": [{"region": "jp"}]})

    text = daily.build_brief("2026-08-18", "<!-- rss -->\n")

    assert text.startswith("# 2026-08-18\n_待填_ 0 0 {{trend_title}}")
    assert "來源覆蓋：jp: 1" in text
    assert "<!-- rss -->" in text


def test_collect_rss_writes_offline_pack_and_reports_degradation(tmp_path, monkeypatch, capsys):
    class FakeCollector:
        @staticmethod
        def rss_sources():
            return [{"id": "one"}]

        @staticmethod
        def collect(sources):
            assert sources == [{"id": "one"}]
            return ([{"title": "signal"}], ["one failed", "two failed", "three failed", "four failed"])

        @staticmethod
        def to_yaml(signals):
            return "signals: 1\n"

    monkeypatch.setitem(daily.sys.modules, "collect_raw_signals", FakeCollector)
    out = tmp_path / "raw.yml"

    note = daily.collect_rss(str(out))

    assert out.read_text(encoding="utf-8") == "signals: 1\n"
    assert "1 則事實訊號、4 來源降級，已寫到" in note
    stdout = capsys.readouterr().out
    assert "raw_signal_pack：收集 1 則" in stdout
    assert " …" in stdout


def test_collect_rss_degrades_when_import_fails(monkeypatch):
    original_import = __import__

    def fail_import(name, *args, **kwargs):
        if name == "collect_raw_signals":
            raise ImportError("offline fixture")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fail_import)
    monkeypatch.delitem(daily.sys.modules, "collect_raw_signals", raising=False)

    assert "RSS 收集略過" in daily.collect_rss(None)


def test_main_writes_draft_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(daily, "ROOT", tmp_path)
    monkeypatch.setattr(daily, "OUT_DIR", tmp_path)
    monkeypatch.setattr(daily, "build_brief", lambda date_str, rss_note: date_str + rss_note)
    monkeypatch.setattr(daily.sys, "argv", ["prog", "--date", "2026-08-18", "--draft"])

    daily.main()

    assert (tmp_path / "2026-08-18.draft.md").read_text(encoding="utf-8") == "2026-08-18"
