#!/usr/bin/env python3
"""
generate_monthly_heat_report.py
===============================
產出當月「熱度速報」的骨架草稿（C4 MVP；2026-06-11 起支援多地區）。

這支腳本**不做 web 判斷**，只負責：
  1. 載入 templates/monthly_heat_report_template.md
  2. 自動帶入當月、該地區的季度基準 period、來源摘要
  3. 其餘品牌 / 單品判斷留 `待填`，交給 prompts/monthly_heat_report.md（AI / 人工）

對照 generate_daily_brief.py：同樣是「填骨架」，內容判斷不在這裡做。
每月 1 號的遠端排程是「全自動產全文」；這支是「本地手動產骨架」的入口。

用法：
    python scripts/generate_monthly_heat_report.py --month 2026-06
    python scripts/generate_monthly_heat_report.py --month 2026-06 --region jp
    python scripts/generate_monthly_heat_report.py --month 2026-06 --draft   # 產 .draft.md（不入版控）
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RANKINGS_DIR = DATA_DIR / "rankings"
TEMPLATE = ROOT / "templates" / "monthly_heat_report_template.md"
OUT_DIR = ROOT / "reports" / "monthly"

# 地區設定：檔名後綴 / 顯示名 / 量化基準榜 / 來源 region 過濾
REGIONS = {
    "us-eu": {
        "suffix": "eu",
        "name": "歐美",
        "baselines": (("lyst-index.yml", "Lyst"), ("stockx.yml", "StockX")),
        "source_regions": ("us-eu", "global"),
    },
    "jp": {
        "suffix": "jp",
        "name": "日本",
        # 日本可自動比對的量化基準只有 Mercari（ZOZO 等即時榜不可自動收，見 docs/rankings.md）
        "baselines": (("mercari-jp.yml", "Mercari"),),
        "source_regions": ("jp", "global"),
    },
}
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")


def latest_period(filename: str) -> str:
    """讀某排行檔的最新 snapshot period；缺檔/缺套件回傳 待查。"""
    if yaml is None:
        return "待查（缺 pyyaml）"
    path = RANKINGS_DIR / filename
    if not path.exists():
        return "待查"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    snaps = data.get("snapshots") or []
    if snaps and isinstance(snaps[0], dict):
        return str(snaps[0].get("period", "待查"))
    return "待查"


def baseline_label(region: dict) -> str:
    """該地區的量化基準標籤，例：「Lyst 2026-Q1・StockX 2025-annual」。"""
    return "・".join(f"{label} {latest_period(fn)}" for fn, label in region["baselines"])


def source_summary(region: dict) -> str:
    """該地區來源摘要，放進報告底部供參考。"""
    if yaml is None:
        return "（缺 pyyaml）"
    path = DATA_DIR / "sources.yml"
    if not path.exists():
        return "（無 sources.yml）"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    hits = [s for s in data.get("sources", []) if s.get("region") in region["source_regions"]]
    media = sum(1 for s in hits if s.get("type") == "media")
    ranking = sum(1 for s in hits if s.get("type") == "ranking")
    return f"{region['name']}/全球來源 {len(hits)} 個（media {media}、ranking {ranking}）"


def build(month: str, region: dict) -> str:
    body = TEMPLATE.read_text(encoding="utf-8") if TEMPLATE.exists() else "# 月報 · {{month}}\n（找不到模板）\n"

    # 只填可自動推導的 metadata；品牌/單品等判斷留給 AI/人工。
    body = body.replace("{{month}}", month)
    body = body.replace("{{region_name}}", region["name"])
    body = body.replace("{{generated_date}}", dt.date.today().isoformat())
    body = body.replace("{{baseline_label}}", baseline_label(region))
    body = body.replace("{{signal_strength}}", "待填")
    body = body.replace("{{collection_limits}}", "待填（若 403 / 無 API，在此降級說明）")

    footer = (
        f"\n\n---\n\n"
        f"<!-- 骨架由 generate_monthly_heat_report.py 產出 · {dt.date.today().isoformat()} -->\n"
        f"<!-- 量化基準：{baseline_label(region)} -->\n"
        f"<!-- {source_summary(region)} -->\n"
        f"<!-- 下一步：依 prompts/monthly_heat_report.md 填入本月訊號（每條標 L1–L4 層級與信心） -->\n"
    )
    return body + footer


def main() -> None:
    parser = argparse.ArgumentParser(description="產出當月熱度速報骨架（歐美 / 日本）")
    parser.add_argument("--month", required=True, help="YYYY-MM")
    parser.add_argument("--region", choices=list(REGIONS), default="us-eu")
    parser.add_argument("--draft", action="store_true", help="輸出 *.draft.md（不入版控）")
    args = parser.parse_args()

    if not MONTH_RE.match(args.month):
        parser.error("--month 格式須為 YYYY-MM，例如 2026-06")

    region = REGIONS[args.region]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{args.month}-{region['suffix']}" + (".draft.md" if args.draft else ".md")
    out_path = OUT_DIR / name

    if out_path.exists():
        print(f"⚠️  {out_path.name} 已存在，未覆蓋。要重產請先刪除或改用 --draft。")
        return

    out_path.write_text(build(args.month, region), encoding="utf-8")
    print(f"✅ 已產出骨架：{out_path.relative_to(ROOT)}")
    print("   下一步：依 prompts/monthly_heat_report.md 用 AI 或人工填入本月品牌 / 單品判斷。")


if __name__ == "__main__":
    main()
