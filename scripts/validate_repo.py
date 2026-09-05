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
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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
        # D36（2026-07-28）：`body_fetchable: false` 是**量出來的**，不是與生俱來的屬性——
        # 六個源被 2026-06-14 的 WebFetch 視角誤判成「不可讀」，本機實測全 200。
        # 所以要封一個源的正文，必須留下「哪個視角、哪天量的」，否則下次沒人知道該不該複驗。
        if source.get("body_fetchable") is False:
            note = source.get("body_fetch_note")
            if not (isinstance(note, str) and re.search(r"\d{4}-\d{2}-\d{2}", note) and "本機" in note):
                errors.append(
                    f"{path}: source {source.get('id', idx)!r} 標了 body_fetchable: false，"
                    "必須附 body_fetch_note（含本機實測日期 YYYY-MM-DD）"
                    "——403 是「誰在看」的陳述，不得只憑遠端視角封源（D36）"
                )
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


def _published_key(value: Any) -> tuple[int, int, int] | None:
    """把 `published` 轉成可比較的 (年, 月, 日)。只到月的當月 0 日——同月的
    `2026-01` 與 `2026-01-31` 因此不會被判成逆序（月精度本來就無法分辨日）。"""
    text = str(value or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.match(r"^(\d{4})-(\d{2})$", text)
    if m:
        return int(m.group(1)), int(m.group(2)), 0
    return None


def check_snapshot_order(snapshots: list, path: Path, errors: list[str]) -> None:
    """`snapshots:` 必須最新在最上方——CLAUDE.md 核心假設 #6。

    2026-09-05 稽核：這條是明文不可破壞假設，卻**零機器守衛**，而有 6 個程式點依賴它
    （`repo_health.check_ranking_snapshot_ages` / `check_lyst_staleness`、`validate_repo` 的
    latest 驗證、`generate_weekly_buy_picks.latest_ranking_periods`、
    `generate_monthly_heat_report.latest_period`、`track_rankings.lyst_comparison_text`）。
    對話端 AI 依 `prompts/ranking_ingest.md` 編 yaml 時**最自然的動作是 append 到最後**，
    一旦這麼做：repo_health 會印最舊那筆的年齡（#231 想解的「三檔 75 天沒人知道」直接反向復發）、
    週挑／月報引用過期 period——**全部靜默**。
    """
    rows = [(i, s) for i, s in enumerate(snapshots, start=1) if isinstance(s, dict)]
    if len(rows) < 2:
        return  # 只有 0–1 筆時「順序」不是承重的，也就沒有可違反的不變式
    keys = []
    for idx, snapshot in enumerate(snapshots, start=1):
        if not isinstance(snapshot, dict):
            continue
        key = _published_key(snapshot.get("published"))
        if key is None:
            # ≥2 筆時每一筆都必須可定日期——否則排序守衛會 fail-open，
            # 而下游 6 個程式點仍照 snapshots[0] 取「最新」。
            errors.append(
                f"{path}: snapshots[{idx}] published {snapshot.get('published')!r} "
                f"無法解析（須為 YYYY-MM-DD 或 YYYY-MM）；本檔有 {len(rows)} 筆快照，"
                f"順序守衛需要每一筆都可定日期"
            )
            continue
        keys.append((idx, key, snapshot.get("published")))
    for (i1, k1, p1), (i2, k2, p2) in zip(keys, keys[1:]):
        if k1 < k2:
            errors.append(
                f"{path}: snapshots 必須最新在最上方（CLAUDE.md 核心假設 #6），"
                f"但 snapshots[{i1}] published={p1!r} 比 snapshots[{i2}] published={p2!r} 舊。"
                f"新快照請 **插到最前面**，不要 append 到最後"
            )


def check_rank_values(items: Any, path: Path, label: str, errors: list[str],
                      required_fields: tuple[str, ...] = ()) -> None:
    rows = require_list(items, f"{path}: {label}", errors)
    ranks: list[Any] = []
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"{path}: {label}[{idx}] must be a mapping")
            continue
        rank = row.get("rank")
        if not isinstance(rank, int) or isinstance(rank, bool):
            errors.append(f"{path}: {label}[{idx}] rank must be an integer")
        else:
            ranks.append(rank)
        # 顯示/比對主鍵（brands→name、products→brand+item）也要驗：track_rankings 與月報
        # 用 row["name"]/row["brand"] 直接 subscript，缺了會在產出時 KeyError 而非寫入時擋下。
        for field in required_fields:
            if not row.get(field):
                errors.append(f"{path}: {label}[{idx}] missing {field}")
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

    check_snapshot_order(snapshots, path, errors)

    source = data.get("source")
    if source == "lyst-index" and snapshots:
        # ⚠️ 不能只驗 snapshots[0]：`track_rankings.lyst_comparison_text` 做季對季比對時
        # 讀的是 **snaps[1]**（前一季），而月報 🆚 段直接 import 它。2026-09-05 實測：
        # snapshots[1] 的 brands 缺一個 `name` → validate_repo 回 0 errors 放行，
        # 產月報時 KeyError('name') 被 generate_monthly_heat_report 的 except 吞掉，
        # 🆚 段變成「（基準變動計算失敗：'name'）」——而那段是 D38 的「硬數據脊椎」。
        for pos, snapshot in enumerate(snapshots[:2]):
            if not isinstance(snapshot, dict):
                continue
            tag = "latest" if pos == 0 else "previous"
            check_rank_values(snapshot.get("brands"), path, f"{tag} brands", errors, ("name",))
            check_rank_values(snapshot.get("products"), path, f"{tag} products", errors, ("brand", "item"))
    elif source == "stockx" and snapshots:
        for idx, snapshot in enumerate(snapshots, start=1):
            if isinstance(snapshot, dict) and "ranking" in snapshot:
                errors.append(f"{path}: snapshots[{idx}] must not collapse StockX data into a single ranking list")
    elif source == "musinsa" and snapshots:
        latest = snapshots[0]
        if isinstance(latest, dict):
            check_rank_values(latest.get("brands"), path, "latest brands", errors, ("name",))
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
    # yaml 為 None（缺 pyyaml）時，load_yaml 先丟 RuntimeError；此處不可寫 `except yaml.YAMLError`，
    # 否則求值 None.YAMLError → AttributeError 蓋掉 RuntimeError、逃出 main() 的 RuntimeError 處理，
    # 變成醜 traceback 而非 CLAUDE.md 要求的「缺 pyyaml 明確回報」。缺套件時放行 RuntimeError 上拋。
    yaml_error = yaml.YAMLError if yaml is not None else ()
    try:
        require_mapping(load_yaml(path), path, errors)
    except yaml_error as exc:
        errors.append(f"{path}: YAML 無法解析：{exc}")
    return CheckResult(str(path.relative_to(ROOT)), errors)


def _check_reader_example_node(
    value: Any, schema: dict[str, Any], layer: str, errors: list[str]
) -> None:
    """依 reader schema 檢查範例的 required、未知 key 與 enum。"""
    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(value, dict):
            errors.append(f"reader_output_schema：{layer} 必須是 object")
            return
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"reader_output_schema：{layer} 缺少必填欄位 {key!r}")
        for key, child in value.items():
            if key not in properties:
                errors.append(f"reader_output_schema：{layer} 出現 schema 未定義欄位 {key!r}")
                continue
            _check_reader_example_node(child, properties[key], f"{layer}.{key}", errors)
    elif schema_type == "array":
        if not isinstance(value, list):
            errors.append(f"reader_output_schema：{layer} 必須是 array")
            return
        item_schema = schema.get("items", {})
        for index, child in enumerate(value):
            _check_reader_example_node(child, item_schema, f"{layer}[{index}]", errors)

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        errors.append(f"reader_output_schema：{layer} 的值 {value!r} 不在 enum {enum!r} 內")


def check_reader_schema_contract() -> CheckResult:
    """確保 region reader 的 JSON 範例與 reader_output_schema 同步。"""
    errors: list[str] = []
    schema_path = DATA_DIR / "scan_units.yml"
    prompt_path = ROOT / "prompts" / "region_reader.md"
    data = require_mapping(load_yaml(schema_path), schema_path, errors)
    schema = data.get("reader_output_schema")
    if not isinstance(schema, dict):
        errors.append("reader_output_schema：data/scan_units.yml 缺少 object schema")
        return CheckResult("reader_output_schema", errors)

    text = prompt_path.read_text(encoding="utf-8")
    heading_at = text.find("## 輸出範例")
    if heading_at < 0:
        errors.append("reader_output_schema：prompts/region_reader.md 缺少「## 輸出範例」")
        return CheckResult("reader_output_schema", errors)
    match = re.search(r"```json\s*\n(.*?)\n```", text[heading_at:], re.DOTALL)
    if match is None:
        errors.append("reader_output_schema：輸出範例下找不到第一個 json 圍籬區塊")
        return CheckResult("reader_output_schema", errors)
    try:
        example = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        errors.append(f"reader_output_schema：輸出範例不是合法 JSON：{exc}")
        return CheckResult("reader_output_schema", errors)

    _check_reader_example_node(example, schema, "頂層", errors)
    return CheckResult("reader_output_schema", errors)


def check_data() -> list[CheckResult]:
    results = [check_sources(), check_brands(), check_people(), check_taxonomy(), check_reader_schema_contract()]
    covered = {DATA_DIR / name for name in ("sources.yml", "brands.yml", "people.yml", "trend_taxonomy.yml", "scan_units.yml")}
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
    "weekly_buy_picks_template.md": ["{{week}}", "## 🧢 頭部", "## 👕 上身", "## 👖 下身", "## 👟 足部", "## 👜 配件", "## 🎯 本週最該記住的一個", "**上週複驗：**"],
    "ranking_snapshot_template.md": ["Lyst Index", "StockX", "snapshots:"],
    "monthly_heat_report_template.md": ["{{month}}", "## 🔥 本月最紅品牌", "## 來源 / 限制"],
    # collect_raw_signals.py 的離線輸出格式範例，不是給寫手填的產出模板——
    # 契約由 test_collect_raw_signals 直接對 yaml 結構驗，這裡刻意留空。
    # （2026-09-05：這支原本完全沒登記，`test_every_template_file_has_a_contract_entry` 才抓到）
    "raw_signal_pack_template.md": [],
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
    # ⚡ flash 速報歷史檔（原 flash-brief.yml 機械產；D35 起對話觸發、新產出對話即讀不 commit）——
    #    檔名/標題跑掉不會被抓（與 daily 同日期格式 + H1）。2026-06-16 補上守門。
    "flash": re.compile(r"^\d{4}-\d{2}-\d{2}\.md$"),
    "monthly": re.compile(r"^\d{4}-\d{2}-[a-z-]+\.md$"),
    "buy_shortlist": re.compile(r"^\d{4}-W\d{2}\.md$"),  # 週挑（ISO 週，D3）
}

# D16（2026-06-14）：daily brief 對話即焚、不入 reports/daily/、不 commit。擁有者要的是「讀，喜歡的自己記」。
# 06-16（最後一個歷史 daily）以前的檔 grandfathered；之後任何被 commit 進來的 daily brief 都是違規——
# 多為平行 session 走 D16 前的舊存檔習慣（06-23 routine、06-24/25/26 session 連四犯，純文件規則擋不住）。
# 這條 gate 把違規檔變 CI 紅、PR merge 不了，從「靠記性」升級成「機制擋死」（CLAUDE.md：反覆出現才硬化、警告必配修復）。
DAILY_FREEZE_CUTOFF = "2026-06-16"

# D35（2026-07-25）：flash 速報同款收斂——改純對話觸發、對話即讀不 commit（flash-brief
# workflow 已刪）。歷史檔（D19 機械產期）grandfathered；凍結線後被 commit 進 reports/flash/
# 的一律擋。與 D16 同型教訓：「不再新增」靠紀律必漂移（daily 曾連四犯），要靠機制擋。
FLASH_FREEZE_CUTOFF = "2026-07-25"


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
                    errors.append(
                        f"{report}: filename does not match {pattern.pattern}"
                        f"（若為本機暫存/實驗檔請刪除該檔，不要放寬此 regex；"
                        f"只有真要新增報告類型時才改 REPORT_PATTERNS）"
                    )
                elif subdir == "daily" and report.name[:-3] > DAILY_FREEZE_CUTOFF:
                    errors.append(
                        f"{report}: D16 違規——daily brief 對話即焚、不得 commit 進 reports/daily/"
                        f"（凍結線 {DAILY_FREEZE_CUTOFF}，之後的 daily 一律擋；歷史檔 grandfathered）。"
                        f"請刪除此檔——擁有者要的是『讀、喜歡的自己記』，不存整份 brief。"
                    )
                elif subdir == "flash" and report.name[:-3] > FLASH_FREEZE_CUTOFF:
                    errors.append(
                        f"{report}: D35 違規——flash 速報對話即讀、不得 commit 進 reports/flash/"
                        f"（凍結線 {FLASH_FREEZE_CUTOFF}，之後的 flash 一律擋；歷史檔 grandfathered）。"
                        f"請刪除此檔。"
                    )
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
