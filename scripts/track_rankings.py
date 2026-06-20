#!/usr/bin/env python3
"""
track_rankings.py
=================
Lyst 季對季名次比對的**純函式 helper**，供 `generate_monthly_heat_report.py`
月報骨架的 `## 🆚 對照量化基準` 段使用。不讀檔、不印出（caller 傳入已 load 的 dict）。

2026-06-20（D21）：移除人工 CLI（看榜指令）與 `ingest_ranking_snapshot.py`（存榜助手）。
擁有者只走對話、從不打指令看檔——那兩個人工操作介面機器無呼叫者、人類也無使用者（出生即死）。
排行快照改由 AI 在對話中直接編輯 `data/rankings/*.yml`（格式見 `templates/ranking_snapshot_template.md`，
排序/口徑細則見 `docs/rankings.md`）。此檔僅保留月報真正 import 的兩個函式。
"""

from __future__ import annotations


def snapshots(data: dict) -> list[dict]:
    """快照清單，最新在前（檔案本就最新放最上）。"""
    return data.get("snapshots", [])


def lyst_comparison_text(data: dict, top: int | None = None) -> str | None:
    """比對最新兩季品牌名次（用我們自己的歷史，而非來源標示），回傳格式化字串。
    快照不足 2 筆回傳 None。top 限制顯示前 N 名（None＝全部）。供月報骨架使用。

    前季若是殘缺快照（`coverage: partial`，如媒體轉載 Top 10、非官方完整 Top 20），
    「不在前季榜上」≠ 真的新進榜——會吐一堆假「🆕 新進榜」。偵測到就標警告、把無法判定的
    標明、並略過「掉出榜外」（殘缺榜本來就沒列全），改提示看快照內建 move 欄。"""
    snaps = snapshots(data)
    if len(snaps) < 2:
        return None

    new, old = snaps[0], snaps[1]
    old_partial = "partial" in str(old.get("coverage", "")).lower()
    old_rank = {b["name"]: b["rank"] for b in old.get("brands", [])}
    lines = [f"📊  Lyst 品牌名次：{old.get('period')} → {new.get('period')}", "  " + "-" * 48]
    if old_partial:
        lines.append(f"  ⚠ 前季（{old.get('period')}）為殘缺快照（{old.get('coverage')}）：")
        lines.append("     季對季變動不可靠，未匹配到的不代表新進榜。請改看各快照內建的 move 欄。")
        lines.append("  " + "-" * 48)
    brands = new.get("brands", [])
    for b in brands[: top or len(brands)]:
        name, rank = b["name"], b["rank"]
        if name not in old_rank:
            change = "－（前季殘缺，無法判定）" if old_partial else "🆕 新進榜"
        else:
            diff = old_rank[name] - rank  # 名次變小 = 上升
            change = "— 持平" if diff == 0 else (f"↑ {diff}" if diff > 0 else f"↓ {abs(diff)}")
        lines.append(f"  {rank:>2}. {name:<18} {change}")

    # 前季殘缺時「掉出榜外」無意義（殘缺榜沒列全），略過不誤導
    if not old_partial:
        dropped = [n for n in old_rank if n not in {b["name"] for b in brands}]
        if dropped:
            lines.append(f"\n  掉出榜外：{', '.join(dropped)}")
    return "\n".join(lines)
