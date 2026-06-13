#!/usr/bin/env python3
"""
track_rankings.py
=================
讀取 data/rankings/ 的排行快照，顯示最新榜，並比對名次演化。

這支腳本是「對比」的核心：每季 / 每份報告新增一筆快照後，
它能算出品牌名次相對上一筆的升降（↑ / ↓ / new / out），
讓你看出趨勢往哪走，而不只是看單一時間點。

資料源：
    data/rankings/lyst-index.yml   歐美：Lyst Index（季度，最紅品牌+單品）
    data/rankings/stockx.yml       歐美：StockX（年度/年中，熱銷實數）
    data/rankings/mercari-jp.yml   日本：Mercari（二手成交需求）
    data/rankings/kream.yml        韓國：KREAM（限量/轉售成交量，韓版 StockX）
    data/rankings/musinsa.yml      韓國：MUSINSA（平台銷售榜，最大男裝電商）

用法：
    python scripts/track_rankings.py                 # 全部來源，最新榜
    python scripts/track_rankings.py --source lyst    # 只看 Lyst
    python scripts/track_rankings.py --source stockx  # 只看 StockX
    python scripts/track_rankings.py --region kr      # 只看韓國（KREAM + MUSINSA）
    python scripts/track_rankings.py --source lyst --compare   # 比對最新兩季名次
    python scripts/track_rankings.py --json           # 輸出 JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Windows 終端機預設 cp950，emoji / 中文會炸。強制 stdout 走 UTF-8。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
RANKINGS_DIR = ROOT / "data" / "rankings"

SOURCES = {
    "lyst": "lyst-index.yml",       # 歐美：季度威望榜
    "stockx": "stockx.yml",         # 歐美：轉售熱銷實數
    "mercari": "mercari-jp.yml",    # 日本：二手成交需求
    "kream": "kream.yml",           # 韓國：限量/轉售成交量（韓版 StockX）
    "musinsa": "musinsa.yml",       # 韓國：平台銷售榜（最大男裝電商）
}

# 顯示分組：依地區，方便 --source all 時排版
REGION_GROUPS = {
    "🇺🇸🇪🇺 歐美": ["lyst", "stockx"],
    "🇯🇵 日本": ["mercari"],
    "🇰🇷 韓國": ["kream", "musinsa"],
}

# --region 旗標 → REGION_GROUPS 鍵
REGION_KEYS = {
    "us-eu": "🇺🇸🇪🇺 歐美",
    "jp": "🇯🇵 日本",
    "kr": "🇰🇷 韓國",
}


def load(source_key: str) -> dict:
    if yaml is None:
        sys.exit("⚠️  需要 pyyaml：pip install pyyaml")
    path = RANKINGS_DIR / SOURCES[source_key]
    if not path.exists():
        sys.exit(f"⚠️  找不到快照檔：{path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def snapshots(data: dict) -> list[dict]:
    """快照清單，最新在前（檔案本就最新放最上）。"""
    return data.get("snapshots", [])


# ---------- 顯示：Lyst ----------

def show_lyst_latest(data: dict) -> None:
    snaps = snapshots(data)
    if not snaps:
        print("（Lyst 無快照）")
        return
    s = snaps[0]
    print(f"\n🏆  Lyst Index · {s.get('period')}（發布 {s.get('published')}）")
    if s.get("methodology"):
        print(f"    方法：{s['methodology']}")

    print("\n  最紅品牌 Top 20")
    print("  " + "-" * 40)
    for b in s.get("brands", []):
        print(f"  {b['rank']:>2}. {b['name']:<18} {fmt_move(b.get('move'))}")

    print("\n  最熱單品 Top 10")
    print("  " + "-" * 40)
    for p in s.get("products", []):
        note = f"  — {p['note']}" if p.get("note") else ""
        print(f"  {p['rank']:>2}. {p['brand']} · {p['item']}{note}")

    if s.get("menswear_focus"):
        print("\n  👔 男裝視角")
        for m in s["menswear_focus"]:
            print(f"     · {m}")
    print()


def fmt_move(move) -> str:
    """把 move 欄位轉成箭頭標示。"""
    if move in (None, "="):
        return "—"
    if move == "new":
        return "🆕 new"
    if move == "re-entry":
        return "↩ re-entry"
    if isinstance(move, int):
        if move > 0:
            return f"↑ +{move}"
        if move < 0:
            return f"↓ {move}"
    return str(move)


def lyst_comparison_text(data: dict, top: int | None = None) -> str | None:
    """比對最新兩季品牌名次（用我們自己的歷史，而非來源標示），回傳格式化字串。
    快照不足 2 筆回傳 None。top 限制顯示前 N 名（None＝全部）。供 CLI 與月報骨架共用。"""
    snaps = snapshots(data)
    if len(snaps) < 2:
        return None

    new, old = snaps[0], snaps[1]
    old_rank = {b["name"]: b["rank"] for b in old.get("brands", [])}
    lines = [f"📊  Lyst 品牌名次：{old.get('period')} → {new.get('period')}", "  " + "-" * 48]
    brands = new.get("brands", [])
    for b in brands[: top or len(brands)]:
        name, rank = b["name"], b["rank"]
        if name not in old_rank:
            change = "🆕 新進榜"
        else:
            diff = old_rank[name] - rank  # 名次變小 = 上升
            change = "— 持平" if diff == 0 else (f"↑ {diff}" if diff > 0 else f"↓ {abs(diff)}")
        lines.append(f"  {rank:>2}. {name:<18} {change}")

    dropped = [n for n in old_rank if n not in {b["name"] for b in brands}]
    if dropped:
        lines.append(f"\n  掉出榜外：{', '.join(dropped)}")
    return "\n".join(lines)


def compare_lyst(data: dict) -> None:
    """CLI：印出 Lyst 季對季名次比對（薄包裝 lyst_comparison_text）。"""
    text = lyst_comparison_text(data)
    if text is None:
        print("\n⚠️  只有 1 筆快照，還無法比對。等下一季新增後再 --compare。")
        print("    （目前先看來源標示的 move 欄位即可。）\n")
        return
    print("\n" + text + "\n")


# ---------- 顯示：StockX ----------

def show_stockx_latest(data: dict) -> None:
    snaps = snapshots(data)
    if not snaps:
        print("（StockX 無快照）")
        return
    s = snaps[0]
    print(f"\n👟  StockX · {s.get('period')}（{s.get('report', '')}）")

    def line(label, d):
        if d:
            note = f"  — {d['note']}" if d.get("note") else ""
            print(f"  {label:<10} {d['brand']} · {d['item']}{note}")

    print()
    line("最暢銷鞋", s.get("best_seller_sneaker"))
    line("服飾王", s.get("apparel_top"))
    line("配件王", s.get("accessory_top"))
    line("史上最暢銷", s.get("all_time_best_seller"))

    if s.get("fastest_growing_brands"):
        print("\n  📈 成長最快品牌")
        for b in s["fastest_growing_brands"]:
            print(f"     {b['brand']:<10} {b['change']}")

    if s.get("notable_new_models"):
        print("\n  🔑 年度最佳新款（各品牌）")
        for m in s["notable_new_models"]:
            note = f"  — {m['note']}" if m.get("note") else ""
            print(f"     {m['brand']} · {m['item']}{note}")

    if s.get("menswear_focus"):
        print("\n  👔 男裝視角")
        for m in s["menswear_focus"]:
            print(f"     · {m}")
    print()


# ---------- 顯示：Mercari ----------

def show_mercari_latest(data: dict) -> None:
    snaps = snapshots(data)
    if not snaps:
        print("（Mercari 無快照）")
        return
    s = snaps[0]
    print(f"\n♻  Mercari（二手成交）· {s.get('period')}（{s.get('report', '')}）")

    bt = s.get("brand_top")
    if bt:
        note = f"  — {bt['note']}" if bt.get("note") else ""
        print(f"\n  成交品牌 #1   {bt['name']}{note}")
    if s.get("cross_gen_brands"):
        print(f"  跨世代保值   {', '.join(s['cross_gen_brands'])}")
    if s.get("category_shift"):
        print("\n  品類結構變化")
        for c in s["category_shift"]:
            print(f"     · {c}")
    if s.get("menswear_read"):
        print("\n  👔 男裝視角")
        for m in s["menswear_read"]:
            print(f"     · {m}")
    print()


# ---------- 顯示：KREAM（韓國，限量/轉售成交） ----------

def show_kream_latest(data: dict) -> None:
    snaps = snapshots(data)
    if not snaps:
        print("（KREAM 無快照）")
        return
    s = snaps[0]
    print(f"\n💎  KREAM（限量/轉售成交）· {s.get('period')}（{s.get('report', '')}）")
    if s.get("methodology"):
        print(f"    方法：{s['methodology']}")

    bt = s.get("brand_top")
    if bt:
        note = f"  — {bt['note']}" if bt.get("note") else ""
        print(f"\n  成交品牌 #{bt.get('rank', 1)}   {bt['name']}{note}")
    if s.get("category_shift"):
        print("\n  平台/結構變化")
        for c in s["category_shift"]:
            print(f"     · {c}")
    if s.get("notable"):
        print("\n  🔑 高熱度標的")
        for n in s["notable"]:
            print(f"     · {n}")
    if s.get("menswear_read"):
        print("\n  👔 男裝視角")
        for m in s["menswear_read"]:
            print(f"     · {m}")
    print()


# ---------- 顯示：MUSINSA（韓國，平台銷售榜） ----------

def show_musinsa_latest(data: dict) -> None:
    snaps = snapshots(data)
    if not snaps:
        print("（MUSINSA 無快照）")
        return
    s = snaps[0]
    print(f"\n🛍  MUSINSA（무신사 銷售榜）· {s.get('period')}（{s.get('report', '')}）")
    if s.get("methodology"):
        print(f"    方法：{s['methodology']}")

    print("\n  銷售品牌榜")
    print("  " + "-" * 40)
    for b in s.get("brands", []):
        note = f"  — {b['note']}" if b.get("note") else ""
        print(f"  {b['rank']:>2}. {b['name']}{note}")

    if s.get("menswear_read"):
        print("\n  👔 男裝視角")
        for m in s["menswear_read"]:
            print(f"     · {m}")
    print()


# 來源 → 顯示函式對照
SHOW = {
    "lyst": show_lyst_latest,
    "stockx": show_stockx_latest,
    "mercari": show_mercari_latest,
    "kream": show_kream_latest,
    "musinsa": show_musinsa_latest,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="排行快照檢視與比對")
    parser.add_argument(
        "--source",
        choices=["lyst", "stockx", "mercari", "kream", "musinsa", "all"],
        default="all",
    )
    parser.add_argument("--region", choices=["us-eu", "jp", "kr"], help="只看某地區（覆蓋 --source）")
    parser.add_argument("--compare", action="store_true", help="比對最新兩季名次（目前僅 Lyst）")
    parser.add_argument("--json", action="store_true", help="輸出最新快照 JSON")
    args = parser.parse_args()

    if args.region:
        targets = REGION_GROUPS[REGION_KEYS[args.region]]
    elif args.source == "all":
        targets = list(SOURCES)
    else:
        targets = [args.source]

    if args.json:
        out = {k: (snapshots(load(k))[:1] or [None])[0] for k in targets}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    for key in targets:
        data = load(key)
        SHOW[key](data)
        if key == "lyst" and args.compare:
            compare_lyst(data)


if __name__ == "__main__":
    main()
