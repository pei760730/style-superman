#!/usr/bin/env python3
"""
test_smoke.py — 核心腳本的最小穩定驗收（C5）

不依賴 pytest，直接 `python tests/test_smoke.py` 就能跑（CI 也跑這支）。
每個 case 跑一條真實指令，斷言 exit code 與輸出，避免後續自動化一改就壞。

涵蓋：
- validate_repo（契約）
- score_trends --demo
- track_rankings --json
- generate_daily_brief --draft（產後即刪）
- generate_monthly_heat_report --draft（產後即刪）
- ingest_ranking_snapshot dry-run：合法 fixture 通過、壞資料被擋
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

    # 2. score_trends demo
    r = run(["scripts/score_trends.py", "--demo"])
    check("score_trends --demo", r.returncode == 0 and "主打" in r.stdout, r.stderr)

    # 3. track_rankings json
    r = run(["scripts/track_rankings.py", "--json"])
    check("track_rankings --json", r.returncode == 0 and r.stdout.strip().startswith("{"), r.stderr)

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

    # 6. ingest dry-run：合法 fixture 應通過（exit 0，不寫檔）
    r = run(["scripts/ingest_ranking_snapshot.py", "--source", "lyst", "--input", str(FIX / "lyst_snapshot.yml")])
    check("ingest dry-run 合法 fixture 通過", r.returncode == 0 and "DRY RUN" in r.stdout, r.stderr)

    # 7. ingest dry-run：壞資料（重複 rank）應被擋（exit 1）
    bad = '- period: "2099-Q9"\n  brands: [{rank: 1, name: A},{rank: 1, name: B}]\n  products: [{rank: 1, brand: A, item: Y}]\n'
    r = run(["scripts/ingest_ranking_snapshot.py", "--source", "lyst"], stdin=bad)
    check("ingest dry-run 壞資料被擋", r.returncode == 1 and "重複 rank" in r.stdout, r.stdout + r.stderr)

    print(f"\n{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
