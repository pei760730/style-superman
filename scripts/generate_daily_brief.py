#!/usr/bin/env python3
"""
generate_daily_brief.py
=======================
產出當日 Daily Brief 的「骨架」草稿。

這支腳本不做 AI 撰寫，它負責：
  1. 讀取 data/ 下的設定（sources / taxonomy / brands / people）
  2. 載入 templates/daily_brief_template.md
  3. 填入日期與來源摘要，產出一份待填的 draft
  4. 把 draft 寫到 reports/daily/YYYY-MM-DD.md

之後由對話 agent（prompts/daily_trend_brief.md）判讀與撰寫實際內容。
收訊號走 collect_raw_signals.py（RSS）；repo 內不呼叫 LLM API（D5），腳本只產骨架。

用法：
    python scripts/generate_daily_brief.py                # 用今天日期
    python scripts/generate_daily_brief.py --date 2026-06-04
    python scripts/generate_daily_brief.py --draft        # 輸出成 *.draft.md（不入版控）
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

# Windows 終端機預設 cp950，emoji / 中文會炸。強制 stdout 走 UTF-8。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TEMPLATE = ROOT / "templates" / "daily_brief_template.md"
OUT_DIR = ROOT / "reports" / "daily"


def load_yaml(path: Path) -> dict:
    """安全載入 YAML；缺套件或缺檔時回傳空 dict 並提示。"""
    if yaml is None:
        print("⚠️  未安裝 pyyaml，略過讀取設定。請 `pip install pyyaml`。")
        return {}
    if not path.exists():
        print(f"⚠️  找不到設定檔：{path}")
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def summarize_sources(sources: list[dict]) -> str:
    """把 sources 依 region 做一行摘要，放進 brief 底部供參考。"""
    by_region: dict[str, int] = {}
    for s in sources:
        by_region[s.get("region", "?")] = by_region.get(s.get("region", "?"), 0) + 1
    parts = [f"{region}: {count}" for region, count in sorted(by_region.items())]
    return " ｜ ".join(parts) if parts else "（無來源設定）"


def build_brief(date_str: str, rss_note: str = "") -> str:
    """把 template 填上日期與骨架佔位，回傳草稿全文。"""
    sources = load_yaml(DATA_DIR / "sources.yml").get("sources", [])

    if TEMPLATE.exists():
        body = TEMPLATE.read_text(encoding="utf-8")
    else:
        body = "# Style Superman — Daily Brief · {{date}}\n\n（找不到模板，請補 templates/daily_brief_template.md）\n"

    # 最小填充：日期與來源計數。其餘佔位留給 AI / 人工。
    body = body.replace("{{date}}", date_str)
    body = body.replace("{{signal_strength}}", "_待填_")
    body = body.replace("{{signal_count}}", "0")
    body = body.replace("{{headline_count}}", "0")

    footer = (
        f"\n\n---\n\n"
        f"<!-- 來源覆蓋：{summarize_sources(sources)} -->\n"
        f"{rss_note}"
        f"<!-- 下一步：用 prompts/daily_trend_brief.md 填入今日訊號 -->\n"
    )
    return body + footer


def collect_rss(out_path: str | None) -> str:
    """收集 RSS 來源成 raw_signal_pack（事實層）。回傳要附在 brief footer 的註解。

    抓取失敗一律優雅降級——即使完全沒網路也不中斷 brief 產出。
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import collect_raw_signals as crs
    except Exception as e:  # noqa: BLE001
        return f"<!-- RSS 收集略過：無法載入 collect_raw_signals（{e}） -->\n"

    sources = crs.rss_sources()
    signals, warnings = crs.collect(sources)

    if out_path:
        try:
            Path(out_path).write_text(crs.to_yaml(signals), encoding="utf-8")
            print(f"📥 raw_signal_pack：收集 {len(signals)} 則 → {out_path}")
        except OSError as e:
            print(f"⚠️  raw pack 寫入失敗：{e}")
    else:
        print(f"📥 raw_signal_pack：收集 {len(signals)} 則（未指定 --raw-signals-out，未寫檔）")

    if warnings:
        print(f"   （{len(warnings)} 個來源降級：{'; '.join(warnings[:3])}{' …' if len(warnings) > 3 else ''}）")

    out_hint = f"，已寫到 {out_path}" if out_path else "（未寫檔）"
    return (
        f"<!-- RSS 收集：{len(signals)} 則事實訊號、{len(warnings)} 來源降級{out_hint}；"
        f"signal_type/credibility 由 brief 主編 agent 判讀 -->\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="產出當日 Daily Brief 骨架")
    parser.add_argument("--date", help="YYYY-MM-DD，預設今天", default=None)
    parser.add_argument(
        "--draft",
        action="store_true",
        help="輸出成 *.draft.md（被 .gitignore 排除，不入版控）",
    )
    parser.add_argument(
        "--with-rss",
        action="store_true",
        help="收集有 RSS 的來源成 raw_signal_pack（事實層，需網路；失敗則優雅降級）",
    )
    parser.add_argument(
        "--raw-signals-out",
        help="把收集到的 raw_signal_pack 寫到此路徑（YAML）；需搭配 --with-rss",
    )
    args = parser.parse_args()

    if args.date:  # 無驗證會把 --date NOT-A-DATE 直接寫成 reports/daily/NOT-A-DATE.md（封存垃圾檔）
        try:
            dt.date.fromisoformat(args.date)
        except ValueError:
            parser.error(f"--date 須為合法 YYYY-MM-DD（收到 {args.date!r}）")
    date_str = args.date or dt.date.today().isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rss_note = ""
    if args.with_rss:
        rss_note = collect_rss(args.raw_signals_out)

    suffix = ".draft.md" if args.draft else ".md"
    out_path = OUT_DIR / f"{date_str}{suffix}"

    if out_path.exists():
        print(f"⚠️  {out_path.name} 已存在，未覆蓋。要重產請先刪除或改用 --draft。")
        return

    out_path.write_text(build_brief(date_str, rss_note), encoding="utf-8")
    print(f"✅ 已產出骨架：{out_path.relative_to(ROOT)}")
    print("   下一步：依 prompts/daily_trend_brief.md 用 AI 或人工補上今日趨勢內容。")


if __name__ == "__main__":
    main()
