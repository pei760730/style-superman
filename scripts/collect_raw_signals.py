#!/usr/bin/env python3
"""
collect_raw_signals.py
======================
從 data/sources.yml 中「有 RSS」的來源收集當日 / 近期文章，
轉成符合 templates/raw_signal_pack_template.md 的 raw_signal_pack。

C6 範圍：**只做「來源事實收集 + 格式化」**——
不做 trend scoring、不判 headline、不呼叫 LLM。
需要判斷的欄位（signal_type / credibility）一律留 `待查`，
交給寫 brief 的主編 agent 後續判讀。

設計：
- 純標準庫（urllib + xml.etree + email.utils + concurrent.futures），不加 feedparser 依賴。
- 抓取與解析**分離**：parse_feed() 吃字串、不碰網路 → 可離線測試。
- 抓取**平行**、解析/歸併**序列照來源順序**：30+ 源每源最高 15s timeout，序列版 wall-clock 是
  所有 fetch 的總和（慢源線性累加）；改用 ThreadPoolExecutor 只平行「抓」（網路 I/O bound、
  urlopen 釋放 GIL），解析與歸併仍照來源順序做 → 輸出與序列版**逐位相同**（可重現、diff 穩定）。
- 抓取失敗（無網路 / 逾時 / 404）**優雅降級**：跳過該來源並記 warning，不中斷。

用法：
    python scripts/collect_raw_signals.py                      # 收集 → stdout（YAML）
    python scripts/collect_raw_signals.py --out /tmp/raw.yml   # 寫檔
    python scripts/collect_raw_signals.py --limit 5            # 每來源最多 5 則
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources.yml"

# 2026-07-03:自報身分的 bot UA(StyleSupermanBot/0.1)被三個源擋 —— bof 回 403、
# heddels / permanent-style 回空 200(WAF 對不明 bot 餵空)。同 URL 換瀏覽器 UA 實測
# 三源全回完整 RSS(bof 120KB / heddels 18KB / permanent-style 394KB)。這些是公開
# 訂閱用 feed,用一般 reader 等級的 UA 屬正常消費;三源曾被 liveness 誤判「死源」
# 差點被 D17 撤掉 —— 死的是 UA,不是源。
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
DEFAULT_LIMIT = 25  # 每來源最多收幾則（2026-06-14 由 10 提到 25：hypebeast 等高產源一天發 30+，10 上限丟掉 2/3、也壓低多樣性）
ATOM = "{http://www.w3.org/2005/Atom}"

# 社群來源（type: community）的標題層 spam 過濾。
# 背景：2026-06-10 brief 收集備註——reddit-techwear 被盜播 spam 灌版（8 則中 5 則）。
# 只攔「明顯非時尚」的盜播 / 導流模式，寧可漏放給主編 agent 判斷，不誤殺正常貼文；
# 濾掉幾則一律記 warning（不靜默，見 CLAUDE.md 誠實原則）。
SPAM_RE = re.compile(
    r"(?i)"
    r"(\b(?:watch|stream(?:ing)?)\b.{0,40}\b(?:free|online|live|hd|1080p?|720p)\b"
    r"|\bfull\s?(?:movie|episode|match|fight|game)\b"
    r"|\b(?:s\d{1,2}\s?e\d{1,3})\b"
    r"|\bt\.me/|\btelegram\b"
    r"|\bcrack(?:ed)?\s?(?:apk|version)\b)"
)


def is_spam(title: str, summary: str = "") -> bool:
    """標題層 spam 判定（盜播 / 導流類）。語意級的離題判斷仍交主編 agent（讀 pack 時）。"""
    return bool(SPAM_RE.search(f"{title} {summary}"))


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
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)  # &amp; / &#39; / &nbsp; → 實字（feeds 常雙重編碼；先解碼再壓空白）
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


def _declare_unbound_prefixes(xml_text: str) -> str:
    """補上 feed 用了卻沒宣告的 XML namespace（出版方常見 bug，例：vogue.co.kr 的 media:）。

    只在根元素補宣告、不動內容；URI 是假的也無妨——本解析器不靠 namespace 取值。
    """
    root_match = re.search(r"<(rss|feed)\b[^>]*>", xml_text)
    if not root_match:
        return xml_text
    root_tag = root_match.group(0)
    declared = set(re.findall(r"xmlns:([\w.-]+)", root_tag))
    used = set(re.findall(r"<([\w.-]+):", xml_text)) | set(re.findall(r"\s([\w.-]+):[\w.-]+=", xml_text))
    missing = used - declared - {"xml", "xmlns"}
    if not missing:
        return xml_text
    extra = "".join(f' xmlns:{p}="urn:undeclared:{p}"' for p in sorted(missing))
    patched_root = root_tag[:-1] + extra + ">"
    return xml_text.replace(root_tag, patched_root, 1)


def parse_feed(xml_text: str, source: dict, limit: int = DEFAULT_LIMIT) -> list[dict]:
    """把 feed 字串解析成 raw signals（不碰網路，可離線測試）。支援 RSS 2.0 與 Atom。"""
    signals: list[dict] = []
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError:
        try:
            root = ET.fromstring(_declare_unbound_prefixes(xml_text.strip()))
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
            "title": html.unescape(title),  # 標題同樣可能雙重編碼（&amp; / &#39;）
            "published": published,
            "summary": summary,
            # 需判斷的欄位留待查，交給寫 brief 的主編 agent
            "signal_type": "待查",
            "credibility": "待查",
        })
    return signals


def fetch_feed(url: str, timeout: int = 15, sleep=time.sleep) -> str | None:
    """抓 feed；失敗回 None（不丟例外）。
    對 429（Too Many Requests）退避重試一次——reddit old 域對連續/bot 請求限速兇，
    批次跑 31 源時相鄰的 reddit 會被連打吃 429（2026-06-15 dogfood 抓到），單發退避後就過。
    sleep 可注入以便測試不真的等。"""
    for attempt in range(2):  # 最多 1 次重試
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            code = e.code
            e.close()  # urlopen 拋錯時 with 沒進去，先關掉 error response 再退避/返回
            if code == 429 and attempt == 0:
                sleep(3)  # 禮貌退避後再試一次
                continue
            return None
        except Exception:  # noqa: BLE001 — 任何網路/解碼錯誤都降級
            return None
    return None


def collect(
    sources: list[dict],
    limit: int = DEFAULT_LIMIT,
    fetcher=fetch_feed,
    max_workers: int = 8,
) -> tuple[list[dict], list[str]]:
    """對每個來源 fetch+parse；回傳 (signals, warnings)。fetcher 可注入以便測試。

    抓取平行（網路 I/O bound）、解析/歸併序列照 `sources` 順序——輸出與序列版逐位相同
    （可重現）。max_workers 上限刻意保守（預設 8）：相鄰同域請求（如 reddit）同時打易招
    429，fetch_feed 已有單次退避重試，配合小池子即可（見該函式註解）。
    """
    signals: list[dict] = []
    warnings: list[str] = []
    if not sources:
        return signals, warnings
    # 只平行「抓」：ThreadPoolExecutor.map 保序、且 fetch_feed 內部吞所有例外回 None（map 不會拋）。
    with ThreadPoolExecutor(max_workers=max(1, min(max_workers, len(sources)))) as ex:
        xml_texts = list(ex.map(lambda s: fetcher(s["rss"]), sources))
    for s, xml_text in zip(sources, xml_texts):
        if xml_text is None:
            warnings.append(f"{s.get('id')}: 抓取失敗（跳過）")
            continue
        got = parse_feed(xml_text, s, limit)
        if not got:
            warnings.append(f"{s.get('id')}: 解析不到項目（跳過）")
        if s.get("type") == "community":
            kept = [sig for sig in got if not is_spam(sig["title"], sig["summary"])]
            dropped = len(got) - len(kept)
            if dropped:
                warnings.append(f"{s.get('id')}: 標題層濾掉 {dropped} 則疑似 spam（盜播/導流）")
            got = kept
        signals.extend(got)
    return signals, warnings


def to_yaml(signals: list[dict]) -> str:
    header = (
        "# raw_signal_pack — 由 collect_raw_signals.py 收集（事實層，未經趨勢判斷）\n"
        "# signal_type / credibility 為『待查』，由寫 brief 的主編 agent 判讀。\n"
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
