#!/usr/bin/env python3
"""
collect_raw_signals.py
======================
從 data/sources.yml 中「有 RSS」的來源收集當日 / 近期文章，
轉成符合 templates/raw_signal_pack_template.md 的 raw_signal_pack。

C6 範圍：**只做「來源事實收集 + 格式化」**——
不做 trend scoring、不判 headline、不呼叫 LLM。
需要判斷的欄位（signal_type / credibility）一律留 `待查`，
交給 prompts/article_to_insight.md（AI / 人工）後續補。

設計：
- 純標準庫（urllib + xml.etree + email.utils），不加 feedparser 依賴。
- 抓取與解析**分離**：parse_feed() 吃字串、不碰網路 → 可離線測試。
- 抓取失敗（無網路 / 逾時 / 404）**優雅降級**：跳過該來源並記 warning，不中斷。

用法：
    python scripts/collect_raw_signals.py                      # 收集 → stdout（YAML）
    python scripts/collect_raw_signals.py --out /tmp/raw.yml   # 寫檔
    python scripts/collect_raw_signals.py --limit 5            # 每來源最多 5 則
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources.yml"

UA = "Mozilla/5.0 (compatible; StyleSupermanBot/0.1; +https://github.com/pei760730/style-superman)"
DEFAULT_LIMIT = 10
ATOM = "{http://www.w3.org/2005/Atom}"


def rss_sources() -> list[dict]:
    """回傳 sources.yml 中 rss 非空的來源。"""
    if yaml is None:
        sys.exit("⚠️  需要 pyyaml：pip install -r requirements.txt")
    data = yaml.safe_load(SOURCES.read_text(encoding="utf-8")) or {}
    return [s for s in data.get("sources", []) if s.get("rss")]


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def _clean(text: str, limit: int = 280) -> str:
    """去 HTML 標籤、壓空白、截斷——summary 只留事實摘要。"""
    import re

    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _norm_date(raw: str) -> str:
    """把 RSS(RFC822) / Atom(ISO) 日期轉成 YYYY-MM-DD；失敗回 待查。"""
    raw = (raw or "").strip()
    if not raw:
        return "待查"
    try:  # RFC822, e.g. "Wed, 04 Jun 2026 10:00:00 +0000"
        return parsedate_to_datetime(raw).date().isoformat()
    except (TypeError, ValueError):
        pass
    # ISO 8601, e.g. "2026-06-04T10:00:00Z"
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[:10]
    return "待查"


def parse_feed(xml_text: str, source: dict, limit: int = DEFAULT_LIMIT) -> list[dict]:
    """把 feed 字串解析成 raw signals（不碰網路，可離線測試）。支援 RSS 2.0 與 Atom。"""
    signals: list[dict] = []
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError:
        return signals

    # RSS 2.0: <rss><channel><item>...；Atom: <feed><entry>...
    items = root.findall(".//item")
    is_atom = False
    if not items:
        items = root.findall(f".//{ATOM}entry")
        is_atom = True

    for item in items[:limit]:
        if is_atom:
            title = _text(item.find(f"{ATOM}title"))
            link_el = item.find(f"{ATOM}link")
            link = (link_el.get("href") if link_el is not None else "") or ""
            published = _norm_date(_text(item.find(f"{ATOM}updated")) or _text(item.find(f"{ATOM}published")))
            summary = _clean(_text(item.find(f"{ATOM}summary")) or _text(item.find(f"{ATOM}content")))
        else:
            title = _text(item.find("title"))
            link = _text(item.find("link"))
            published = _norm_date(_text(item.find("pubDate")))
            summary = _clean(_text(item.find("description")))

        if not (title or link):
            continue
        signals.append({
            "source_id": source.get("id"),
            "source_tier": source.get("tier"),
            "region": source.get("region"),
            "url": link,
            "title": title,
            "published": published,
            "summary": summary,
            # 需判斷的欄位留待查，交給 prompts/article_to_insight.md
            "signal_type": "待查",
            "credibility": "待查",
        })
    return signals


def fetch_feed(url: str, timeout: int = 15) -> str | None:
    """抓 feed；失敗回 None（不丟例外）。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001 — 任何網路/解碼錯誤都降級
        return None


def collect(sources: list[dict], limit: int = DEFAULT_LIMIT, fetcher=fetch_feed) -> tuple[list[dict], list[str]]:
    """對每個來源 fetch+parse；回傳 (signals, warnings)。fetcher 可注入以便測試。"""
    signals: list[dict] = []
    warnings: list[str] = []
    for s in sources:
        xml_text = fetcher(s["rss"])
        if xml_text is None:
            warnings.append(f"{s.get('id')}: 抓取失敗（跳過）")
            continue
        got = parse_feed(xml_text, s, limit)
        if not got:
            warnings.append(f"{s.get('id')}: 解析不到項目（跳過）")
        signals.extend(got)
    return signals, warnings


def to_yaml(signals: list[dict]) -> str:
    header = (
        "# raw_signal_pack — 由 collect_raw_signals.py 收集（事實層，未經趨勢判斷）\n"
        "# signal_type / credibility 為『待查』，交給 prompts/article_to_insight.md 補。\n"
        "# 此檔為中間產物，不入長期版控（見 templates/raw_signal_pack_template.md）。\n"
    )
    body = yaml.dump({"signals": signals}, sort_keys=False, allow_unicode=True)
    return header + body


def main() -> None:
    parser = argparse.ArgumentParser(description="從 RSS 來源收集 raw_signal_pack（事實層）")
    parser.add_argument("--out", help="輸出 YAML 檔；省略則印到 stdout")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="每來源最多收幾則")
    args = parser.parse_args()

    sources = rss_sources()
    signals, warnings = collect(sources, args.limit)

    out_yaml = to_yaml(signals)
    if args.out:
        Path(args.out).write_text(out_yaml, encoding="utf-8")
        print(f"✅ 收集 {len(signals)} 則訊號，來自 {len(sources)} 個 RSS 來源 → {args.out}")
    else:
        print(out_yaml)

    for w in warnings:
        print(f"⚠️  {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
