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
    - daily brief 斷更幾天
    - 週挑（buy_shortlist）是否落後 2 週以上
    - 當月 monthly report 是否缺
    - Lyst 季度快照是否落後超過一季
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
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

# 新鮮度門檻
DAILY_STALE_DAYS = 3          # daily brief 超過這天數沒產出就警告
MONTHLY_GRACE_DAY = 3         # 每月 N 號後仍無當月月報就警告
LYST_STALE_QUARTERS = 2       # Lyst 快照落後 >= 這個季數就警告（落後 1 季屬正常發布延遲）

# 報告產出契約（重定位 2026-06-05 拍板後產的報告適用；歷史快照不溯及。月報以當月 1 號計）
OUTPUT_CONTRACT_SINCE = dt.date(2026, 6, 5)
OUTPUT_BANNED_MARKS = ("對創作者的意義", "可拍選題", "Content Hooks")  # 重定位前的欄位 / 段落識別字
OUTPUT_CONTRACTS = (
    # (reports/ 子目錄, 檔名 glob, 現行 template 的必有段落)
    ("daily", "????-??-??.md", "## 🛒 對我有用 For Me"),
    ("monthly", "????-??-*.md", "## 🛒 本月挑買方向"),
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

def check_daily_freshness(today: dt.date) -> list[Finding]:
    findings: list[Finding] = []
    dates = []
    for report in (ROOT / "reports" / "daily").glob("????-??-??.md"):
        try:
            dates.append(dt.date.fromisoformat(report.stem))
        except ValueError:
            continue
    if not dates:
        findings.append(Finding(
            "warn", "reports/daily/ 沒有任何 daily brief",
            "跑 python scripts/generate_daily_brief.py 啟動每日產線",
        ))
        return findings
    latest = max(dates)
    gap = (today - latest).days
    if gap > DAILY_STALE_DAYS:
        findings.append(Finding(
            "warn",
            f"daily brief 已 {gap} 天沒產出（最新：{latest.isoformat()}）",
            "重啟每日產線：generate_daily_brief.py --with-rss 產骨架 → AI/人工補內容；"
            "daily-brief.yml 的 schedule 已開啟（2026-06-10）仍斷更＝排程死了或註冊消失，"
            "去看 GitHub Actions run 紀錄（檔案在 ≠ 在跑，見 docs/lessons.md）",
        ))
    else:
        findings.append(Finding("info", f"daily brief 最新：{latest.isoformat()}（{gap} 天前）"))
    return findings


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
        return [Finding(
            "warn",
            f"週挑已 {behind} 週沒產出（最新：{latest[0]}-W{latest[1]:02d}）",
            "跑 generate_weekly_buy_picks.py 產骨架 → 依 prompts/weekly_buy_picks.md 補內容；"
            "若不想維持週更，更新 docs/decisions.md 調整節奏宣告",
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
                "確認每月 1 號的排程 agent 是否有跑；或手動 generate_monthly_heat_report.py 補產"
                f"（--region {'jp' if suffix == 'jp' else 'us-eu'}）",
            ))
    return findings


def check_lyst_staleness(today: dt.date) -> list[Finding]:
    """Lyst 是唯一固定季度節奏的榜，落後兩季以上代表 ingest 斷了。"""
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
    if behind >= LYST_STALE_QUARTERS:
        return [Finding(
            "warn",
            f"Lyst 快照落後 {behind} 季（最新：{max(periods)}）",
            "新一季 Lyst Index 已發布的話，跑 prompts/ranking_ingest.md → ingest_ranking_snapshot.py 補快照",
        )]
    return [Finding("info", f"Lyst 快照：落後 {behind} 季（正常發布延遲內）")]


def check_output_contract(today: dt.date) -> list[Finding]:
    """重定位後產的報告（daily / monthly）必須符合現行契約（templates/）。

    決策守衛只掃活文件，reports/ 是封存快照不在 scope——排程 / 外部 agent
    拿舊任務卡「產出」的報告會從這個缺口進來（2026-06-10 daily 實際發生）。
    這裡補產出層防線：只檢查拍板日之後產的報告，歷史快照不溯及、不回改。

    另防「空轉殭屍」：骨架有必有段落標題、新鮮度也綠，但內容從沒被填——
    報告日期已過仍殘留 {{...}} 佔位 = 產線只產殼。當日的不吵（內容填寫中）。
    """
    findings: list[Finding] = []
    for subdir, pattern, required_mark in OUTPUT_CONTRACTS:
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
            if required_mark not in text:
                problems.append(f"缺必有段落「{required_mark}」")
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


# ---------- 輸出 ----------

def run_checks(today: dt.date, consistency_only: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    findings += check_scripts_documented()
    findings += check_orphans()
    findings += check_path_references()
    findings += check_workflow_scripts()
    findings += check_decision_guards()
    if not consistency_only:
        findings += check_daily_freshness(today)
        findings += check_weekly_picks_freshness(today)
        findings += check_monthly_freshness(today)
        findings += check_lyst_staleness(today)
        findings += check_output_contract(today)
        findings += check_rss_coverage()
    return findings


ICONS = {"error": "❌", "warn": "⚠️ ", "info": "ℹ️ "}


def main() -> None:
    parser = argparse.ArgumentParser(description="Repo 自我健康檢查（Observe / Diagnose / Next Action）")
    parser.add_argument("--json", action="store_true", help="輸出 JSON（給 agent / 自動化吃）")
    parser.add_argument("--strict", action="store_true", help="WARN 也算失敗")
    parser.add_argument("--consistency", action="store_true", help="只跑一致性檢查（CI 用，不含新鮮度）")
    parser.add_argument("--date", help="以指定日期計算新鮮度（YYYY-MM-DD，測試用）")
    args = parser.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
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
