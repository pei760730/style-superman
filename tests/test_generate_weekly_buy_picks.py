import datetime as dt

from scripts import generate_weekly_buy_picks as weekly


def test_week_bounds_handles_midweek_and_iso_year_boundary():
    assert weekly.week_bounds(dt.date(2026, 8, 19)) == (
        dt.date(2026, 8, 17),
        dt.date(2026, 8, 23),
    )
    assert weekly.week_bounds(dt.date(2027, 1, 1)) == (
        dt.date(2026, 12, 28),
        dt.date(2027, 1, 3),
    )


def test_latest_ranking_periods_reads_sorted_yaml_files(tmp_path, monkeypatch):
    (tmp_path / "z.yml").write_text(
        "source: Zed\nsnapshots:\n  - period: 2026-Q2\n", encoding="utf-8"
    )
    (tmp_path / "a.yml").write_text(
        "source: Alpha\nsnapshots:\n  - period: 2025-annual\n", encoding="utf-8"
    )
    (tmp_path / "empty.yml").write_text("source: Empty\nsnapshots: []\n", encoding="utf-8")
    monkeypatch.setattr(weekly, "RANKINGS_DIR", tmp_path)

    assert weekly.latest_ranking_periods() == ["Alpha 2025-annual", "Zed 2026-Q2"]


def test_latest_ranking_periods_degrades_without_yaml(monkeypatch):
    monkeypatch.setattr(weekly, "yaml", None)
    assert weekly.latest_ranking_periods() == ["（缺 pyyaml，略過 rankings 摘要）"]


def test_build_fills_derived_fields_and_replaces_remaining_placeholders(tmp_path, monkeypatch):
    template = tmp_path / "weekly.md"
    template.write_text(
        "# {{week}}\n{{date_range}}\n{{signal_basis}}\n{{h1_item}}\n", encoding="utf-8"
    )
    monkeypatch.setattr(weekly, "TEMPLATE", template)
    monkeypatch.setattr(weekly, "latest_ranking_periods", lambda: ["Lyst 2026-Q1"])

    label, body = weekly.build(dt.date(2027, 1, 1))

    assert label == "2026-W53"
    assert "2026-12-28 ～ 2027-01-03" in body
    assert "rankings：Lyst 2026-Q1" in body
    assert "{{" not in body
    assert "_待填_" in body


def test_main_writes_draft_and_refuses_existing_snapshot(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(weekly, "ROOT", tmp_path)
    monkeypatch.setattr(weekly, "OUT_DIR", tmp_path)
    monkeypatch.setattr(weekly, "build", lambda day: ("2026-W34", "body"))
    monkeypatch.setattr(weekly.sys, "argv", ["prog", "--date", "2026-08-18", "--draft"])

    weekly.main()
    assert (tmp_path / "2026-W34.draft.md").read_text(encoding="utf-8") == "body"

    (tmp_path / "2026-W34.md").write_text("archive", encoding="utf-8")
    monkeypatch.setattr(weekly.sys, "argv", ["prog", "--date", "2026-08-18"])
    try:
        weekly.main()
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("existing archived snapshot must stop the command")
    assert "不覆寫" in capsys.readouterr().out
