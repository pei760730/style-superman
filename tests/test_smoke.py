#!/usr/bin/env python3
"""
test_smoke.py — 核心腳本的最小穩定驗收（C5）

不依賴 pytest，直接 `python tests/test_smoke.py` 就能跑（CI 也跑這支）。
每個 case 跑一條真實指令，斷言 exit code 與輸出，避免後續自動化一改就壞。

涵蓋：
- validate_repo（契約）
- track_rankings --json
- generate_daily_brief --draft（產後即刪）
- generate_monthly_heat_report --draft（產後即刪）
- ingest_ranking_snapshot dry-run：合法 fixture 通過、壞資料被擋
- RSS 離線解析 + 降級
- repo_health --consistency（文件↔程式碼一致性）
- 反向探針：決策守衛抓違規識別字、產出契約（daily / monthly）抓舊世界觀格式（探針檔產後即刪）
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
FIX = ROOT / "tests" / "fixtures"

_passed = 0
_failed = 0


def run(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, *args], cwd=ROOT, input=stdin, capture_output=True, text=True, encoding="utf-8"
    )


def check(name: str, cond: bool, detail: str = "") -> None:
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"✅ {name}")
    else:
        _failed += 1
        print(f"❌ {name}  {detail}")


def main() -> int:
    # 1. validate_repo 全綠
    r = run(["scripts/validate_repo.py"])
    check("validate_repo exit 0", r.returncode == 0, r.stdout + r.stderr)

    # 2. track_rankings json — 不只「長得像 JSON」，要真的可解析且含 lyst 榜結構
    import json as _json

    r = run(["scripts/track_rankings.py", "--json"])
    try:
        rankings = _json.loads(r.stdout)
    except _json.JSONDecodeError:
        rankings = None
    ok_rank = (
        r.returncode == 0
        and isinstance(rankings, dict)
        and "lyst" in rankings
        and rankings["lyst"].get("period")
        and isinstance(rankings["lyst"].get("brands"), list)
        and len(rankings["lyst"]["brands"]) > 0
    )
    check("track_rankings --json 結構可解析", ok_rank, r.stdout[:120])

    # 4. daily brief draft（產後刪）
    draft = ROOT / "reports" / "daily" / "2099-01-01.draft.md"
    r = run(["scripts/generate_daily_brief.py", "--date", "2099-01-01", "--draft"])
    check("generate_daily_brief --draft", r.returncode == 0 and draft.exists(), r.stderr)
    draft.unlink(missing_ok=True)

    # 5. monthly heat report draft（產後刪）
    mdraft = ROOT / "reports" / "monthly" / "2099-01-eu.draft.md"
    r = run(["scripts/generate_monthly_heat_report.py", "--month", "2099-01", "--draft"])
    check("generate_monthly_heat_report --draft", r.returncode == 0 and mdraft.exists(), r.stderr)
    mdraft.unlink(missing_ok=True)

    # 5b. monthly heat report 日本線（--region jp → -jp 後綴、標題帶地區名；產後刪）
    jdraft = ROOT / "reports" / "monthly" / "2099-01-jp.draft.md"
    r = run(["scripts/generate_monthly_heat_report.py", "--month", "2099-01", "--region", "jp", "--draft"])
    ok = r.returncode == 0 and jdraft.exists() and "日本男裝" in jdraft.read_text(encoding="utf-8")
    check("generate_monthly_heat_report --region jp", ok, r.stderr)
    jdraft.unlink(missing_ok=True)

    # 6. ingest dry-run：合法 fixture 應通過（exit 0，不寫檔）
    r = run(["scripts/ingest_ranking_snapshot.py", "--source", "lyst", "--input", str(FIX / "lyst_snapshot.yml")])
    check("ingest dry-run 合法 fixture 通過", r.returncode == 0 and "DRY RUN" in r.stdout, r.stderr)

    # 7. ingest dry-run：壞資料（重複 rank）應被擋（exit 1）
    bad = '- period: "2099-Q9"\n  brands: [{rank: 1, name: A},{rank: 1, name: B}]\n  products: [{rank: 1, brand: A, item: Y}]\n'
    r = run(["scripts/ingest_ranking_snapshot.py", "--source", "lyst"], stdin=bad)
    check("ingest dry-run 壞資料被擋", r.returncode == 1 and "重複 rank" in r.stdout, r.stdout + r.stderr)

    # 8–9. RSS 收集（離線：用 fixture，不碰網路）
    sys.path.insert(0, str(ROOT / "scripts"))
    import collect_raw_signals as crs  # noqa: E402

    feed_xml = (FIX / "sample_feed.xml").read_text(encoding="utf-8")
    src = {"id": "test-src", "tier": 2, "region": "us-eu", "rss": "x"}
    sigs = crs.parse_feed(feed_xml, src)
    ok_parse = (
        len(sigs) == 2
        and sigs[0]["source_id"] == "test-src"
        and sigs[0]["published"] == "2026-06-04"      # RFC822 → YYYY-MM-DD
        and sigs[0]["signal_type"] == "待查"           # 收集層不判斷
        and "<" not in sigs[0]["summary"]              # HTML 已清掉
    )
    check("RSS parse_feed 離線解析", ok_parse, str(sigs[:1]))

    # collect() 注入假 fetcher：抓取失敗應降級成 warning，不丟例外
    sigs2, warns = crs.collect([src, {"id": "dead", "tier": 3, "region": "jp", "rss": "y"}],
                               fetcher=lambda url: feed_xml if url == "x" else None)
    check("RSS collect 注入 fetcher + 降級", len(sigs2) == 2 and len(warns) == 1, f"{len(sigs2)} sigs, {warns}")

    # 9a. 社群來源 spam 過濾：盜播類標題被濾掉且記 warning；正常貼文不受影響
    spam_feed = feed_xml.replace(
        "</channel>",
        "<item><title>WATCH Fight Night FREE online HD stream</title>"
        "<link>http://spam.example</link></item></channel>",
    )
    community = {"id": "test-reddit", "tier": 3, "region": "global", "type": "community", "rss": "x"}
    sigs3, warns3 = crs.collect([community], fetcher=lambda url: spam_feed)
    ok_spam = (
        len(sigs3) == 2                                   # 原 2 則正常保留
        and any("spam" in w for w in warns3)              # 濾掉的有報出來（不靜默）
        and not crs.is_spam("AURALEE indigo denim review")  # 正常標題不誤殺
    )
    check("社群來源 spam 過濾 + 不誤殺", ok_spam, f"{len(sigs3)} sigs, {warns3}")

    # 9c. 未宣告 namespace 的 feed（出版方 bug，如 vogue.co.kr 的 media:）：fallback 補宣告後照常解析
    unbound_feed = feed_xml.replace(
        "</title>", "</title><media:thumbnail url='http://img.example/x.jpg'/>", 1
    )
    sigs4 = crs.parse_feed(unbound_feed, src)
    check("RSS unbound prefix fallback", len(sigs4) == 2, str(sigs4[:1]))
    check("RSS 真壞 XML 仍降級回空", crs.parse_feed("<rss><channel><item>", src) == [], "")

    # 9d. flash 速報：純機械抽取（離線，import 直接呼叫 extract，不碰網路）
    import generate_flash as gf  # noqa: E402

    flash_sigs = [
        {"source_id": "hypebeast", "region": "global", "published": "2026-06-16",
         "url": "https://hypebeast.com/2026/6/adidas-samba-mule", "title": "adidas Samba Mule Drops",
         "summary": "Name: adidas Samba Mule SKU: HP5054 Release Date: Fall 2026"},   # 硬訊號 → 留
        {"source_id": "hypebeast", "region": "global", "published": "2026-06-16",
         "url": "https://x/2", "title": "The 11 Best Sneakers Right Now", "summary": "x"},  # roundup → 剔
        {"source_id": "hypebeast", "region": "global", "published": "2026-06-16",
         "url": "https://x/3", "title": "2026 NBA Finals Recap", "summary": "x"},          # noise → 剔
        {"source_id": "gq-style", "region": "us-eu", "published": "2026-06-16",
         "url": "https://x/4", "title": "New Suede Loafer", "summary": "x"},               # 白名單外 → 剔
        {"source_id": "hypebeast", "region": "global", "published": "2026-06-01",
         "url": "https://x/5", "title": "Stale Drop", "summary": "x"},                     # 過期 → 剔
    ]
    md = gf.extract(flash_sigs, "2026-06-16")
    ok_flash = (
        "Samba Mule" in md and "HP5054" in md         # 白名單硬訊號 + summary 事實帶出
        and "11 Best" not in md                        # roundup 標題剔除
        and "NBA Finals" not in md                     # noise 標題剔除
        and "Suede Loafer" not in md                   # 白名單外源剔除
        and "Stale Drop" not in md                     # 過期剔除
    )
    check("flash 速報機械抽取（白名單×去 roundup×去 noise×近期）", ok_flash, md[:200])

    # 9b. 週挑骨架（draft 模式，不污染版控）
    r = run(["scripts/generate_weekly_buy_picks.py", "--date", "2099-01-07", "--draft"])
    draft = ROOT / "reports" / "buy_shortlist" / "2099-W02.draft.md"
    check("generate_weekly_buy_picks --draft", r.returncode == 0 and draft.exists(),
          r.stdout + r.stderr)
    if draft.exists():
        text = draft.read_text(encoding="utf-8")
        check("週挑骨架含 5 區與週期", "2099-W02" in text and "🧢 頭部" in text and "👟 足部" in text and "👜 配件" in text,
              text[:200])
        draft.unlink()

    # 10. repo_health 一致性檢查全綠（文件↔程式碼沒有漂移；新鮮度 WARN 不在此擋）
    r = run(["scripts/repo_health.py", "--consistency"])
    check("repo_health --consistency exit 0", r.returncode == 0, r.stdout + r.stderr)

    # 11. 決策守衛反向測試：違規識別字寫進活文件必須被抓（exit 1 且訊息點名守衛）
    violating = ROOT / "scripts" / "_guard_smoke_probe.py"
    # 探針識別字拆開組裝，避免本測試檔自己觸發守衛
    violating.write_text("# probe: " + "content_" + "ideas" + "\n", encoding="utf-8")
    try:
        r = run(["scripts/repo_health.py", "--consistency"])
        check("決策守衛抓到違規識別字", r.returncode == 1 and "決策守衛" in r.stdout,
              r.stdout + r.stderr)
    finally:
        violating.unlink()

    # 12. 產出契約反向測試：重定位後的 daily / monthly 用舊世界觀格式必須被抓（WARN，--strict 才 exit 1）
    bad_daily = ROOT / "reports" / "daily" / "2099-12-31.md"
    bad_daily.write_text("# Style Superman — Daily Brief · 2099-12-31\n\n- **對創作者的意義：** probe\n",
                         encoding="utf-8")
    bad_monthly = ROOT / "reports" / "monthly" / "2099-12-eu.md"
    bad_monthly.write_text("# 月報 probe\n\n## 🎬 可拍選題（2–3 條）\n", encoding="utf-8")
    # 空轉殭屍探針：日期已過、有必有段落、但殘留 {{}} 佔位 = 只產殼沒填內容
    hollow = ROOT / "reports" / "daily" / "2026-06-06.md"
    hollow_existed = hollow.exists()
    if not hollow_existed:
        hollow.write_text("# probe\n\n## 🎯 對我最相關 For Me\n- {{hot_item}}\n", encoding="utf-8")
    try:
        r = run(["scripts/repo_health.py", "--strict"])
        check("產出契約抓到舊世界觀格式（daily + monthly）",
              r.returncode == 1
              and "daily/2099-12-31.md 不符現行產出契約" in r.stdout
              and "monthly/2099-12-eu.md 不符現行產出契約" in r.stdout,
              r.stdout + r.stderr)
        if not hollow_existed:
            check("產出契約抓到空轉殭屍（骨架未填）",
                  "daily/2026-06-06.md 不符現行產出契約" in r.stdout and "骨架未填內容" in r.stdout,
                  r.stdout)
    finally:
        bad_daily.unlink()
        bad_monthly.unlink()
        if not hollow_existed:
            hollow.unlink()

    print(f"\n{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
