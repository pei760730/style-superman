#!/usr/bin/env python3
"""
score_trends.py
===============
對趨勢做加權評分與排序。

輸入是一份趨勢清單（每個趨勢含五個維度的 0–5 原始分），
輸出是加權後的綜合分與排序。權重與規則見 docs/trend_scoring_rules.md。

五個維度：
    heat              當下熱度
    growth            成長速度（比熱度更看「斜率」）
    longevity         可持續性（短命病毒 vs 長期趨勢）
    content_potential 內容可塑性（好不好拍）
    accessibility     落地度（一般人能不能穿 / 買）

用法：
    # 用內建範例資料跑一次（驗證腳本可用）
    python scripts/score_trends.py --demo

    # 從 JSON 檔讀趨勢清單
    python scripts/score_trends.py --input trends.json

JSON 格式（list[dict]）：
    [
      {"name": "barrel jeans", "heat": 4, "growth": 5,
       "longevity": 3, "content_potential": 4, "accessibility": 3},
      ...
    ]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Windows 終端機預設 cp950，emoji / 中文會炸。強制 stdout 走 UTF-8。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 權重：強調「成長性」與「內容潛力」——我們要的是能拍、又還在升的趨勢，
# 而不是已經到頂的大眾品。權重總和為 1.0。詳見 docs/trend_scoring_rules.md。
WEIGHTS = {
    "heat": 0.20,
    "growth": 0.30,
    "longevity": 0.15,
    "content_potential": 0.25,
    "accessibility": 0.10,
}

DIMENSIONS = list(WEIGHTS.keys())
MAX_RAW = 5  # 每個維度 0–5


def score_one(trend: dict) -> float:
    """回傳 0–100 的綜合分。缺維度視為 0 並警告。"""
    total = 0.0
    for dim, weight in WEIGHTS.items():
        raw = trend.get(dim)
        if raw is None:
            print(f"⚠️  趨勢 {trend.get('name', '?')} 缺維度 '{dim}'，以 0 計。")
            raw = 0
        raw = max(0, min(MAX_RAW, raw))  # 夾在 0–5
        total += (raw / MAX_RAW) * weight
    return round(total * 100, 1)


def rank(trends: list[dict]) -> list[dict]:
    """為每個趨勢算分並由高到低排序。"""
    for t in trends:
        t["score"] = score_one(t)
    return sorted(trends, key=lambda t: t["score"], reverse=True)


def tier_of(score: float) -> str:
    """把分數映射到行動分級。門檻見 docs/trend_scoring_rules.md。"""
    if score >= 75:
        return "🔥 主打 (push)"
    if score >= 55:
        return "✅ 採用 (use)"
    if score >= 40:
        return "👀 觀察 (watch)"
    return "🧊 暫存 (park)"


def print_table(ranked: list[dict]) -> None:
    print(f"\n{'#':>2}  {'分數':>5}  {'分級':<14}  趨勢")
    print("-" * 60)
    for i, t in enumerate(ranked, 1):
        print(f"{i:>2}  {t['score']:>5}  {tier_of(t['score']):<14}  {t.get('name', '?')}")
    print()


DEMO_DATA = [
    {"name": "barrel / banana leg jeans", "heat": 4, "growth": 5,
     "longevity": 3, "content_potential": 4, "accessibility": 3},
    {"name": "gorpcore (機能戶外)", "heat": 4, "growth": 3,
     "longevity": 4, "content_potential": 4, "accessibility": 3},
    {"name": "全身 tonal 棕 (mocha)", "heat": 3, "growth": 4,
     "longevity": 3, "content_potential": 5, "accessibility": 4},
    {"name": "suede 樂福鞋", "heat": 3, "growth": 3,
     "longevity": 4, "content_potential": 3, "accessibility": 4},
    {"name": "balaclava 巴拉克拉瓦帽", "heat": 2, "growth": 2,
     "longevity": 1, "content_potential": 3, "accessibility": 1},
]


def main() -> None:
    parser = argparse.ArgumentParser(description="趨勢加權評分與排序")
    parser.add_argument("--input", help="趨勢清單 JSON 檔路徑")
    parser.add_argument("--demo", action="store_true", help="用內建範例資料跑")
    parser.add_argument("--json", action="store_true", help="輸出 JSON 而非表格")
    args = parser.parse_args()

    if args.demo:
        trends = DEMO_DATA
    elif args.input:
        trends = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        parser.error("請提供 --input <file> 或 --demo")
        return

    ranked = rank(trends)

    if args.json:
        for t in ranked:
            t["tier"] = tier_of(t["score"])
        print(json.dumps(ranked, ensure_ascii=False, indent=2))
    else:
        print_table(ranked)


if __name__ == "__main__":
    main()
