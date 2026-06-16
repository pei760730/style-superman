#!/usr/bin/env python3
"""
generate_flash.py
=================
⚡ Style 速報：白名單硬資訊源 × 純機械抽取（零 LLM，守 D5）。

定位（D19，2026-06-16）：手機可獨立觸發的「速報層」——回答「今天有什麼上了/漲了/併了」，
帶 RSS summary 內現成的 SKU / 價格 / 發售日。**不做趨勢判讀、不挖 picks、不下熱度結論**
（那是 opus 對話深度版的活）。因為只做機械抽取、不讓 LLM 假裝判讀，
不會退化成 D16 砍掉的「空殼 roundup」。

挑源邏輯：只收「標題即資訊」的發售 / 新品 / 併購 / 漲價硬源（WHITELIST），
排除需要逐篇判讀的 roundup / editorial / clickbait（那些留桌面深度版）。

用法：
    python scripts/generate_flash.py                                   # 收 RSS → stdout
    python scripts/generate_flash.py --date 2026-06-16 --out reports/flash/2026-06-16.md
    python scripts/generate_flash.py --signals-in raw.yml --out /tmp/flash.md   # 讀現成 signals（離線/測試）
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
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

# 白名單 = summary 結構化、標題非 clickbait 的硬資訊源（發售 / 新品 / 併購 / 漲價）。
# 不在此清單的（highsnobiety / gq-* / esquire / blackbird / popeye / mens-nonno /
# reddit / w-vogue-dazed-korea）需要 LLM 挖 picks / 判讀，留給對話深度版。
WHITELIST = {
    "hypebeast", "hypebeast-jp", "hypebeast-kr", "sneakernews",
    "wwd", "fashionsnap", "senken", "fratello-watches", "monochrome-watches",
}

# 排除 roundup / 評論 / clickbait 標題（需 LLM 挖 picks，留深度版）。
ROUNDUP_RE = re.compile(
    r"(best|guide|\bvs\b|showdown|picks|every |how to|why |these |roundup|"
    r"추천|선정|\d+\s*選|ベスト|特集|名品|リスト|厳選|セレク|まとめ)",
    re.I,
)
# 排除非時尚雜訊（hypebeast 常混入體育 / 科技 / 汽車 / 電影 / 訃聞 / 金融）。
NOISE_RE = re.compile(
    r"(\bnba\b|\bbmw\b|\bdji\b|spacex|\bipo\b|patent|sues|box office|"
    r"\bfilm\b|movie|映画|興収|逝去|passed away|타계|le mans|auction|"
    r"trillionaire|트릴리어네어|결승전|파이널|球迷)",
    re.I,
)

REGION_NAME = {"global": "🌐 全球", "jp": "🇯🇵 日本", "kr": "🇰🇷 韓國", "us-eu": "🇺🇸🇪🇺 歐美"}
REGION_ORDER = ["global", "jp", "kr", "us-eu"]
MAX_PER_REGION = 12


def _slug(url: str) -> str:
    """取 URL 末段 path 當跨語言去重 key（hypebeast .com / .kr 同新聞 slug 相同）。"""
    path = re.sub(r"[?#].*$", "", url or "").rstrip("/")
    return path.rsplit("/", 1)[-1].lower()


def _clip(summary: str, limit: int = 110) -> str:
    """summary 抽前 limit 字（硬資訊通常在開頭）；去掉 reddit 尾綴雜訊。"""
    s = re.sub(r"\s+", " ", summary or "").strip()
    s = re.sub(r"(submitted by|&#32;|\[link\]|\[comments\]).*$", "", s).strip()
    return s[:limit] + ("…" if len(s) > limit else "")


def _recent_window(date_str: str, days: int = 2) -> set[str]:
    """回傳 [date_str-(days-1), date_str] 的日期字串集合（含今天往前 days 天）。"""
    try:
        end = dt.date.fromisoformat(date_str)
    except ValueError:
        return {date_str}
    return {(end - dt.timedelta(days=i)).isoformat() for i in range(max(days, 1))}


def extract(signals: list[dict], date_str: str, days: int = 2) -> str:
    """純機械抽取（不碰網路，可離線測）：白名單 × 非 roundup × 非 noise × 近 N 天 × 去重。"""
    recent = _recent_window(date_str, days)
    lines = [
        f"# ⚡ Style 速報 — {date_str}",
        "",
        "> 白名單硬資訊源 × 純機械抽取（零 LLM）：今天有什麼上了 / 漲了 / 併了，"
        "帶 SKU / 價格 / 發售日。趨勢判讀 + picks 看對話深度版。",
        "> 同一事件可能在各區各出一次（跨語言）；標題帶一點雜訊屬正常（速報定位，掃一眼可略）。",
    ]
    total = 0
    for region in REGION_ORDER:
        # 去重只在「同區內」（防同區 RSS 重複條目）；跨區同事件保留，讓每區完整——
        # 全域去重會把韓 / 日的本地發售被全球同 slug 吃光、整區只剩漏網雜訊。
        seen: set[str] = set()
        rows: list[dict] = []
        for s in signals:
            if s.get("region") != region or s.get("source_id") not in WHITELIST:
                continue
            if str(s.get("published")) not in recent:
                continue
            title = (s.get("title") or "").strip()
            if not title or ROUNDUP_RE.search(title) or NOISE_RE.search(title):
                continue
            key = _slug(s.get("url", "")) or title.lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append(s)
        if not rows:
            continue
        rows = rows[:MAX_PER_REGION]
        lines.append("")
        lines.append(f"## {REGION_NAME[region]}（{len(rows)} 則）")
        lines.append("")
        for s in rows:
            total += 1
            lines.append(f"- **[{s['title'].strip()}]({s.get('url', '')})**")
            summ = _clip(s.get("summary", ""))
            if summ:
                lines.append(f"  {summ}")
    if total == 0:
        lines += ["", "_今日白名單源無符合速報條件的硬訊號（可能非發售日 / 全是 roundup）。_"]
    return "\n".join(lines) + "\n"


def _collect_live() -> list[dict]:
    """連網收集（複用 collect_raw_signals，不另寫抓取）。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import collect_raw_signals as crs

    signals, warnings = crs.collect(crs.rss_sources())
    for w in warnings:
        print(f"⚠️  {w}", file=sys.stderr)
    return signals


def _load_signals(path: str) -> list[dict]:
    if yaml is None:
        sys.exit("⚠️  需要 pyyaml：pip install pyyaml")
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return data.get("signals", [])


def main() -> None:
    parser = argparse.ArgumentParser(description="⚡ Style 速報：白名單硬資訊源純機械抽取（零 LLM）")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD，預設今天")
    parser.add_argument("--out", default=None, help="輸出 .md 路徑；省略則印到 stdout")
    parser.add_argument("--signals-in", default=None,
                        help="讀現成 raw_signal_pack（YAML）而非連網收集——離線 / 測試用")
    parser.add_argument("--days", type=int, default=2, help="收近幾天（含今天），預設 2")
    args = parser.parse_args()

    if args.date:  # 壞 --date 會被直接寫進報告標題與檔名
        try:
            dt.date.fromisoformat(args.date)
        except ValueError:
            parser.error(f"--date 須為合法 YYYY-MM-DD（收到 {args.date!r}）")
    date_str = args.date or dt.date.today().isoformat()
    signals = _load_signals(args.signals_in) if args.signals_in else _collect_live()
    md = extract(signals, date_str, args.days)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"✅ 速報已產出 → {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
