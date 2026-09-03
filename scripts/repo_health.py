#!/usr/bin/env python3
"""
repo_health.py
==============
Repo 自我健康檢查 — Self-Evolution Loop 的 Observe / Diagnose / Next Action 層。

validate_repo.py 檢查「格式契約」（YAML 欄位、template 段落）；
這支檢查「系統還活著嗎、文件與程式碼有沒有漂移」：

  一致性（ERROR，CI 會擋）：
    - scripts/*.py 每支都要在 scripts/README.md 有說明
    - docs/ prompts/ templates/ 的每個檔案都要被其他文件引用（孤兒偵測）
    - 活文件中提到的 repo 內路徑必須存在（文件↔程式碼漂移偵測）
    - .github/workflows/ 引用的腳本必須存在
    - 決策守衛（data/decision_guards.yml）：已拍板決策的禁用識別字
      不得回到活文件 / 程式碼（擋「殭屍任務卡」——舊世界觀的任務被照做）

  新鮮度 / 產線（WARN，CI 不擋，但由 health.yml 週期巡檢盯）：
    - 週挑 (buy_shortlist) 落後幾週（INFO，D29 後無硬 SLA）
    - 每個排行基準快照的年齡（INFO；Lyst 另有 D31 發布寬限 WARN）
    - 當月 monthly report 是否缺
    - Lyst 季度快照是否有「已發布逾寬限卻沒 ingest」的季（D31 發布寬限模型，非日曆季差）
    - 判斷軸（D40，全 info）：週挑「上週複驗」數／lessons 重演 ≥3 未硬化／雷達快照滿 90 天未回測
    - 重定位後產的報告（daily / monthly）是否符合現行契約
      （殭屍任務卡的產出層防線——決策守衛不掃 reports/，舊世界觀產出從這裡抓）

歷史紀錄（CHANGELOG、reports/）不在路徑掃描範圍——
它們允許提到已刪除或未建立的檔案。

用法：
    python scripts/repo_health.py            # 人讀報告 + Next Actions
    python scripts/repo_health.py --json     # 給 agent 吃的 JSON
    python scripts/repo_health.py --strict   # WARN 也算失敗（手動巡檢用）

exit code：有 ERROR → 1（--strict 時 WARN 也算）；否則 0。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 讓 _probe_rss 能 import 同層的 collect_raw_signals；模組載入時設一次（不在每次 probe 時重插，避免 sys.path 污染）
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

ROOT = Path(__file__).resolve().parent.parent

# 新鮮度門檻
# （daily 斷更檢查已於 2026-06-14 移除：D16 後 daily brief 改對話觸發、不入 reports/daily/，
#   用「檔案新鮮度」監控對話產出只會永遠誤報，見 docs/decisions.md D16）
MONTHLY_GRACE_DAY = 3         # 每月 N 號後仍無當月月報就警告
LYST_PUBLISH_LAG_DAYS = 45    # Lyst 季度索引在「季結束後 ~3-4 週」才發布(Q2'25=7/23)。
                              # 舊的純日曆季差(落後>=2季就警)讓每年 1/4/7/10 月的頭六週
                              # 固定假警報 —— behind 跳 2 但新索引根本還沒出、無事可做。
                              # 改成:只有「已過發布寬限的季」沒 ingest 才算真落後。

# 報告產出契約（重定位 2026-06-05 拍板後產的報告適用；歷史快照不溯及。月報以當月 1 號計）
OUTPUT_CONTRACT_SINCE = dt.date(2026, 6, 5)
OUTPUT_BANNED_MARKS = ("對創作者的意義", "可拍選題", "Content Hooks")  # 重定位前的欄位 / 段落識別字
OUTPUT_CONTRACTS = (
    # (reports/ 子目錄, 檔名 glob, 必有段落；tuple = 任一即可，含過渡期舊名)
    # daily 段落 2026-06-14 由「🛒 對我有用」改名「🎯 對我最相關」(D15)；舊名續收以免凍結舊 brief 變不合規
    ("daily", "????-??-??.md", ("## 🎯 對我最相關 For Me", "## 🛒 對我有用 For Me")),
    ("monthly", "????-??-*.md", ("## 🛒 本月挑買方向",)),
)

# 月報地區線：後綴 → 起算月（該月起，當月缺檔才算斷更；日本線 2026-07 開跑）
MONTHLY_REGION_SINCE = {"eu": dt.date(2026, 6, 1), "jp": dt.date(2026, 7, 1)}

# 路徑掃描的「活文件」範圍；歷史紀錄不掃（允許提到已刪/規劃中的檔案）
PATH_SCAN_EXCLUDE = {
    "CHANGELOG.md",                    # 演進史，會提到已移除的檔案
    "AI_SYSTEM_UPGRADE_REPORT.md",     # 點時審計紀錄（sleep-mode 巡檢），同屬歷史紀錄
}
PATH_RE = re.compile(
    r"(?:data|docs|prompts|scripts|templates|tests|\.github)/[A-Za-z0-9_\-./]*\.(?:md|py|yml|yaml|xml|txt)"
)
PLACEHOLDER_MARKS = ("YYYY", "{{", "<", "*", "…")

# 死源偵測偽陽性退避：非活類（gone/nxdomain/blocked/empty/unreachable）隔這麼多秒重打一次再定讞——只防真瞬斷（DNS 抖、暫時 5xx），
# 治不了 UA/egress 地理這類「探測視角」問題（UA 級 WAF 常間歇、重試偶爾矇過≠治好；
# 對症解是 reader-grade UA + 本機複核，見 docs/lessons.md 2026-07-03 訂正節）；
# 429 有自己的退避、不在此列。測試可傳 retry_delay=0 關掉。
LIVENESS_RETRY_DELAY_SEC = 2.0

# ---------- 判斷軸（D40，2026-09-03）----------
# 迴圈原本只量流程（活著沒、漂沒漂）；這三個檢查把「判斷準不準」拉進 Observe 層。
# 全部 info 級：health.yml 跑 --strict，warn 會讓週一四巡檢變紅、開 issue——判斷軸是儀表不是告警（D29 精神）。
WEEKLY_REVIEW_SINCE = (2026, 36)   # 週挑 header 從這一 ISO 週起帶「上週複驗」欄；之前的 grandfather
LESSON_HARDEN_AT = 3               # 取自 lessons.md 自己的規矩「不要讓同一個坑踩第三次」：重演到 3 就該硬化
RADAR_BACKTEST_DAYS = 90           # D11：品牌雷達快照「三個月後回測」；只認檔名含 brand-radar 的 analysis 快照
WEEKLY_REVIEW_RE = re.compile(r"\*\*上週複驗：\*\*\s*推薦\s*(\d+)\s*／\s*複驗\s*(\d+)\s*／\s*須更正\s*(\d+)")
LESSON_RECUR_RE = re.compile(r"\*\*重演\*\*：(\d+)")


class Finding:
    def __init__(self, level: str, message: str, action: str | None = None):
        self.level = level      # error / warn / info
        self.message = message
        self.action = action    # 對應的下一步行動（可為 None）


def living_md_files() -> list[Path]:
    """要掃描的活文件：repo 內 .md，排除 reports/（封存快照）與明確排除清單。"""
    files = []
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("reports/") or rel in PATH_SCAN_EXCLUDE:
            continue
        if "__pycache__" in rel or rel.startswith((".venv/", "venv/")):
            continue
        files.append(path)
    return files


# ---------- 一致性檢查（ERROR） ----------

def check_scripts_documented() -> list[Finding]:
    """每支 scripts/*.py 都要在 scripts/README.md 被提到。"""
    findings: list[Finding] = []
    readme = ROOT / "scripts" / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    for script in sorted((ROOT / "scripts").glob("*.py")):
        if script.name not in text:
            findings.append(Finding(
                "error",
                f"scripts/{script.name} 未出現在 scripts/README.md",
                f"在 scripts/README.md 補上 {script.name} 的用法說明（或移除該腳本）",
            ))
    return findings


def check_orphans() -> list[Finding]:
    """docs/ prompts/ templates/ 的每個檔案都要被其他文件引用至少一次。"""
    findings: list[Finding] = []
    corpus: dict[str, str] = {}
    for path in living_md_files():
        corpus[path.relative_to(ROOT).as_posix()] = path.read_text(encoding="utf-8")
    # CHANGELOG 雖不做路徑存在掃描，但「被引用」的證據仍可採計
    for rel in PATH_SCAN_EXCLUDE:
        p = ROOT / rel
        if p.exists():
            corpus[rel] = p.read_text(encoding="utf-8")

    for subdir in ("docs", "prompts", "templates"):
        for path in sorted((ROOT / subdir).glob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            referenced = any(
                path.name in text for other, text in corpus.items() if other != rel
            )
            if not referenced:
                findings.append(Finding(
                    "error",
                    f"{rel} 沒有被任何其他文件引用（孤兒檔）",
                    f"把 {rel} 接回導覽（README / docs），或評估是否該刪除 / 併入他檔",
                ))
    return findings


def check_path_references() -> list[Finding]:
    """活文件中提到的 repo 內路徑必須真的存在（文件↔程式碼漂移）。"""
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for path in living_md_files():
        rel = path.relative_to(ROOT).as_posix()
        for match in PATH_RE.findall(path.read_text(encoding="utf-8")):
            if any(mark in match for mark in PLACEHOLDER_MARKS):
                continue
            if (rel, match) in seen:
                continue
            seen.add((rel, match))
            if not (ROOT / match).exists():
                findings.append(Finding(
                    "error",
                    f"{rel} 提到 {match}，但該檔不存在",
                    f"修正 {rel} 的引用（檔案改名 / 已刪 / 規劃未建都要讓文件反映現實）",
                ))
    return findings


def check_decision_guards() -> list[Finding]:
    """已拍板決策的禁用識別字不得回到活文件 / 程式碼（data/decision_guards.yml）。

    只做識別字層（檔名 / 欄位名 / 目錄名），零誤殺；散文層語意矛盾仍靠 review。
    """
    findings: list[Finding] = []
    guards_path = ROOT / "data" / "decision_guards.yml"
    if not guards_path.exists():
        return [Finding("error", "data/decision_guards.yml 不存在",
                        "補回決策守衛檔（或從 git 歷史還原）")]
    try:
        import yaml
    except ImportError:
        return [Finding("warn", "缺 pyyaml，略過決策守衛檢查", "pip install -r requirements.txt")]
    data = yaml.safe_load(guards_path.read_text(encoding="utf-8")) or {}

    scan_suffixes = (".md", ".py", ".yml", ".yaml")
    for guard in data.get("guards", []):
        pattern = re.compile(guard["pattern"])
        excludes = tuple(guard.get("exclude", []))
        for scope in guard.get("scope", []):
            base = ROOT / scope
            paths = [base] if base.is_file() else sorted(base.rglob("*")) if base.is_dir() else []
            for path in paths:
                if not path.is_file() or path.suffix not in scan_suffixes:
                    continue
                rel = path.relative_to(ROOT).as_posix()
                if rel.startswith(excludes) or "__pycache__" in rel:
                    continue
                for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if pattern.search(line):
                        findings.append(Finding(
                            "error",
                            f"{rel}:{n} 違反決策守衛 {guard['id']}（{guard['decision']}）：{line.strip()[:80]}",
                            f"該決策已拍板：{guard['reason']}——移除此引用；"
                            f"若是要推翻決策，先更新 docs/decisions.md 與本守衛，不要默默繞過",
                        ))
                        break  # 每檔每守衛報一次即可
    return findings


def check_workflow_scripts() -> list[Finding]:
    """workflows 內 run: 引用的 scripts / tests 檔案必須存在。"""
    findings: list[Finding] = []
    wf_dir = ROOT / ".github" / "workflows"
    pattern = re.compile(r"(?:scripts|tests)/[A-Za-z0-9_\-]+\.py")
    for wf in sorted(wf_dir.glob("*.yml")):
        for match in set(pattern.findall(wf.read_text(encoding="utf-8"))):
            if not (ROOT / match).exists():
                findings.append(Finding(
                    "error",
                    f".github/workflows/{wf.name} 引用 {match}，但該檔不存在",
                    f"修正 {wf.name} 或補回 {match}",
                ))
    return findings


# ---------- 新鮮度檢查（WARN） ----------

def check_weekly_picks_freshness(today: dt.date) -> list[Finding]:
    """週挑（buy_shortlist）斷更檢查。目錄空 = 還沒開始，只提示不警告。"""
    weeks = []
    for report in (ROOT / "reports" / "buy_shortlist").glob("????-W??.md"):
        m = re.match(r"^(\d{4})-W(\d{2})$", report.stem)
        if m:
            weeks.append((int(m.group(1)), int(m.group(2))))
    if not weeks:
        return [Finding("info", "reports/buy_shortlist/ 尚無週挑",
                        "想開始的話：generate_weekly_buy_picks.py 產骨架")]
    iso = today.isocalendar()
    latest = max(weeks)
    # 以 ISO 週一日期相減算落後週數——ISO 年有 52/53 週（2026 即 53 週），
    # 用「×52」跨年會少算一週，warning 晚一週才響。
    behind = (
        dt.date.fromisocalendar(iso[0], iso[1], 1)
        - dt.date.fromisocalendar(latest[0], latest[1], 1)
    ).days // 7
    if behind >= 2:
        # D29: 移除 patrol 對週挑的硬 SLA。D25/D26 的「週一早安觸發 + 候選池收斂」
        # 機制保留——該產還是產；但落後不再是讓 health.yml --strict 變紅的 warn，
        # 因為週挑無強制週更承諾（合 D16/D20/D21）。降為 info：仍顯示落後供參考，
        # 但 CI 紅保留給真斷更（daily brief 死、契約違反、ERROR）＝真的壞了。
        return [Finding(
            "info",
            f"週挑落後 {behind} 週（最新：{latest[0]}-W{latest[1]:02d}）"
            "——週一早安該產就產（D25/D26），但無硬 SLA、不擋巡檢（D29）",
            "想產就在週一早安說，或直接說「產一支週挑」",
        )]
    return [Finding("info", f"週挑最新：{latest[0]}-W{latest[1]:02d}（落後 {behind} 週內）")]


def check_monthly_freshness(today: dt.date) -> list[Finding]:
    findings: list[Finding] = []
    for suffix, since in MONTHLY_REGION_SINCE.items():
        if today < since:
            continue
        expected = ROOT / "reports" / "monthly" / f"{today:%Y-%m}-{suffix}.md"
        if expected.exists():
            findings.append(Finding("info", f"當月月報已存在：{expected.name}"))
        elif today.day >= MONTHLY_GRACE_DAY:
            findings.append(Finding(
                "warn",
                f"當月月報 {expected.name} 不存在（已過每月 {MONTHLY_GRACE_DAY} 號）",
                "月報改對話觸發（D16，無排程）：說一聲跑 generate_monthly_heat_report.py 產骨架 → 補內容"
                f"（--region {'jp' if suffix == 'jp' else 'us-eu'}）",
            ))
    return findings


def check_lyst_staleness(today: dt.date) -> list[Finding]:
    """Lyst 是唯一固定季度節奏的榜。D31（2026-07-03）改「發布寬限」模型：上一季索引要
    「季結束 + LYST_PUBLISH_LAG_DAYS 天」後才算可 ingest，「已發布逾寬限卻沒 ingest」才 WARN
    ——紅＝「有東西可以 ingest 而沒人動」，不再是「日曆走到季界」（舊日曆季差語意已廢）。"""
    try:
        import yaml
    except ImportError:
        return [Finding("warn", "缺 pyyaml，略過 Lyst 快照檢查", "pip install -r requirements.txt")]
    path = ROOT / "data" / "rankings" / "lyst-index.yml"
    if not path.exists():
        return [Finding("error", "data/rankings/lyst-index.yml 不存在", "補回 Lyst 快照檔")]
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    snaps = data.get("snapshots") or []
    periods = [s.get("period", "") for s in snaps if isinstance(s, dict)]
    latest_q = None
    for p in periods:
        m = re.match(r"^(\d{4})-Q([1-4])$", str(p))
        if m:
            idx = int(m.group(1)) * 4 + int(m.group(2))
            latest_q = max(latest_q or 0, idx)
    if latest_q is None:
        return [Finding("warn", "lyst-index.yml 沒有可解析的季度 period", "檢查 snapshots 的 period 格式（YYYY-QN）")]
    current_q = today.year * 4 + (today.month - 1) // 3 + 1
    behind = current_q - latest_q
    # 上一季的索引要「季結束 + LYST_PUBLISH_LAG_DAYS」後才存在;在那之前它不算可 ingest。
    prev_idx = current_q - 1
    py, pq = (prev_idx - 1) // 4, (prev_idx - 1) % 4 + 1
    prev_end = (dt.date(py, 12, 31) if pq == 4
                else dt.date(py, pq * 3 + 1, 1) - dt.timedelta(days=1))
    expected_q = prev_idx if today > prev_end + dt.timedelta(days=LYST_PUBLISH_LAG_DAYS) else prev_idx - 1
    if latest_q < expected_q:
        return [Finding(
            "warn",
            f"Lyst 快照落後 {behind} 季且新一季已發布逾 {LYST_PUBLISH_LAG_DAYS} 天寬限（最新：{max(periods)}）",
            "新一季 Lyst Index 已發布的話，在對話請 AI 依 prompts/ranking_ingest.md 把新快照編輯進 "
            "data/rankings/lyst-index.yml（D21：直接編 yaml，ingest_ranking_snapshot.py 已移除）",
        )]
    return [Finding("info", f"Lyst 快照：落後 {behind} 季（發布節奏寬限內，無可 ingest 的新季）")]


RANKING_AGE_SKIP = {"lyst-index.yml"}   # Lyst 走 D31 的發布寬限模型，這裡不重複報


def _parse_published(value):
    """回 (date, month_only)。`published` 兩種寫法在檔裡都真實存在：'2026-06-20' 與 '2026-01'。
    只到月的當月 1 號算並標出精度——別讓「2026-01」看起來像精確到日。"""
    s = str(value).strip().strip("'\"")
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3))), False
        except ValueError:
            return None, False
    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if m:
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), 1), True
        except ValueError:
            return None, False
    return None, False


def check_ranking_snapshot_ages(today: dt.date) -> list[Finding]:
    """每個排行基準的最新快照有多舊。D31 只盯 Lyst，其餘四檔沒有任何東西在看——
    2026-09-03 實測：musinsa / kream / snkrdunk 三檔同時停在 6/20–6/21（75 天），
    月報「韓潮外溢」段因此兩份都只能標待查，而 repo_health 印的是「一切健康」。

    這裡**只印年齡（info），不判定多舊算過期**：門檻是內容判斷——`prompts/monthly_heat_report.md`
    的基準新鮮度 #3 只覆蓋 Lyst 與 MUSINSA，且各檔 `cadence` 欄寫的是**來源的發布節奏**、
    不是本檔的入庫承諾（kream/snkrdunk 的欄位註解明寫「按需記」）。硬要換算成 WARN 等於
    我替擁有者訂了一個他沒訂過的 SLA。先讓數字在開工時看得見——今天是靠手讀 yaml 才發現的。"""
    try:
        import yaml
    except ImportError:
        return [Finding("warn", "缺 pyyaml，略過排行快照年齡檢查", "pip install -r requirements.txt")]
    rdir = ROOT / "data" / "rankings"
    if not rdir.is_dir():
        return []
    findings: list[Finding] = []
    for path in sorted(rdir.glob("*.yml")):
        if path.name in RANKING_AGE_SKIP:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        source = data.get("source") or path.stem
        parts = str(data.get("cadence") or "").split()
        cadence = parts[0] if parts else "待查"
        snaps = [s for s in (data.get("snapshots") or []) if isinstance(s, dict)]
        if not snaps:
            findings.append(Finding("info", f"排行快照 {source}：尚無快照（cadence {cadence}）"))
            continue
        raw = snaps[0].get("published", "")
        made, month_only = _parse_published(raw)
        if made is None:
            findings.append(Finding(
                "info", f"排行快照 {source}：最新一筆 published 無法解析（{raw!r}，cadence {cadence}）"))
            continue
        precision = "（只到月）" if month_only else ""
        findings.append(Finding(
            "info",
            f"排行快照 {source}：最新 {raw}{precision}，{(today - made).days} 天前（cadence {cadence}）",
        ))
    return findings


def check_output_contract(today: dt.date) -> list[Finding]:
    """重定位後產的報告（daily / monthly）必須符合現行契約（templates/）。

    決策守衛只掃活文件，reports/ 是封存快照不在 scope——排程 / 外部 agent
    拿舊任務卡「產出」的報告會從這個缺口進來（2026-06-10 daily 實際發生）。
    這裡補產出層防線：只檢查拍板日之後產的報告，歷史快照不溯及、不回改。

    另防「空轉殭屍」：骨架有必有段落標題、新鮮度也綠，但內容從沒被填——
    報告日期已過仍殘留 {{...}} 佔位 = 產線只產殼。當日的不吵（內容填寫中）。
    """
    findings: list[Finding] = []
    for subdir, pattern, required_marks in OUTPUT_CONTRACTS:
        for report in sorted((ROOT / "reports" / subdir).glob(pattern)):
            m = re.match(r"^(\d{4})-(\d{2})(?:-(\d{2}))?", report.stem)
            if not m:
                continue
            try:
                day = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 1))
            except ValueError:
                continue
            if day < OUTPUT_CONTRACT_SINCE:
                continue
            text = report.read_text(encoding="utf-8")
            problems = []
            if not any(rm in text for rm in required_marks):
                problems.append(f"缺必有段落「{required_marks[0]}」")
            hits = [mark for mark in OUTPUT_BANNED_MARKS if mark in text]
            if hits:
                problems.append(f"含重定位前識別字 {hits}")
            if "{{" in text and day < today:
                problems.append("骨架未填內容（殘留 {{…}} 佔位且日期已過）")
            if problems:
                findings.append(Finding(
                    "warn",
                    f"reports/{subdir}/{report.name} 不符現行產出契約：{'；'.join(problems)}",
                    f"產出端失效（舊任務卡或只產殼沒填內容）：更新產出該報告的排程 / agent 任務指示，"
                    f"並依 templates/ 現行契約補齊 {report.name}",
                ))
    return findings


def check_rss_coverage() -> list[Finding]:
    try:
        import yaml
    except ImportError:
        return []
    data = yaml.safe_load((ROOT / "data" / "sources.yml").read_text(encoding="utf-8")) or {}
    sources = data.get("sources", [])
    # 分母只算結構上走得了 RSS 的來源（media / community）。
    # ranking 走快照、social 無 RSS（IG 待 API）、retailer 無公開 feed 且不硬刮——
    # 全來源當分母會讓覆蓋率永遠像「只做一半」，指標衰退成沒人看的噪音。
    rssable = [s for s in sources if s.get("type") in ("media", "community")]
    with_rss = sum(1 for s in rssable if s.get("rss"))
    other = len(sources) - len(rssable)
    return [Finding(
        "info",
        f"RSS 覆蓋：{with_rss}/{len(rssable)} 個可自動收來源"
        f"（另 {other} 個 ranking/social/retailer 結構性不走 RSS）",
    )]


def _probe_rss(url: str, timeout: int = 15) -> tuple[str, int]:
    """打一次 rss，回 (狀態類別, http_code)。
    狀態類別（2026-07-21 視角感知分類——#186 四次誤殺的結構修法）：
      ok / empty(200但解析0則) / ratelimited(429)
      gone(404/410＝真死候補) / nxdomain(DNS 查無此域＝最強真死訊號)
      blocked(403＝活著但拒收「本探測視角」，永不當死源證據) / unreachable(timeout/5xx/其他＝視角存疑)。
    403 是「誰在看」的陳述、不是「還在不在」的陳述：bof 對 Actions egress 連紅五輪、
    本機兩閘全活（#186 7/20）；reader-grade UA（#177）救不了 IP 信譽封鎖，故 403 永不判死。
    2026-06-15 dogfood 教訓（429≠死源）續留：限速單獨歸類。"""
    import collect_raw_signals as c  # 同層；路徑已於模組載入時設好
    req = urllib.request.Request(url, headers={"User-Agent": c.UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml = resp.read().decode("utf-8", errors="replace")
        n = len(c.parse_feed(xml, {"id": "_probe", "url": url}))
        return ("ok", 200) if n > 0 else ("empty", 200)
    except urllib.error.HTTPError as e:
        code = e.code
        e.close()  # urlopen 拋錯時 with 沒進去，error response 要自己關（否則連線開到 GC）
        if code == 429:
            return ("ratelimited", 429)
        if code == 403:
            return ("blocked", 403)
        if code in (404, 410):
            return ("gone", code)
        return ("unreachable", code)
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), socket.gaierror):
            return ("nxdomain", 0)  # DNS 查無此域——唯一不需第二視角佐證的死訊號
        return ("unreachable", 0)
    except Exception:  # noqa: BLE001 — timeout / decode 都歸連不上（視角存疑、非死）
        return ("unreachable", 0)


def check_source_liveness(probe=_probe_rss, retry_delay: float = LIVENESS_RETRY_DELAY_SEC) -> list[Finding]:
    """實際連網打每個 rss URL，揪出『設定在、但每次都默默 403/404/0 則』的死源。
    需網路、慢，故只在 --liveness 手動跑（不入預設 / CI --strict，否則 CI 會因外站抖動變 flaky）。
    根因：collect_raw_signals 對抓取失敗優雅降級——死源會永遠躲在『31 個 RSS』的數字裡沒人發現
    （Mercari 陳貨 D17、reddit www 域 403 都是這類）。此檢查把『宣稱 ≠ 實際』顯性化。
    429（限速）單獨標示、不算死源——活著但被擋，是『調抓取節奏』而非『撤源』的訊號。
    偽陽性退避（D32，2026-07-03）：dead/empty/unreachable 隔 retry_delay 秒重打一次，二次仍非活才定讞死源
    ——只防真瞬斷（DNS 抖、暫時 5xx）；歷史兩組誤報實例事後查明皆非瞬斷（6/16 KR=Actions 地理、
    7/2 bof/heddels/permanent-style=bot UA 被擋，#177 換 reader-grade UA 解），重試防不了那類
    「探測視角」持續封鎖——報死先疑地理/UA、本機複核再談撤源（docs/lessons.md 2026-07-03）。
    標籤即機器契約（2026-07-21）：health.yml 以 grep「死源候補：」決定開 issue；
    「疑遭阻擋」「限速」為非死判定,永不觸發撤源流程——撤源指引只掛在死源候補行。"""
    try:
        import yaml
    except ImportError:
        return [Finding("warn", "缺 pyyaml，無法跑來源死活檢查", "pip install pyyaml")]
    data = yaml.safe_load((ROOT / "data" / "sources.yml").read_text(encoding="utf-8")) or {}
    rssable = [s for s in data.get("sources", []) if s.get("rss")]
    detail: list[Finding] = []
    ok = candidate = suspect = limited = 0

    def _confirm(url: str) -> tuple[str, int]:
        status, code = probe(url)
        # ok=活、429=活著被限速（自有退避、不重打以免火上加油）；
        # 非活類（gone/nxdomain/blocked/empty/unreachable）可能是瞬斷 → 隔一下重打一次再定讞（降偽陽性）。
        if status not in ("ok", "ratelimited"):
            if retry_delay:
                time.sleep(retry_delay)
            status, code = probe(url)
        return status, code

    # 平行探測（每源最高 15s timeout，序列版最壞 33×15≈8 分鐘；I/O bound、urlopen 釋放 GIL）。
    # 結果照 rssable 順序歸併 → 死源/限速清單穩定可重現。max_workers 保守（429 已被當非死源處理）。
    if not rssable:
        results: list[tuple[str, int]] = []
    else:
        with ThreadPoolExecutor(max_workers=max(1, min(8, len(rssable)))) as ex:
            results = list(ex.map(lambda s: _confirm(s["rss"]), rssable))
    for s, (status, code) in zip(rssable, results):
        if status == "ok":
            ok += 1
        elif status == "ratelimited":
            limited += 1
            detail.append(Finding(
                "warn",
                f"限速（非死源）：{s.get('id')} 回 429——活著但被擋，調抓取節奏（退避/間隔）而非撤源",
            ))
        elif status in ("gone", "nxdomain"):
            candidate += 1
            detail.append(Finding(
                "warn",
                f"死源候補：{s.get('id')}（{s.get('rss')}）→ {status}"
                + (f" HTTP {code}" if code else "")
                + "——404/410/NXDOMAIN 屬真死訊號",
                "確認可否換域名/端點修復；真的無解就比照 D17 撤源、改 sources.yml + 記 decisions",
            ))
        else:  # blocked / empty / unreachable — 探測視角存疑，非死源判定
            suspect += 1
            detail.append(Finding(
                "warn",
                f"疑遭阻擋（本探測視角）：{s.get('id')}（{s.get('rss')}）→ {status}"
                + (f" HTTP {code}" if code else "")
                + "——本行是 Actions egress 視角；flash 與深度日報 D35 起均在本機對話跑,不受影響",
                "本機 --liveness 複核；勿依本行撤源；本機亦死才改判死源候補（#122×2、#186 四次誤殺教訓）",
            ))
    summary = Finding(
        "info" if (candidate == 0 and suspect == 0 and limited == 0) else "warn",
        f"來源死活：{ok}/{len(rssable)} 個 RSS 實際收得到料"
        + (f"，{candidate} 死源候補" if candidate else "")
        + (f"，{suspect} 疑遭阻擋（探測視角，非死源）" if suspect else "")
        + (f"，{limited} 被限速（非死，見下）" if limited else ""),
    )
    return [summary, *detail]


# ---------- 輸出 ----------

def check_analysis_outputs() -> list[Finding]:
    """reports/analysis 的 brand-radar / deep-dive 檔名/結構刻意自由（非日期），不進
    OUTPUT_CONTRACTS 的日期契約，但仍會被 commit 進 master——之前完全無守門。
    補最低防線（擁有者 2026-06-16 拍板：保留自由格式，只守 H1 + 禁字）：
    ① H1 開頭 ② 不含重定位前識別字（擋舊世界觀從這個產出缺口進來，同 2026-06-10 daily 型）。"""
    findings: list[Finding] = []
    adir = ROOT / "reports" / "analysis"
    if not adir.is_dir():
        return findings
    for report in sorted(adir.glob("*.md")):
        if report.name.endswith(".draft.md"):
            continue
        text = report.read_text(encoding="utf-8")
        problems = []
        if not text.lstrip().startswith("# "):
            problems.append("缺 H1 開頭")
        hits = [mark for mark in OUTPUT_BANNED_MARKS if mark in text]
        if hits:
            problems.append(f"含重定位前識別字 {hits}")
        if problems:
            findings.append(Finding(
                "warn",
                f"reports/analysis/{report.name} 不符最低產出契約：{'；'.join(problems)}",
                "analysis 格式自由但需 H1 + 不含舊世界觀識別字；補上或清掉違規識別字",
            ))
    return findings


# ---------- 判斷軸（D40）：info 級，不擋巡檢 ----------


def check_weekly_review() -> list[Finding]:
    """判斷軸的第一個數字：上週推薦位被本週複驗後「須更正」幾條。
    這個數字本來就每週手寫在候選池 ⚠️ 區塊（W34 五處、W35 六處＋複驗三處），但池子是
    gitignored 草稿、沒人把它讀成指標。週挑 header 帶一行可解析欄位，這裡只是印出來。
    缺欄位＝info 提醒、不擋（D29：週挑無硬 SLA）；WEEKLY_REVIEW_SINCE 之前的週 grandfather。"""
    latest = None
    for report in (ROOT / "reports" / "buy_shortlist").glob("????-W??.md"):
        m = re.match(r"^(\d{4})-W(\d{2})$", report.stem)
        if m:
            key = (int(m.group(1)), int(m.group(2)))
            if latest is None or key > latest[0]:
                latest = (key, report)
    if latest is None or latest[0] < WEEKLY_REVIEW_SINCE:
        return []
    (year, week), report = latest
    label = f"{year}-W{week:02d}"
    m = WEEKLY_REVIEW_RE.search(report.read_text(encoding="utf-8"))
    if not m:
        return [Finding(
            "info",
            f"{label} 未記「上週複驗」（推薦／複驗／須更正 三個數）",
            "週挑收斂時填 header 的「上週複驗：推薦 N ／ 複驗 N ／ 須更正 N」——來源是候選池 ⚠️ 區塊，不是新調查",
        )]
    rec, chk, fix = (int(x) for x in m.groups())
    rate = f"{fix}/{chk}" if chk else "—"
    return [Finding("info", f"{label} 上週複驗：推薦 {rec}、複驗 {chk}、須更正 {fix}（更正率 {rate}）")]


def check_lessons_recurrence() -> list[Finding]:
    """D7「反覆出現才硬化」原本沒有計數器——實測 soft note 自標「重演／再犯」六條、都沒人硬化。
    lessons.md 的 soft note 自帶 `- **重演**：N｜已硬化：…` 或 `｜未硬化`；只數「## Soft notes」
    之下、N ≥ LESSON_HARDEN_AT、且該行沒有「｜已硬化」的條目。**只認顯式標籤、不掃散文**（否則會把
    「別再犯」讀成再犯）；沒標＝0、不溯及。info 級：這是提醒該硬化，不是硬化本身。"""
    path = ROOT / "docs" / "lessons.md"
    if not path.exists():
        return []
    findings: list[Finding] = []
    in_soft = False
    title = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_soft = "Soft" in line
            continue
        if not in_soft:
            continue
        if line.startswith("### "):
            title = line[4:].strip()
            continue
        m = LESSON_RECUR_RE.search(line)
        if m and int(m.group(1)) >= LESSON_HARDEN_AT and "｜已硬化" not in line:
            findings.append(Finding(
                "info",
                f"教訓已重演 {m.group(1)} 次仍未硬化：{title}",
                "反覆出現才硬化（D7）——現在就是那個時候：硬化成檢查或文件硬規則，並把該行改標「｜已硬化：…」",
            ))
    return findings


def check_radar_backtest_due(today: dt.date) -> list[Finding]:
    """D11 承諾雷達快照「三個月後回測『當時說紅的還紅嗎』」，但 repo 裡從沒有東西會觸發它。
    只認檔名含 brand-radar 的 analysis 快照；滿 RADAR_BACKTEST_DAYS 天且沒有同名 -backtest.md
    兄弟檔才提示（回測寫兄弟檔，不回改封存快照）。info 級、回測本身仍是對話觸發（D7）。"""
    adir = ROOT / "reports" / "analysis"
    if not adir.is_dir():
        return []
    findings: list[Finding] = []
    for report in sorted(adir.glob("*brand-radar*.md")):
        if report.name.endswith(("-backtest.md", ".draft.md")):
            continue
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", report.name)
        if not m:
            continue
        try:
            made = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        age = (today - made).days
        if age >= RADAR_BACKTEST_DAYS and not report.with_name(report.stem + "-backtest.md").exists():
            findings.append(Finding(
                "info",
                f"雷達快照 {report.name} 已 {age} 天未回測（D11：三個月後回測「當時說紅的還紅嗎」）",
                f"對話說「回測 {report.stem}」→ 產 reports/analysis/{report.stem}-backtest.md（不回改快照）",
            ))
    return findings

def run_checks(today: dt.date, consistency_only: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    findings += check_scripts_documented()
    findings += check_orphans()
    findings += check_path_references()
    findings += check_workflow_scripts()
    findings += check_decision_guards()
    findings += check_analysis_outputs()  # consistency 層：每 PR 擋 analysis 禁字/H1 回流
    findings += check_lessons_recurrence()  # consistency 層（D40）：教訓重演 ≥3 未硬化，每 PR 提醒
    if not consistency_only:
        # daily 斷更檢查已移除（D16：daily brief 對話觸發、不入 reports/daily/，無檔可監控）
        findings += check_weekly_picks_freshness(today)
        findings += check_monthly_freshness(today)
        findings += check_lyst_staleness(today)
        findings += check_ranking_snapshot_ages(today)  # D31 只盯 Lyst；其餘四檔的年齡也要看得見
        findings += check_output_contract(today)
        findings += check_rss_coverage()
        findings += check_weekly_review()            # D40 判斷軸：上週推薦位複驗後須更正幾條
        findings += check_radar_backtest_due(today)  # D40/D11：雷達快照滿 90 天未回測
    return findings


ICONS = {"error": "❌", "warn": "⚠️ ", "info": "ℹ️ "}


def main() -> None:
    parser = argparse.ArgumentParser(description="Repo 自我健康檢查（Observe / Diagnose / Next Action）")
    parser.add_argument("--json", action="store_true", help="輸出 JSON（給 agent / 自動化吃）")
    parser.add_argument("--strict", action="store_true", help="WARN 也算失敗")
    parser.add_argument("--consistency", action="store_true", help="只跑一致性檢查（CI 用，不含新鮮度）")
    parser.add_argument("--liveness", action="store_true", help="實際連網打每個 RSS，揪出死源（慢、需網路，不入 CI）")
    parser.add_argument("--date", help="以指定日期計算新鮮度（YYYY-MM-DD，測試用）")
    args = parser.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    if args.liveness:
        findings = check_source_liveness()
    else:
        findings = run_checks(today, consistency_only=args.consistency)

    errors = [f for f in findings if f.level == "error"]
    warns = [f for f in findings if f.level == "warn"]
    infos = [f for f in findings if f.level == "info"]
    # 同一條行動可能被多個 finding 指到（如多處缺 pyyaml）——去重保序
    actions = list(dict.fromkeys(
        f.action for f in findings if f.action and f.level in ("error", "warn")
    ))

    if args.json:
        print(json.dumps({
            "date": today.isoformat(),
            "errors": [f.message for f in errors],
            "warnings": [f.message for f in warns],
            "info": [f.message for f in infos],
            "next_actions": actions,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Repo Health · {today.isoformat()}")
        print("=" * 50)
        for f in errors + warns + infos:
            print(f"{ICONS[f.level]} {f.message}")
        if actions:
            print("\n## Next Actions（依優先序）")
            for i, action in enumerate(actions, 1):
                print(f"{i}. {action}")
        if not errors and not warns:
            print("\n✅ 一切健康，沒有待辦。")

    failed = bool(errors) or (args.strict and bool(warns))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
