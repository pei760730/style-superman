#!/usr/bin/env python3
"""
generate_monthly_heat_report.py
===============================
產出當月「歐美熱度速報」的骨架草稿（C4 MVP）。

這支腳本**不做 web 判斷**，只負責：
  1. 載入 templates/monthly_heat_report_template.md
  2. 自動帶入當月、最新 Lyst / StockX 季度基準 period、來源摘要
  3. 其餘品牌 / 單品判斷留 `待填`，交給 prompts/monthly_heat_report.md（AI / 人工）

對照 generate_daily_brief.py：同樣是「填骨架」，內容判斷不在這裡做。
每月 1 號的遠端排程是「全自動產全文」；這支是「本地手動產骨架」的入口。

用法：
    python scripts/generate_monthly_heat_report.py --month 2026-06
    python scripts/generate_monthly_heat_report.py --month 2026-06 --region us-eu
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

REGION_SUFFIX = {"us-eu": "eu"}  # region → 檔名後綴；目前僅歐美
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


def source_summary() -> str:
    """歐美來源摘要，放進報告底部供參考。"""
    if yaml is None:
        return "（缺 pyyaml）"
    path = DATA_DIR / "sources.yml"
    if not path.exists():
        return "（無 sources.yml）"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    eu = [s for s in data.get("sources", []) if s.get("region") in ("us-eu", "global")]
    media = sum(1 for s in eu if s.get("type") == "media")
    ranking = sum(1 for s in eu if s.get("type") == "ranking")
    return f"歐美/全球來源 {len(eu)} 個（media {media}、ranking {ranking}）"


def build(month: str) -> str:
    lyst = latest_period("lyst-index.yml")
    stockx = latest_period("stockx.yml")
    body = TEMPLATE.read_text(encoding="utf-8") if TEMPLATE.exists() else "# 月報 · {{month}}\n（找不到模板）\n"

    # 只填可自動推導的 metadata；品牌/單品等判斷留給 AI/人工。
    body = body.replace("{{month}}", month)
    body = body.replace("{{generated_date}}", dt.date.today().isoformat())
    body = body.replace("{{baseline_quarter}}", lyst)
    body = body.replace("{{signal_strength}}", "待填")
    body = body.replace("{{collection_limits}}", "待填（若 403 / 無 API，在此降級說明）")

    footer = (
        f"\n\n---\n\n"
        f"<!-- 骨架由 generate_monthly_heat_report.py 產出 · {dt.date.today().isoformat()} -->\n"
        f"<!-- 季度基準：Lyst {lyst}、StockX {stockx} -->\n"
        f"<!-- {source_summary()} -->\n"
        f"<!-- 下一步：依 prompts/monthly_heat_report.md 填入本月訊號（每條標 L1–L4 層級與信心） -->\n"
    )
    return body + footer


def main() -> None:
    parser = argparse.ArgumentParser(description="產出當月歐美熱度速報骨架")
    parser.add_argument("--month", required=True, help="YYYY-MM")
    parser.add_argument("--region", choices=list(REGION_SUFFIX), default="us-eu")
    parser.add_argument("--draft", action="store_true", help="輸出 *.draft.md（不入版控）")
    args = parser.parse_args()

    if not MONTH_RE.match(args.month):
        parser.error("--month 格式須為 YYYY-MM，例如 2026-06")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = REGION_SUFFIX[args.region]
    name = f"{args.month}-{suffix}" + (".draft.md" if args.draft else ".md")
    out_path = OUT_DIR / name

    if out_path.exists():
        print(f"⚠️  {out_path.name} 已存在，未覆蓋。要重產請先刪除或改用 --draft。")
        return

    out_path.write_text(build(args.month), encoding="utf-8")
    print(f"✅ 已產出骨架：{out_path.relative_to(ROOT)}")
    print("   下一步：依 prompts/monthly_heat_report.md 用 AI 或人工填入本月品牌 / 單品判斷。")


if __name__ == "__main__":
    main()
