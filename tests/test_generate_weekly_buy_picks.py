import datetime as dt
import re

import pytest

from scripts import generate_weekly_buy_picks as weekly

# 合成的主編已判定文字，不是來源辨識器：測骨架相容，不宣稱驗出來源事實。
EVIDENCE_EXAMPLES = [
    (
        "original-and-two-reprints",
        (
            "原出現次數 8｜本次檢視來源 3 筆：確認獨立 1／轉載 2／不確定 0；"
            "[A 原稿：自採](https://a.example.invalid/one)、"
            "[B：明示轉載 A](https://b.example.invalid/two)、"
            "[C：明示轉載 A](https://c.example.invalid/three)。"
        ),
    ),
    (
        "reprints-without-original-in-scope",
        (
            "原出現次數 8｜本次檢視來源 3 筆：確認獨立 0／轉載 3／不確定 0；"
            "[B](https://b.example.invalid/two)、[C](https://c.example.invalid/three)、"
            "[D](https://d.example.invalid/four) 均明示轉載 A，A 未納入本次可核對紀錄。"
        ),
    ),
    (
        "different-domains-unconfirmed-provenance",
        (
            "原出現次數 8｜本次檢視來源 2 筆：確認獨立 0／轉載 0／不確定 2；"
            "[E](https://e.example.invalid/one)、[F](https://f.example.invalid/two) "
            "商品均確認為合成 FS-100，但原稿關係未明，網域不同不作獨立證據。"
        ),
    ),
    (
        "rerun-and-reordered-observation",
        (
            "原出現次數 8｜本次檢視來源 1 筆：確認獨立 1／轉載 0／不確定 0；"
            "[A](https://a.example.invalid/one) 同一觀測的重跑副本去重，改變檢視順序不增量。"
        ),
    ),
    (
        "same-name-roundup-distinct-products",
        (
            "原出現次數 4｜本次檢視來源 1 筆：確認獨立 1／轉載 0／不確定 0；"
            "[roundup](https://a.example.invalid/list?product_id=FS100&variant=cotton) "
            "已明示自採 FS-100 與 FS-200 兩款；本項只歸屬 FS-100，FS-200 另列。"
        ),
    ),
    (
        "identity-insufficient-excluded",
        (
            "原出現次數 4｜補充證據：無法核對；"
            "[照片](https://a.example.invalid/blur) 型號不明，另註無法歸屬，不納入本項 M 或 U。"
        ),
    ),
    ("legacy-aggregate-only", "原出現次數 8｜補充證據：無法核對；未提供逐筆證據。"),
    ("missing-original-count", "原出現次數 待查｜補充證據：無法核對。"),
]


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
    (tmp_path / "empty.yml").write_text(
        "source: Empty\nsnapshots: []\n", encoding="utf-8"
    )
    monkeypatch.setattr(weekly, "RANKINGS_DIR", tmp_path)

    assert weekly.latest_ranking_periods() == ["Alpha 2025-annual", "Zed 2026-Q2"]


def test_latest_ranking_periods_degrades_without_yaml(monkeypatch):
    monkeypatch.setattr(weekly, "yaml", None)
    assert weekly.latest_ranking_periods() == ["（缺 pyyaml，略過 rankings 摘要）"]


def test_build_fills_derived_fields_and_replaces_remaining_placeholders(
    tmp_path, monkeypatch
):
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


def test_weekly_template_keeps_existing_fields_and_five_by_three_slots():
    text = weekly.TEMPLATE.read_text(encoding="utf-8")
    slots = [f"{part}{number}" for part in "htbfa" for number in (1, 2, 3)]
    fields = ("item", "what", "region", "price_sku", "why_hot", "hype")
    expected = {f"{slot}_{field}" for slot in slots for field in fields}
    expected.update(
        (
            "week",
            "date_range",
            "signal_basis",
            "last_week_review",
            "one_pick",
            "summary",
        )
    )
    assert set(re.findall(r"\{\{([a-z0-9_]+)\}\}", text)) == expected
    zones = re.split(r"^## ", text, flags=re.MULTILINE)[1:6]
    assert [
        len(re.findall(r"^### [123]\. ", zone, re.MULTILINE)) for zone in zones
    ] == [3] * 5


@pytest.mark.parametrize(
    "case_id,annotation", EVIDENCE_EXAMPLES, ids=[case[0] for case in EVIDENCE_EXAMPLES]
)
def test_build_preserves_reviewed_evidence_inside_existing_why_hot(
    case_id, annotation, tmp_path, monkeypatch
):
    """實際模板與 build 的相容測試；分類判斷另由主編逐例審閱。"""
    original = weekly.TEMPLATE.read_text(encoding="utf-8")
    template = tmp_path / f"{case_id}.md"
    reason = "合成主編理由與選品順序保留。"
    template.write_text(
        original.replace("{{h1_why_hot}}", reason + annotation), encoding="utf-8"
    )
    monkeypatch.setattr(weekly, "TEMPLATE", template)
    monkeypatch.setattr(weekly, "latest_ranking_periods", lambda: ["合成快照"])

    label, body = weekly.build(dt.date(2099, 1, 7))

    assert label == "2099-W02"
    assert f"- **為什麼這週在紅：** {reason}{annotation}\n" in body
    assert "{{" not in body
    assert body.count("- **為什麼這週在紅：**") == 15
    assert body.count("- **炒作 vs 真（週期位置）：**") == 15
    assert re.findall(r"^## .+$", body, re.MULTILINE) == re.findall(
        r"^## .+$", original, re.MULTILINE
    )
    assert re.findall(r"^### ([123])\. ", body, re.MULTILINE) == ["1", "2", "3"] * 5


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
