#!/usr/bin/env python3
"""
generate_weekly_buy_picks.py
============================
產出「本週最值得買 Head-to-Toe」的骨架草稿。

這支腳本不做 AI 撰寫（決策 D5），它負責：
  1. 算出 ISO 週期與日期範圍（週一～週日）
  2. 載入 templates/weekly_buy_picks_template.md
  3. 自動帶入「本週訊號依據」：本週的 daily briefs 清單 + 各排行快照最新 period
  4. 把骨架寫到 reports/buy_shortlist/YYYY-Wnn.md

挑買內容由 AI（prompts/weekly_buy_picks.md）或人工補上。

用法：
    python scripts/generate_weekly_buy_picks.py                 # 本週
    python scripts/generate_weekly_buy_picks.py --date 2026-06-10
    python scripts/generate_weekly_buy_picks.py --draft         # 產 *.draft.md（不入版控）
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
TEMPLATE = ROOT / "templates" / "weekly_buy_picks_template.md"
OUT_DIR = ROOT / "reports" / "buy_shortlist"
DAILY_DIR = ROOT / "reports" / "daily"
RANKINGS_DIR = ROOT / "data" / "rankings"


def week_bounds(day: dt.date) -> tuple[dt.date, dt.date]:
    """回傳該日所屬 ISO 週的（週一, 週日）。"""
    monday = day - dt.timedelta(days=day.weekday())
    return monday, monday + dt.timedelta(days=6)


def briefs_in_range(start: dt.date, end: dt.date) -> list[str]:
    names = []
    for report in sorted(DAILY_DIR.glob("????-??-??.md")):
        try:
            d = dt.date.fromisoformat(report.stem)
        except ValueError:
            continue
        if start <= d <= end:
            names.append(report.stem)
    return names


def latest_ranking_periods() -> list[str]:
    """各排行快照檔最新一筆的 period，給「為什麼是本週」當數據基準。"""
    if yaml is None:
        return ["（缺 pyyaml，略過 rankings 摘要）"]
    parts = []
    for path in sorted(RANKINGS_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        snaps = data.get("snapshots") or []
        if snaps and isinstance(snaps[0], dict):
            parts.append(f"{data.get('source', path.stem)} {snaps[0].get('period', '?')}")
    return parts


def build(day: dt.date) -> tuple[str, str]:
    """回傳 (週標籤 YYYY-Wnn, 骨架全文)。"""
    iso = day.isocalendar()
    week_label = f"{iso[0]}-W{iso[1]:02d}"
    monday, sunday = week_bounds(day)

    body = TEMPLATE.read_text(encoding="utf-8")
    body = body.replace("{{week}}", week_label)
    body = body.replace("{{date_range}}", f"{monday.isoformat()} ～ {sunday.isoformat()}")

    briefs = briefs_in_range(monday, sunday)
    basis = (
        f"daily briefs：{', '.join(briefs) if briefs else '（本週尚無）'}"
        f" ｜ rankings：{' / '.join(latest_ranking_periods())}"
    )
    body = body.replace("{{signal_basis}}", basis)
    # 其餘 {{...}} 佔位留給 AI / 人工，整段換成待填標記
    body = re.sub(r"\{\{[a-z0-9_]+\}\}", "_待填_", body)
    return week_label, body


def main() -> None:
    parser = argparse.ArgumentParser(description="產出本週 Head-to-Toe 挑買榜骨架")
    parser.add_argument("--date", help="以該日期所屬 ISO 週產出（YYYY-MM-DD）")
    parser.add_argument("--draft", action="store_true", help="輸出 *.draft.md（不入版控）")
    args = parser.parse_args()

    day = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    week_label, body = build(day)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = ".draft.md" if args.draft else ".md"
    out = OUT_DIR / f"{week_label}{suffix}"
    if out.exists() and not args.draft:
        print(f"⚠️  {out} 已存在，不覆寫（封存快照不回改）。要重產請先手動處理。")
        raise SystemExit(1)
    out.write_text(body, encoding="utf-8")
    print(f"✅ 已產出骨架：{out.relative_to(ROOT)}")
    print("   下一步：依 prompts/weekly_buy_picks.md 填入 4 區 × 3 樣與理由。")


if __name__ == "__main__":
    main()
