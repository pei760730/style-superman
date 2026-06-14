#!/usr/bin/env python3
"""
validate_repo.py
================
Lightweight repository contract checks for Style Superman.

This script intentionally checks structure, not fashion facts. It is meant to
catch broken YAML, missing required fields, duplicate ranking ranks, and missing
core template/report sections before a PR is merged.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in missing dependency envs
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RANKINGS_DIR = DATA_DIR / "rankings"
TEMPLATES_DIR = ROOT / "templates"
REPORTS_DIR = ROOT / "reports"


@dataclass
class CheckResult:
    name: str
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def load_yaml(path: Path) -> Any:
    if yaml is None:
        raise RuntimeError("需要 pyyaml：pip install -r requirements.txt")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def require_mapping(value: Any, path: Path, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path}: top-level YAML must be a mapping")
        return {}
    return value


def require_list(value: Any, label: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{label}: must be a list")
        return []
    return value


def missing_fields(item: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in item or item[field] in (None, ""))


def check_unique(items: list[dict[str, Any]], key: str, label: str, errors: list[str]) -> None:
    seen: set[Any] = set()
    for item in items:
        value = item.get(key)
        if value in seen:
            errors.append(f"{label}: duplicate {key}={value!r}")
        seen.add(value)


def check_sources() -> CheckResult:
    errors: list[str] = []
    path = DATA_DIR / "sources.yml"
    data = require_mapping(load_yaml(path), path, errors)
    sources = require_list(data.get("sources"), f"{path}: sources", errors)
    required = {"id", "name", "region", "type", "tier", "url"}
    for idx, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"{path}: sources[{idx}] must be a mapping")
            continue
        missing = missing_fields(source, required)
        if missing:
            errors.append(f"{path}: source {source.get('id', idx)!r} missing {', '.join(missing)}")
    check_unique([s for s in sources if isinstance(s, dict)], "id", str(path), errors)
    return CheckResult("data/sources.yml", errors)


def check_brands() -> CheckResult:
    errors: list[str] = []
    path = DATA_DIR / "brands.yml"
    data = require_mapping(load_yaml(path), path, errors)
    brands = require_list(data.get("brands"), f"{path}: brands", errors)
    required = {"id", "name", "region", "segment", "tier", "watch"}
    for idx, brand in enumerate(brands, start=1):
        if not isinstance(brand, dict):
            errors.append(f"{path}: brands[{idx}] must be a mapping")
            continue
        missing = missing_fields(brand, required)
        if missing:
            errors.append(f"{path}: brand {brand.get('id', idx)!r} missing {', '.join(missing)}")
        if "watch" in brand and not isinstance(brand["watch"], list):
            errors.append(f"{path}: brand {brand.get('id', idx)!r} watch must be a list")
    check_unique([b for b in brands if isinstance(b, dict)], "id", str(path), errors)
    return CheckResult("data/brands.yml", errors)


def check_people() -> CheckResult:
    errors: list[str] = []
    path = DATA_DIR / "people.yml"
    data = require_mapping(load_yaml(path), path, errors)
    people = require_list(data.get("people"), f"{path}: people", errors)
    required = {"id", "name", "role", "region", "influence", "watch"}
    for idx, person in enumerate(people, start=1):
        if not isinstance(person, dict):
            errors.append(f"{path}: people[{idx}] must be a mapping")
            continue
        missing = missing_fields(person, required)
        if missing:
            errors.append(f"{path}: person {person.get('id', idx)!r} missing {', '.join(missing)}")
        if "watch" in person and not isinstance(person["watch"], list):
            errors.append(f"{path}: person {person.get('id', idx)!r} watch must be a list")
    check_unique([p for p in people if isinstance(p, dict)], "id", str(path), errors)
    return CheckResult("data/people.yml", errors)


def check_taxonomy() -> CheckResult:
    errors: list[str] = []
    path = DATA_DIR / "trend_taxonomy.yml"
    data = require_mapping(load_yaml(path), path, errors)
    categories = require_list(data.get("categories"), f"{path}: categories", errors)
    tag_groups = data.get("tag_groups")
    if not isinstance(tag_groups, dict):
        errors.append(f"{path}: tag_groups must be a mapping")
    for idx, category in enumerate(categories, start=1):
        if not isinstance(category, dict):
            errors.append(f"{path}: categories[{idx}] must be a mapping")
            continue
        missing = missing_fields(category, {"id", "name", "desc", "examples"})
        if missing:
            errors.append(f"{path}: category {category.get('id', idx)!r} missing {', '.join(missing)}")
    check_unique([c for c in categories if isinstance(c, dict)], "id", str(path), errors)
    return CheckResult("data/trend_taxonomy.yml", errors)


def check_rank_values(items: Any, path: Path, label: str, errors: list[str]) -> None:
    rows = require_list(items, f"{path}: {label}", errors)
    ranks: list[Any] = []
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"{path}: {label}[{idx}] must be a mapping")
            continue
        rank = row.get("rank")
        if not isinstance(rank, int):
            errors.append(f"{path}: {label}[{idx}] rank must be an integer")
        else:
            ranks.append(rank)
    if len(ranks) != len(set(ranks)):
        errors.append(f"{path}: {label} contains duplicate ranks")


def check_ranking_file(path: Path) -> CheckResult:
    errors: list[str] = []
    data = require_mapping(load_yaml(path), path, errors)
    if not data.get("source"):
        errors.append(f"{path}: missing source")
    snapshots = require_list(data.get("snapshots"), f"{path}: snapshots", errors)
    for idx, snapshot in enumerate(snapshots, start=1):
        if not isinstance(snapshot, dict):
            errors.append(f"{path}: snapshots[{idx}] must be a mapping")
            continue
        if not snapshot.get("period"):
            errors.append(f"{path}: snapshots[{idx}] missing period")

    source = data.get("source")
    if source == "lyst-index" and snapshots:
        latest = snapshots[0]
        if isinstance(latest, dict):
            check_rank_values(latest.get("brands"), path, "latest brands", errors)
            check_rank_values(latest.get("products"), path, "latest products", errors)
    elif source == "stockx" and snapshots:
        for idx, snapshot in enumerate(snapshots, start=1):
            if isinstance(snapshot, dict) and "ranking" in snapshot:
                errors.append(f"{path}: snapshots[{idx}] must not collapse StockX data into a single ranking list")
    elif source == "musinsa" and snapshots:
        latest = snapshots[0]
        if isinstance(latest, dict):
            check_rank_values(latest.get("brands"), path, "latest brands", errors)
    elif source == "kream" and snapshots:
        latest = snapshots[0]
        if isinstance(latest, dict):
            if "brand_top" not in latest:
                errors.append(f"{path}: latest KREAM snapshot missing brand_top")
            if "menswear_read" not in latest:
                errors.append(f"{path}: latest KREAM snapshot missing menswear_read")
    return CheckResult(str(path.relative_to(ROOT)), errors)


def check_yaml_parseable(path: Path) -> CheckResult:
    """無專屬契約的 data YAML 最低防線：可解析、頂層是 mapping。

    新 data 檔（如 trend_history / decision_guards）不必逐一註冊就有
    broken-YAML 防護；要加欄位契約時再升級成專屬 check。
    """
    errors: list[str] = []
    try:
        require_mapping(load_yaml(path), path, errors)
    except yaml.YAMLError as exc:
        errors.append(f"{path}: YAML 無法解析：{exc}")
    return CheckResult(str(path.relative_to(ROOT)), errors)


def check_data() -> list[CheckResult]:
    results = [check_sources(), check_brands(), check_people(), check_taxonomy()]
    covered = {DATA_DIR / name for name in ("sources.yml", "brands.yml", "people.yml", "trend_taxonomy.yml")}
    for path in sorted(RANKINGS_DIR.glob("*.yml")):
        results.append(check_ranking_file(path))
        covered.add(path)
    for path in sorted(DATA_DIR.rglob("*.yml")):
        if path not in covered:
            results.append(check_yaml_parseable(path))
    return results


TEMPLATE_REQUIREMENTS = {
    "daily_brief_template.md": ["{{date}}", "## 📌 今日三行", "## 🔥 今日重點趨勢 Headline Trends", "## 🇯🇵 日潮 JP 追蹤", "## 🇰🇷 韓潮 KR 追蹤", "## 🌍 歐美 US-EU 追蹤", "## 🎯 對我最相關 For Me"],
    "trend_card_template.md": ["{{trend_name}}"],
    "weekly_buy_picks_template.md": ["{{week}}", "## 🧢 頭部", "## 👕 上身", "## 👖 下身", "## 👟 足部", "## 👜 配件", "## 🎯 本週最該記住的一個"],
    "ranking_snapshot_template.md": ["Lyst Index", "StockX", "snapshots:"],
    "monthly_heat_report_template.md": ["{{month}}", "## 🔥 本月最紅品牌", "## 來源 / 限制"],
}


def check_templates() -> list[CheckResult]:
    results: list[CheckResult] = []
    for filename, required_bits in TEMPLATE_REQUIREMENTS.items():
        path = TEMPLATES_DIR / filename
        errors: list[str] = []
        if not path.exists():
            errors.append(f"{path}: missing template")
        else:
            text = path.read_text(encoding="utf-8")
            for bit in required_bits:
                if bit not in text:
                    errors.append(f"{path}: missing required text {bit!r}")
        results.append(CheckResult(f"templates/{filename}", errors))
    return results


REPORT_PATTERNS = {
    "daily": re.compile(r"^\d{4}-\d{2}-\d{2}\.md$"),
    "monthly": re.compile(r"^\d{4}-\d{2}-[a-z-]+\.md$"),
    "buy_shortlist": re.compile(r"^\d{4}-W\d{2}\.md$"),  # 週挑（ISO 週，D3）
}


def check_reports() -> list[CheckResult]:
    results: list[CheckResult] = []
    for subdir, pattern in REPORT_PATTERNS.items():
        path = REPORTS_DIR / subdir
        errors: list[str] = []
        if not path.exists():
            errors.append(f"{path}: missing directory")
        else:
            for report in sorted(path.glob("*.md")):
                # *.draft.md 是 gitignored 的中間產物（產骨架→填→改名/刪），不入版控、
                # 跟 .gitignore 一致地略過，否則本機產 draft 就誤報檔名不符。
                if report.name.endswith(".draft.md"):
                    continue
                if not pattern.match(report.name):
                    errors.append(f"{report}: filename does not match {pattern.pattern}")
                text = report.read_text(encoding="utf-8").strip()
                if not text.startswith("# "):
                    errors.append(f"{report}: report must start with a level-1 heading")
        results.append(CheckResult(f"reports/{subdir}", errors))
    return results


def print_results(results: list[CheckResult]) -> int:
    failed = False
    for result in results:
        if result.ok:
            print(f"✅ {result.name}")
        else:
            failed = True
            print(f"❌ {result.name}")
            for error in result.errors:
                print(f"   - {error}")
    return 1 if failed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Style Superman repo contracts")
    parser.add_argument("--data", action="store_true", help="only validate data YAML files")
    parser.add_argument("--templates", action="store_true", help="only validate templates")
    parser.add_argument("--reports", action="store_true", help="only validate report filenames/headings")
    args = parser.parse_args()

    selected = [args.data, args.templates, args.reports]
    run_all = not any(selected)

    try:
        results: list[CheckResult] = []
        if run_all or args.data:
            results.extend(check_data())
        if run_all or args.templates:
            results.extend(check_templates())
        if run_all or args.reports:
            results.extend(check_reports())
    except RuntimeError as exc:
        print(f"⚠️  {exc}")
        raise SystemExit(1)

    raise SystemExit(print_results(results))


if __name__ == "__main__":
    main()
