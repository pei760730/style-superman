#!/usr/bin/env python3
"""
test_smoke.py — 核心腳本的最小穩定驗收（C5）

不依賴 pytest，直接 `python tests/test_smoke.py` 就能跑（CI 也跑這支）。
每個 case 跑一條真實指令，斷言 exit code 與輸出，避免後續自動化一改就壞。

涵蓋：
- validate_repo（契約）
- track_rankings.lyst_comparison_text（月報 🆚 段季對季比對；CLI/ingest 已 D21 移除）
- generate_daily_brief --draft（產後即刪）
- generate_monthly_heat_report --draft（產後即刪）
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
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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

    # 1b. D16 gate 回歸鎖：凍結線（2026-06-16）後的 daily 檔（非 draft）被 validate 擋下。
    #     根因＝平行 session 走 D16 前舊存檔習慣把整份 brief commit 進 reports/daily/（06-23~26 連犯，
    #     純文件規則擋不住）→ 硬化成 gate。擁有者要的是「讀、喜歡的自己記」，不存整份 brief。
    stray = ROOT / "reports" / "daily" / "2099-12-31.md"
    stray.write_text("# stray daily（測試用，產後即刪）\n", encoding="utf-8")
    try:
        r = run(["scripts/validate_repo.py"])
        check(
            "D16 gate 擋住凍結線後的 daily（非 draft）",
            r.returncode != 0 and "D16" in (r.stdout + r.stderr),
            r.stdout + r.stderr,
        )
    finally:
        stray.unlink(missing_ok=True)

    # 2. track_rankings 的 lyst_comparison_text（月報 🆚 段唯一在用的函式）見 9d 回歸鎖。
    #    （CLI / --json / ingest 已於 D21 移除——擁有者只走對話，無人工指令，見 docs/rankings.md）

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

    # 5c. 壞日期/月份反向：四支 generator 對非法輸入要非 0 退出、且不產垃圾封存檔（fail-open 缺口回歸鎖）
    #     附帶 stderr 編碼回歸鎖（2026-06-24）：argparse 的中文錯誤訊息走 stderr，腳本若只
    #     reconfigure stdout、漏了 stderr，本機 cp950 會吐亂碼／capture 時 UnicodeDecodeError。
    #     run() 用 encoding="utf-8" 收 stderr——這裡斷言收到的中文未被 cp950 弄壞（含 CJK、無替代字）。
    for _args, _bad in [
        (["scripts/generate_daily_brief.py", "--date", "NOT-A-DATE"], ROOT / "reports" / "daily" / "NOT-A-DATE.md"),
        (["scripts/generate_monthly_heat_report.py", "--month", "2026-13"], ROOT / "reports" / "monthly" / "2026-13-eu.md"),
        (["scripts/generate_weekly_buy_picks.py", "--date", "2026-13-40"], None),
        (["scripts/generate_flash.py", "--date", "NOT-A-DATE"], None),
    ]:
        r = run(_args)
        bad_made = bool(_bad and _bad.exists())
        _err = r.stderr or ""
        # 至少一個 CJK 字元（中文錯誤訊息有解碼正確）且無 U+FFFD 替代字（沒被 cp950 ↔ utf-8 互轉弄壞）
        _stderr_ok = any("一" <= ch <= "鿿" for ch in _err) and "�" not in _err
        check(f"壞日期被擋不產檔：{_args[0].split('/')[-1]}",
              r.returncode != 0 and not bad_made and _stderr_ok,
              f"rc={r.returncode} bad_made={bad_made} stderr_ok={_stderr_ok} stderr={_err[:80]!r}")
        if bad_made:
            _bad.unlink()  # 萬一驗證沒擋住，清掉避免污染

    # 6–7. （ingest_ranking_snapshot dry-run 測試已隨 D21 移除——存榜助手刪除，排行快照改由 AI 在對話直接編輯 yaml）

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

    # 8b. HTML entity 解碼：feeds 常雙重編碼（&amp;amp; / &amp;#39;），不該原樣漏進產出
    #     （flash _clip 裡的 &#32; strip 是這問題的 band-aid 症狀，根治在收集層 html.unescape）
    ent_feed = (
        "<rss><channel>"
        "<item><title>Nike &amp;amp; Tiffany&#39;s drop</title>"
        "<link>http://e.example/x</link>"
        "<description>&lt;p&gt;Rosa&amp;amp;Co. &amp;#8217;26&lt;/p&gt;</description>"
        "<pubDate>Wed, 04 Jun 2026 10:00:00 +0000</pubDate></item>"
        "</channel></rss>"
    )
    esig = crs.parse_feed(ent_feed, src)
    ok_ent = (
        len(esig) == 1
        and esig[0]["title"] == "Nike & Tiffany's drop"
        and "&amp;" not in esig[0]["summary"]
        and "&#" not in esig[0]["summary"]
    )
    check("RSS HTML entity 解碼（title+summary）", ok_ent, str(esig[:1]))

    # collect() 注入假 fetcher：抓取失敗應降級成 warning，不丟例外
    sigs2, warns = crs.collect([src, {"id": "dead", "tier": 3, "region": "jp", "rss": "y"}],
                               fetcher=lambda url: feed_xml if url == "x" else None)
    check("RSS collect 注入 fetcher + 降級", len(sigs2) == 2 and len(warns) == 1, f"{len(sigs2)} sigs, {warns}")

    # 9e. 平行 collect 保序回歸鎖（抓取已平行化；輸出仍須照 sources 順序、與「完成順序」無關）。
    #     讓越前面的源抓得越慢：若實作改用完成順序（如 as_completed）組裝，結果會反過來 → 被這鎖抓到。
    import time as _t
    _order_src = [{"id": f"src{i}", "tier": 2, "region": "global", "rss": str(i)} for i in range(5)]

    def _slow_fetch(url):
        _t.sleep(0.02 * (5 - int(url)))  # url "0" 最慢、"4" 最快
        return (f"<rss><channel><item><title>t{url}</title><link>http://e/{url}</link>"
                "<pubDate>Wed, 04 Jun 2026 10:00:00 +0000</pubDate></item></channel></rss>")

    _osigs, _ = crs.collect(_order_src, fetcher=_slow_fetch)
    check("平行 collect 仍照來源順序（不隨完成順序）",
          [s["source_id"] for s in _osigs] == [f"src{i}" for i in range(5)],
          [s["source_id"] for s in _osigs])

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

    # 9d. track_rankings.lyst_comparison_text 前季 partial 不可假「新進榜」（commit 5fee0bf 修的 bug，留回歸鎖）
    #     （月報 🆚 對照量化基準段唯一在用的函式；ingest/CLI 已於 D21 移除，見 docs/rankings.md）
    import track_rankings as _tr  # noqa: E402
    _cmp = _tr.lyst_comparison_text({"snapshots": [
        {"period": "2099-Q2", "brands": [{"rank": 1, "name": "A"}, {"rank": 2, "name": "NewBrand"}]},
        {"period": "2099-Q1", "coverage": "partial", "brands": [{"rank": 1, "name": "A"}]},
    ]}) or ""
    check("compare 前季 partial 不假新進榜", "無法判定" in _cmp and "🆕 新進榜" not in _cmp, _cmp[:200])

    # 9f. fetch_feed 對 429 退避重試一次（reddit 限速；sleep 可注入正是為了測，不真的等）
    import urllib.request as _ur
    import urllib.error as _ue
    import io as _io
    _calls = {"n": 0}

    class _FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"<rss><channel><item><title>X</title><link>http://x</link></item></channel></rss>"

    def _fake_open(req, timeout=15):
        _calls["n"] += 1
        if _calls["n"] == 1:
            raise _ue.HTTPError("http://x", 429, "Too Many Requests", {}, _io.BytesIO(b""))
        return _FakeResp()

    _orig = _ur.urlopen
    _ur.urlopen = _fake_open
    try:
        _xml = crs.fetch_feed("http://x", sleep=lambda s: None)
    finally:
        _ur.urlopen = _orig
    check("fetch_feed 429 退避重試成功", _xml is not None and _calls["n"] == 2, f"calls={_calls['n']}")

    # 9g. repo_health 來源死活檢查平行化保序回歸鎖（探測已平行；死源/限速清單須照 sources.yml 順序、
    #     與完成順序無關 → issue body 穩定可重現）。注入快樁 probe（不連網），讓越前面的源回得越慢。
    import repo_health as _rh  # noqa: E402
    _live_src = [{"id": f"L{i}", "rss": f"http://e/{i}"} for i in range(6)]
    _st = {0: ("ok", 200), 1: ("gone", 404), 2: ("ratelimited", 429),
           3: ("ok", 200), 4: ("blocked", 403), 5: ("ok", 200)}

    def _live_probe(url, timeout=15):
        i = int(url.rsplit("/", 1)[1])
        _t.sleep(0.02 * (6 - i))  # L0 最慢、L5 最快
        return _st[i]

    import yaml as _yl
    _orig_load = _yl.safe_load
    _yl.safe_load = lambda *a, **k: {"sources": _live_src}
    try:
        # retry_delay=0：關掉 D32 偽陽性退避的 sleep，讓保序測試快且確定（確定性 stub 的死源重打仍死）
        _lout = _rh.check_source_liveness(probe=_live_probe, retry_delay=0)
    finally:
        _yl.safe_load = _orig_load
    _ldetail = [f.message for f in _lout[1:]]
    _live_ok = (
        "3/6" in _lout[0].message                                    # 3 ok
        and len(_lout) == 4                                          # summary + L1/L2/L4
        and "L1" in _ldetail[0] and "L2" in _ldetail[1] and "L4" in _ldetail[2]  # 照來源順序
        and "死源候補" in _ldetail[0] and "疑遭阻擋" in _ldetail[2]  # gone→候補、blocked→視角阻擋（403 永不判死）
    )
    check("liveness 平行探測仍照來源順序（不隨完成順序）", _live_ok,
          [m[:24] for m in _ldetail])

    # 9g-2. D32 偽陽性退避回歸鎖：瞬斷源（首打 dead/empty/unreachable、重打就活）不該被誤報死源。
    #       每源給獨立計數，確認①失敗類第一次真的重打了 ②重打回 ok 就不進死源候補清單 ③429 不重打（自有退避）。
    _retry_calls = {"t": 0, "e": 0, "u": 0, "r": 0, "ok": 0}
    _retry_src = [{"id": "transient", "rss": "http://x/t"},   # gone→ok
                  {"id": "flap-empty", "rss": "http://x/e"},  # empty→ok
                  {"id": "flap-unreach", "rss": "http://x/u"},# unreachable→ok
                  {"id": "limited", "rss": "http://x/r"},     # 429（不重打）
                  {"id": "alive", "rss": "http://x/ok"}]      # ok（不重打）
    def _flaky_probe(url, timeout=15):
        k = url.rsplit("/", 1)[1]
        _retry_calls[k] += 1
        first = {"t": ("gone", 404), "e": ("empty", 200), "u": ("unreachable", 0),
                 "r": ("ratelimited", 429), "ok": ("ok", 200)}[k]
        # 失敗類第二次探測回活；429/ok 維持原狀
        if _retry_calls[k] >= 2 and k in ("t", "e", "u"):
            return ("ok", 200)
        return first
    _yl.safe_load = lambda *a, **k: {"sources": _retry_src}
    try:
        _rout = _rh.check_source_liveness(probe=_flaky_probe, retry_delay=0)
    finally:
        _yl.safe_load = _orig_load
    _rdetail = [f.message for f in _rout[1:]]
    _retry_ok = (
        "4/5" in _rout[0].message                              # t/e/u 重打回活 + alive = 4 ok
        and _retry_calls["t"] == 2 and _retry_calls["e"] == 2 and _retry_calls["u"] == 2  # 失敗類有重打
        and _retry_calls["r"] == 1 and _retry_calls["ok"] == 1                            # 429/ok 不重打
        and not any("死源候補：" in m for m in _rdetail)        # 沒有任何源被誤報死（「疑遭阻擋」「限速」不算死判定）
        and any("限速" in m for m in _rdetail)                 # 429 仍被標限速
    )
    check("liveness 瞬斷源重試回活不誤報死源（429/ok 不重打）", _retry_ok,
          {"summary": _rout[0].message[:40], "calls": _retry_calls})

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

    # 9h. validate_repo 缺 pyyaml 時要乾淨回報、不可崩 traceback（回歸鎖）。
    #     check_yaml_parseable 舊版寫死 `except yaml.YAMLError`：yaml 缺套件被設成 None 時，
    #     求值 None.YAMLError → AttributeError 蓋掉 load_yaml 丟的 RuntimeError、逃出 main() 的
    #     RuntimeError 處理，違反 CLAUDE.md「缺 pyyaml 明確回報」。注入 yaml=None 模擬缺套件，
    #     斷言只拿到 RuntimeError（main 會接住印 ⚠️），絕不是 AttributeError。
    import validate_repo as _vr  # noqa: E402
    _orig_yaml = _vr.yaml
    _vr.yaml = None
    try:
        _raised = None
        try:
            _vr.check_yaml_parseable(ROOT / "data" / "trend_history.yml")
        except BaseException as _e:  # noqa: BLE001 — 就是要分辨拿到哪種例外
            _raised = _e
        check("validate_repo 缺 pyyaml 乾淨上拋 RuntimeError（非 AttributeError）",
              isinstance(_raised, RuntimeError),
              f"raised={type(_raised).__name__ if _raised else None}")
    finally:
        _vr.yaml = _orig_yaml

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
