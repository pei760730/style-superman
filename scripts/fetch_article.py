#!/usr/bin/env python3
"""
fetch_article.py
================
把「單篇文章 URL」抓成純文字（標題 / 日期 / 正文），給寫 brief 的對話 agent 挖 picks、
補價格與型號用。**純機械抽取、零 LLM**（守 D5）——判讀、選材、寫稿全留在對話端。

為什麼有這支（D36，2026-07-28）：
  `data/sources.yml` 的 `body_fetchable` 這批旗標是 2026-06-14 用「WebFetch 視角」量出來的，
  卻被寫成「源的永久屬性」。2026-07-28 本機複驗七源：permanent-style / gq / esquire /
  drapers / bof / fratello 六源全部 200、正文與價格都拿得到（PS $3,800、GQ 亞麻襯衫
  $120/$90/$50…），只有 sneakernews 本機也 403（換 UA 亦然＝真站級封鎖）。
  403 是「誰在看」的陳述，不是「這個源可不可讀」——repo 已在 RSS 死活軸硬化過這條
  （#186 四次誤殺 → #193 視角感知分類，見 repo_health.check_source_liveness），
  本檔是把同一條原則套到「正文抓取軸」：brief 實際在本機跑（D30/D35），就用本機視角抓。

紅線：
  - 零 LLM（D5）：只做 HTTP + 去標籤 + 壓空白，不下任何判斷。
  - 不新增來源（D18）：網域不在 sources.yml 只印提醒、不擋——單次引用 ≠ 把它收進來源清單。
  - **本機專用**：Actions egress 對多源會 403（liveness 誤殺史），故不進 CI、不排程；
    受限環境（web / 手機）抓不到就回非 0，讓 agent 退 WebFetch / Firecrawl，別假裝有內文。

用法：
    python scripts/fetch_article.py <url>                  # 標題 + 日期 + 正文（截斷）
    python scripts/fetch_article.py <url> --max-chars 4000
    python scripts/fetch_article.py <url> --json           # 給程式接的結構化輸出

退出碼：0 成功／3 HTTP 錯誤（含 403＝本視角被拒）／4 連不上（逾時 / DNS / 解碼）／
        5 抓到了但正文過短（JS 殼或付費牆，別拿去當「讀過原文」的證據）。
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover — 只影響 D18 網域提醒，不影響抓取
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources.yml"

# UA 直接沿用 collect_raw_signals 的單一事實來源：#177（2026-07-03）已經證實「reader 等級
# 瀏覽器 UA」才是這些公開內容的正常消費方式，兩支腳本各自寫一份就是下一次漂移的種子
# （這次的假陰性正是「UA 改了、旗標沒複驗」造成的）。這是直接引用既有常數，
# 不是另建共用抽象層（D6 否決的是那種東西）。
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_raw_signals import UA  # 需先設好 sys.path 才能 import 同層腳本

DEFAULT_TIMEOUT = 25
DEFAULT_MAX_CHARS = 12000
MIN_BODY_CHARS = 200  # 低於此視為沒真的拿到正文（JS 殼 / 付費牆擋頁）

_BLOCK_TAGS = "script|style|noscript|svg|template|form|iframe"
_BREAK_TAGS = "p|br|div|li|tr|h1|h2|h3|h4|h5|h6|section|article|blockquote"


def fetch(url, timeout=DEFAULT_TIMEOUT):
    """抓 URL；回 (status, html)。HTTP 錯誤回 (code, "")、連不上回 (0, "")，不丟例外。"""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja,en;q=0.9,zh-TW;q=0.8,ko;q=0.7",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        code = e.code
        e.close()  # urlopen 拋錯時 with 沒進去，手動關掉 error response
        return code, ""
    except Exception:  # noqa: BLE001 — timeout / DNS / 解碼一律降級，交給呼叫端判斷
        return 0, ""


def _strip(raw):
    """拿掉整段不是內文的東西（腳本 / 樣式 / 內嵌 SVG…），連內容一起丟。"""
    return re.sub(rf"(?is)<({_BLOCK_TAGS})\b[^>]*>.*?</\1\s*>", " ", raw)


def main_region(raw):
    """取最像正文的區塊：<article> 最長者 > <main> > 整頁。純結構啟發、不判讀語意。"""
    articles = re.findall(r"(?is)<article\b[^>]*>(.*?)</article\s*>", raw)
    if articles:
        best = max(articles, key=len)
        if len(best) > 500:  # 太短通常是側欄的相關文章卡，不是本文
            return best
    main = re.search(r"(?is)<main\b[^>]*>(.*?)</main\s*>", raw)
    if main and len(main.group(1)) > 500:
        return main.group(1)
    return raw


def to_text(raw):
    """HTML → 純文字：先把段落級標籤換成換行（保留可讀的斷句），再去標籤、解實體、壓空白。"""
    text = _strip(raw)
    text = re.sub(rf"(?is)</?({_BREAK_TAGS})\b[^>]*>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n\s*\n\s*", "\n\n", text)  # 多空行壓成一個空行
    return "\n".join(line.strip() for line in text.split("\n")).strip()


def title_of(raw):
    """標題：og:title / <title> / 第一個 <h1> 取最長者。

    不直接信 og:title——permanent-style 的 og:title 是站名「Permanent Style」，
    真標題只在 <title> 與 <h1>（2026-07-28 實測）。取最長是機械且夠用的解法。
    """
    cands = []
    og = re.search(r'(?is)<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', raw)
    if og:
        cands.append(og.group(1))
    t = re.search(r"(?is)<title[^>]*>(.*?)</title\s*>", raw)
    if t:
        cands.append(t.group(1))
    h1 = re.search(r"(?is)<h1\b[^>]*>(.*?)</h1\s*>", raw)
    if h1:
        cands.append(re.sub(r"(?s)<[^>]+>", " ", h1.group(1)))
    cleaned = [re.sub(r"\s+", " ", html.unescape(c)).strip() for c in cands]
    return max(cleaned, key=len) if cleaned else ""


def published_of(raw):
    """發佈日 → YYYY-MM-DD；抓不到回「待查」（同 collect_raw_signals 的誠實慣例）。"""
    for pat in (
        r'(?is)<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\'](\d{4}-\d{2}-\d{2})',
        r'(?is)<meta[^>]+name=["\'](?:date|pubdate|publish-date)["\'][^>]+content=["\'](\d{4}-\d{2}-\d{2})',
        r'(?is)<time[^>]+datetime=["\'](\d{4}-\d{2}-\d{2})',
        r'(?is)"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})',
    ):
        m = re.search(pat, raw)
        if m:
            return m.group(1)
    return "待查"


def known_domains():
    """sources.yml 既有來源的網域集合（D18 提醒用；缺 pyyaml 就回空集合、不影響抓取）。"""
    if yaml is None or not SOURCES.exists():
        return set()
    data = yaml.safe_load(SOURCES.read_text(encoding="utf-8")) or {}
    hosts = set()
    for s in data.get("sources", []):
        for key in ("url", "rss"):
            m = re.match(r"https?://([^/]+)", s.get(key) or "")
            if m:
                # 用 re.sub 不用 lstrip("www.")：lstrip 吃的是「字元集合」，
                # 會把 wwd.com 啃成 d.com（同類陷阱：wwdjapan.com、wwdkorea.com）。
                hosts.add(re.sub(r"^www\.", "", m.group(1).lower()))
    return hosts


def article(url, timeout=DEFAULT_TIMEOUT, max_chars=DEFAULT_MAX_CHARS, fetcher=fetch):
    """抓一篇 → dict（fetcher 可注入以便離線測試）。status/ok 一併回報，不吞失敗。"""
    status, raw = fetcher(url, timeout)
    out = {"url": url, "status": status, "title": "", "published": "待查",
           "chars": 0, "words": 0, "text": "", "ok": False}
    if not raw:
        return out
    body = to_text(main_region(raw))[:max_chars]
    out.update({
        "title": title_of(raw),
        "published": published_of(raw),
        "chars": len(body),
        "words": len(body.split()),
        "text": body,
        "ok": len(body) >= MIN_BODY_CHARS,
    })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="抓單篇文章正文（本機視角、純機械、零 LLM）。判讀留給對話 agent。"
    )
    ap.add_argument("url", help="文章網址（http/https）")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"逾時秒數（預設 {DEFAULT_TIMEOUT}）")
    ap.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS,
                    help=f"正文最多輸出幾字（預設 {DEFAULT_MAX_CHARS}）")
    ap.add_argument("--json", action="store_true", help="輸出 JSON（給程式接）")
    args = ap.parse_args(argv)

    if not re.match(r"^https?://", args.url):
        ap.error("網址要以 http:// 或 https:// 開頭")

    host = re.sub(r"^www\.", "", (re.match(r"https?://([^/]+)", args.url).group(1)).lower())
    if host not in known_domains():
        print(f"ℹ️  {host} 不在 data/sources.yml：單次引用可以，但**不代表收進來源清單**（D18 加來源要拍板）",
              file=sys.stderr)

    res = article(args.url, timeout=args.timeout, max_chars=args.max_chars)

    if res["status"] == 0:
        print(f"⚠️  連不上（逾時 / DNS / 解碼失敗）：{args.url}", file=sys.stderr)
        return 4
    if res["status"] >= 400:
        hint = "＝本視角被拒，不是這個源不能讀；換視角或走 WebFetch / Firecrawl" if res["status"] == 403 else ""
        print(f"⚠️  HTTP {res['status']}{hint}：{args.url}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"# {res['title'] or '（無標題）'}")
        print(f"<{res['url']}>　·　{res['published']}　·　{res['words']} words / {res['chars']} chars\n")
        print(res["text"])

    if not res["ok"]:
        print(f"⚠️  正文只有 {res['chars']} 字元（JS 殼或付費牆？）——不足以當「讀過原文」的證據，"
              "別據此寫推薦（證據門檻，見 prompts/daily_trend_brief.md）", file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
