#!/usr/bin/env python3
"""
ingest_ranking_snapshot.py
==========================
安全地把「一筆新的排行快照」加進 data/rankings/<source>.yml。

目的：降低手填 Lyst / StockX / KREAM / MUSINSA 快照的出錯風險。
先 **dry-run** 檢查（預設行為，不寫檔），確認格式與契約都對，再加 `--write` 真正寫入。
寫入時用**文字插入**把新快照放到 `snapshots:` 最上面，**不重新序列化整個檔**，
所以既有快照的註解與排版都不會被破壞。

用法：
    # 檢查（不寫檔）——預設
    python scripts/ingest_ranking_snapshot.py --source lyst --input /tmp/lyst_q2.yml

    # 從 stdin 讀
    cat /tmp/lyst_q2.yml | python scripts/ingest_ranking_snapshot.py --source lyst

    # 通過檢查後真正寫入
    python scripts/ingest_ranking_snapshot.py --source lyst --input /tmp/lyst_q2.yml --write

輸入格式：一段 YAML，內容是「一筆 snapshot」——可以是
    - 單一 mapping（period: ... 開頭），或
    - 只含一個 mapping 的 list（- period: ... 開頭）
格式見 templates/ranking_snapshot_template.md。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
RANKINGS_DIR = ROOT / "data" / "rankings"

SOURCES = {
    "lyst": "lyst-index.yml",
    "stockx": "stockx.yml",
    "kream": "kream.yml",
    "musinsa": "musinsa.yml",
}
# 檔案內 `source:` 欄位的值（顯示用標籤；跨來源誤投由 validate_snapshot 的欄位檢查擋下）
SOURCE_FIELD = {
    "lyst": "lyst-index",
    "stockx": "stockx",
    "kream": "kream",
    "musinsa": "musinsa",
}


def fail(msg: str) -> "None":
    print(f"⚠️  {msg}")
    raise SystemExit(1)


def load_input(path: str | None) -> tuple[dict, str]:
    """讀輸入（檔案或 stdin），回傳 (snapshot dict, 原始文字)。"""
    if path:
        raw = Path(path).read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            fail("沒有 --input 也沒有 stdin 輸入。請提供新快照 YAML。")
        raw = sys.stdin.read()

    if not raw.strip():
        fail("輸入是空的。")

    parsed = yaml.safe_load(raw)
    # 接受 list[1] 或單一 mapping
    if isinstance(parsed, list):
        if len(parsed) != 1:
            fail(f"輸入應只含 1 筆 snapshot，實際有 {len(parsed)} 筆。")
        snapshot = parsed[0]
    elif isinstance(parsed, dict):
        snapshot = parsed
    else:
        fail("輸入無法解析成 snapshot（需為 mapping 或單元素 list）。")
    if not isinstance(snapshot, dict):
        fail("snapshot 必須是 mapping（key: value）。")
    return snapshot, raw


def existing_periods(target_path: Path) -> tuple[list, dict]:
    """回傳 (現有 period 清單, 目標檔解析後的 dict)。"""
    data = yaml.safe_load(target_path.read_text(encoding="utf-8")) or {}
    snaps = data.get("snapshots") or []
    periods = [s.get("period") for s in snaps if isinstance(s, dict)]
    return periods, data


# ---------- 各來源的 snapshot 契約檢查 ----------

def check_ranks(rows, label: str, errors: list[str], required_fields: tuple[str, ...] = ()) -> int:
    if not isinstance(rows, list):
        errors.append(f"{label} 必須是 list")
        return 0
    ranks = []
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            errors.append(f"{label}[{i}] 必須是 mapping")
            continue
        rank = row.get("rank")
        # bool 是 int 的子類別——True/False 不可當名次（否則 rank: true 會被當成 1）
        if not isinstance(rank, int) or isinstance(rank, bool):
            errors.append(f"{label}[{i}] rank 必須是整數")
        else:
            ranks.append(rank)
        # 顯示/比對主鍵也要驗（brands→name、products→brand+item）：track_rankings 與月報直接
        # 用 row["name"]/row["brand"] subscript，缺了會在產出時 KeyError 而非寫入時擋下。
        for field in required_fields:
            if not row.get(field):
                errors.append(f"{label}[{i}] 缺 {field}")
    if len(ranks) != len(set(ranks)):
        errors.append(f"{label} 有重複 rank")
    return len(rows)


def validate_snapshot(source: str, snap: dict) -> tuple[list[str], list[str]]:
    """回傳 (errors, info)。errors 非空代表不可寫入。"""
    errors: list[str] = []
    info: list[str] = []

    period = snap.get("period")
    if not period:
        errors.append("缺 period（或為空）")
    elif not isinstance(period, str):
        # 非字串 period（YAML 把 2026 當 int、2026-01-01 當 date）會讓重複檢查靜默失效
        errors.append(f"period 必須是字串（{period!r} 被 YAML 解析成 {type(period).__name__}，請加引號）")
    else:
        info.append(f"period = {period}")

    if source == "lyst":
        n_b = check_ranks(snap.get("brands"), "brands", errors, ("name",))
        n_p = check_ranks(snap.get("products"), "products", errors, ("brand", "item"))
        info.append(f"brands {n_b} 筆、products {n_p} 筆")
    elif source == "stockx":
        if "ranking" in snap:
            errors.append("StockX 不可把資料壓成單一 'ranking' list（口徑要分開）")
        known = [k for k in ("best_seller_sneaker", "apparel_top", "accessory_top",
                             "all_time_best_seller", "notable_new_models",
                             "fastest_growing_brands") if k in snap]
        if not known:
            errors.append("StockX snapshot 沒有任何已知欄位（best_seller_sneaker 等）")
        else:
            info.append(f"欄位：{', '.join(known)}")
    elif source == "kream":
        # 與 validate_repo 對齊：KREAM 以 brand_top 為頭、必帶男裝視角
        for required in ("brand_top", "menswear_read"):
            if required not in snap:
                errors.append(f"KREAM snapshot 缺 {required}")
        bt = snap.get("brand_top")
        if isinstance(bt, dict) and bt.get("name"):
            info.append(f"brand_top = {bt['name']}")
    elif source == "musinsa":
        # 與 validate_repo 對齊：MUSINSA 是品牌銷售榜，brands rank 不可重複、name 不可缺
        n_b = check_ranks(snap.get("brands"), "brands", errors, ("name",))
        if "menswear_read" not in snap:
            errors.append("MUSINSA snapshot 缺 menswear_read")
        info.append(f"brands {n_b} 筆")

    return errors, info


def build_block(snap: dict) -> str:
    """把 snapshot 重新輸出成可插在 snapshots: 底下的 2-space list item。"""
    dumped = yaml.dump([snap], sort_keys=False, allow_unicode=True, default_flow_style=False)
    # 整段縮排 2 格，放到 `snapshots:` 之下
    return "".join(f"  {line}" if line.strip() else line for line in dumped.splitlines(keepends=True))


def write_snapshot(target_path: Path, snap: dict) -> None:
    """把新 snapshot 文字插到 `snapshots:` 行的正下方，保留檔內既有註解與排版。
    寫前先在記憶體驗證插入後仍是合法 YAML 且新 period 確實進去——這是唯一程式化寫 data 檔的點，
    寧可放棄寫入也不把壞檔留在磁碟上。"""
    lines = target_path.read_text(encoding="utf-8").splitlines(keepends=True)
    idx = next((i for i, ln in enumerate(lines) if ln.rstrip() == "snapshots:"), None)
    if idx is None:
        fail(f"{target_path.name} 找不到 `snapshots:` 行，無法插入。")
    block = build_block(snap)
    if not block.endswith("\n"):
        block += "\n"
    lines.insert(idx + 1, block)
    new_text = "".join(lines)

    # 寫前自驗：插入後還能 parse、且新 period 真的在 snapshots 裡（檔案此刻尚未被動）
    try:
        reparsed = yaml.safe_load(new_text) or {}
    except yaml.YAMLError as e:
        fail(f"插入後 YAML 解析失敗，已放棄寫入（檔案未動）：{e}")
    periods_after = [s.get("period") for s in (reparsed.get("snapshots") or []) if isinstance(s, dict)]
    if snap.get("period") not in periods_after:
        fail("插入後在 snapshots 找不到新 period，疑似插錯位置，已放棄寫入（檔案未動）。")

    target_path.write_text(new_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="安全加入一筆排行快照（預設 dry-run）")
    parser.add_argument("--source", choices=list(SOURCES), required=True)
    parser.add_argument("--input", help="新快照 YAML 檔；省略則讀 stdin")
    parser.add_argument("--write", action="store_true", help="通過檢查後真正寫入（預設只 dry-run）")
    args = parser.parse_args()

    if yaml is None:
        fail("需要 pyyaml：pip install -r requirements.txt")

    target_path = RANKINGS_DIR / SOURCES[args.source]
    if not target_path.exists():
        fail(f"找不到目標檔：{target_path}")

    snap, _raw = load_input(args.input)

    errors, info = validate_snapshot(args.source, snap)

    # 跨檔檢查：period 不可與既有重複
    periods, _data = existing_periods(target_path)
    period = snap.get("period")
    if period and period in periods:
        errors.append(f"period {period!r} 已存在於 {target_path.name}，不可重複 ingest")

    print(f"來源：{args.source}（{SOURCE_FIELD[args.source]}）→ {target_path.relative_to(ROOT)}")
    for line in info:
        print(f"  · {line}")
    print(f"  · 既有 snapshots：{len(periods)} 筆 {periods if periods else ''}")

    if errors:
        print("\n❌ 檢查未通過：")
        for e in errors:
            print(f"   - {e}")
        raise SystemExit(1)

    print("\n✅ 契約檢查通過。")

    if not args.write:
        print("（DRY RUN — 未寫入。確認無誤後加 --write 真正寫入。）")
        return

    write_snapshot(target_path, snap)
    print(f"✍️  已將 {period} 插入 {target_path.name} 的 snapshots 最上方。")
    print("   下一步請自驗：")
    print(f"     python scripts/validate_repo.py --data")
    print(f"     python scripts/track_rankings.py --source {args.source} --compare")


if __name__ == "__main__":
    main()
