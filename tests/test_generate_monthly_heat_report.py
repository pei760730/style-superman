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
    """測的是 baseline_label / baseline_movement 的**函式契約**，不是某地區當下的資料。

    ⚠️ 2026-09-05 訂正：這支原本硬斷言 `baseline_label(REGIONS["jp"]) == "無"` 與
    「jp 的 movement 含『無可自動收的量化基準』」——那是把 **D24 前的錯誤狀態釘死**。
    D24（2026-06-21）用 SNKRDUNK 重建了日本量化板，`snkrdunk.yml` 也在 repo 裡，
    但 `REGIONS["jp"]["baselines"]` 忘了接；**這支測試會讓「把它接上」看起來像迴歸**，
    是修復路上的絆索。改成用合成 region 測空/非空兩條分支，地區實際資料由
    `test_every_region_scoped_ranking_file_is_claimed_as_a_baseline` 從 yaml 推導著看。
    """
    monkeypatch.setattr(monthly, "latest_period", lambda filename: "period-" + filename)

    empty = {"suffix": "xx", "baselines": ()}
    assert monthly.baseline_label(empty) == "無"
    assert "無可自動收的量化基準" in monthly.baseline_movement(empty)

    assert monthly.baseline_label(monthly.REGIONS["us-eu"]) == (
        "Lyst period-lyst-index.yml・StockX period-stockx.yml"
    )

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


def test_every_region_scoped_ranking_file_is_claimed_as_a_baseline():
    """`data/rankings/` 裡凡是 `region` 對得上某個月報地區的檔，都必須被那個地區認領為 baseline。

    立法理由（2026-09-05 稽核）：D24（2026-06-21）用 SNKRDUNK 重建了日本球鞋轉售量化板、
    `data/rankings/snkrdunk.yml` 也建好了，但 `REGIONS["jp"]["baselines"]` 一直是 `()`，
    註解引用的還是 D24 **前一週**（06-14）的狀態。後果不是骨架難看而是**產出說謊**：
    2026-08-jp.md 與 2026-09-jp.md 兩份月報都白紙黑字寫「本區無可自動收的量化基準榜」，
    而那個榜就躺在同一個 repo 裡，76 天沒人用。

    這裡不維護第二份手工清單（那正是會漂開的東西），而是**從 yaml 自己的 `region` 欄位推導**：
    新增一個排行檔、或改它的 region，忘了接進對應地區就會紅。
    """
    import yaml

    rankings_dir = monthly.RANKINGS_DIR
    for path in sorted(rankings_dir.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        region_key = data.get("region")
        if region_key not in monthly.REGIONS:
            continue  # 跨區指數（region 留空）或非月報地區（如 kr）——不在此契約內
        claimed = {filename for filename, _label in monthly.REGIONS[region_key]["baselines"]}
        assert path.name in claimed, (
            f"{path.name} 的 region={region_key!r} 對應到月報地區 {region_key!r}，"
            f"但 REGIONS[{region_key!r}]['baselines'] 只有 {sorted(claimed)}——"
            f"該地區的月報會印「無可自動收的量化基準」，而這個檔就在 repo 裡"
        )


def test_baseline_label_names_the_actual_snapshot_not_the_word_none():
    """有 baseline 的地區，標籤要帶出真的快照 period，不能還是「無」。

    反向探針：把某地區的 baselines 清空就會紅——擋的是「檔案還在但被從清單裡拿掉」這種靜默退化。
    """
    for key, region in monthly.REGIONS.items():
        if not region["baselines"]:
            continue
        label = monthly.baseline_label(region)
        assert label != "無", f"{key} 有 baselines 卻回傳「無」"
        for _filename, name in region["baselines"]:
            assert name in label, f"{key} 的標籤 {label!r} 沒有帶出 {name}"
