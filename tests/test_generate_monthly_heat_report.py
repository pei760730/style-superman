from scripts import generate_monthly_heat_report as monthly


def test_latest_period_handles_dependency_file_and_shape(tmp_path, monkeypatch):
    monkeypatch.setattr(monthly, "RANKINGS_DIR", tmp_path)
    assert monthly.latest_period("missing.yml") == "待查"

    (tmp_path / "rank.yml").write_text(
        "snapshots:\n  - period: 2026-Q2\n", encoding="utf-8"
    )
    assert monthly.latest_period("rank.yml") == "2026-Q2"

    monkeypatch.setattr(monthly, "yaml", None)
    assert monthly.latest_period("rank.yml") == "待查（缺 pyyaml）"


def test_baseline_labels_and_movements_cover_regional_contracts(tmp_path, monkeypatch):
    monkeypatch.setattr(monthly, "latest_period", lambda filename: "period-" + filename)
    assert monthly.baseline_label(monthly.REGIONS["jp"]) == "無"
    assert monthly.baseline_label(monthly.REGIONS["us-eu"]) == (
        "Lyst period-lyst-index.yml・StockX period-stockx.yml"
    )
    assert "無可自動收的量化基準" in monthly.baseline_movement(monthly.REGIONS["jp"])

    other = {"suffix": "kr", "baselines": (("x.yml", "X"),)}
    assert "無季對季名次可比" in monthly.baseline_movement(other)

    monkeypatch.setattr(monthly, "yaml", None)
    assert "缺 pyyaml" in monthly.baseline_movement(monthly.REGIONS["us-eu"])


def test_eu_baseline_movement_uses_ranking_helper(tmp_path, monkeypatch):
    path = tmp_path / "lyst-index.yml"
    path.write_text("snapshots:\n  - period: new\n  - period: old\n", encoding="utf-8")
    monkeypatch.setattr(monthly, "RANKINGS_DIR", tmp_path)

    class FakeRankings:
        @staticmethod
        def lyst_comparison_text(data, top):
            assert len(data["snapshots"]) == 2
            assert top == 20
            return "comparison"

    monkeypatch.setitem(monthly.sys.modules, "track_rankings", FakeRankings)
    text = monthly.baseline_movement(monthly.REGIONS["us-eu"])

    assert "```\ncomparison\n```" in text
    assert "自有歷史" in text


def test_source_summary_counts_only_region_sources(tmp_path, monkeypatch):
    (tmp_path / "sources.yml").write_text(
        "sources:\n"
        "  - {region: jp, type: media}\n"
        "  - {region: global, type: ranking}\n"
        "  - {region: us-eu, type: media}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(monthly, "DATA_DIR", tmp_path)

    assert monthly.source_summary(monthly.REGIONS["jp"]) == (
        "日本/全球來源 2 個（media 1、ranking 1）"
    )


def test_build_fills_automatic_metadata_and_keeps_editorial_placeholders(tmp_path, monkeypatch):
    template = tmp_path / "monthly.md"
    template.write_text(
        "# {{region_name}} {{month}} {{generated_date}} {{baseline_label}} "
        "{{baseline_movement}} {{signal_strength}} {{collection_limits}} {{brand_1}}",
        encoding="utf-8",
    )
    monkeypatch.setattr(monthly, "TEMPLATE", template)
    monkeypatch.setattr(monthly, "baseline_label", lambda region: "BASE")
    monkeypatch.setattr(monthly, "baseline_movement", lambda region: "MOVE")
    monkeypatch.setattr(monthly, "source_summary", lambda region: "SOURCES")

    text = monthly.build("2026-08", monthly.REGIONS["jp"])

    assert "# 日本 2026-08" in text
    assert "BASE MOVE 待填 待填（若 403 / 無 API，在此降級說明） {{brand_1}}" in text
    assert "<!-- SOURCES -->" in text


def test_main_writes_draft_and_does_not_overwrite(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(monthly, "ROOT", tmp_path)
    monkeypatch.setattr(monthly, "OUT_DIR", tmp_path)
    monkeypatch.setattr(monthly, "build", lambda month, region: "first")
    monkeypatch.setattr(
        monthly.sys,
        "argv",
        ["prog", "--month", "2026-08", "--region", "jp", "--draft"],
    )

    monthly.main()
    out = tmp_path / "2026-08-jp.draft.md"
    assert out.read_text(encoding="utf-8") == "first"

    monkeypatch.setattr(monthly, "build", lambda month, region: "second")
    monthly.main()
    assert out.read_text(encoding="utf-8") == "first"
    assert "已存在，未覆蓋" in capsys.readouterr().out
