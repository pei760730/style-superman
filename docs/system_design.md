# System Design — Style Superman

## 1. 定位

Style Superman 是一套 **Men's Fashion & Culture Intelligence System**（給我自己用的個人情報中樞）。它的工作不是收集文章，而是把每天的潮流雜訊，轉成「有觀點、可挑買 / 可行動」的個人情報。

設計上區分三種資產：

| 資產類型 | 位置 | 性質 | 誰維護 |
|----------|------|------|--------|
| 知識底層 | `data/` | 長期、低頻變動 | 人 + 機器逐步擴充 |
| 每日快照 | `reports/daily/` | 高頻、不可變 | 每日產出後封存 |
| 處理邏輯 | `scripts/` + `prompts/` + `templates/` | 規則與格式 | 隨系統演進 |

## 2. 資料流（Pipeline）

```
        ┌─────────────┐
        │  sources.yml │  ← 來源清單
        └──────┬──────┘
               │ (1) 收集 collect
               ▼
        ┌─────────────┐
        │ 原始訊號 raw │  ← collect_raw_signals.py（事實層，主編 agent 直接判讀）
        └──────┬──────┘
               │ (2) 分類 classify  ← trend_taxonomy.yml
               ▼
        ┌─────────────┐
        │ 分類後訊號   │ ──(週深挖旁支)──► trend cards：prompts/trend_analysis.md + templates/trend_card_template.md
        └──────┬──────┘
               │ (3) 簡報 brief  ← prompts/daily_trend_brief.md（趨勢挑選＝主編判斷，不走自動評分）
               ▼
        ┌─────────────┐
        │ Daily Brief  │ → reports/daily/YYYY-MM-DD.md
        └──────┬──────┘
               │ (4) 挑買 pick  ← brief For Me / 週挑（D9：不開獨立卡）
               ▼
        ┌─────────────┐
        │ 週挑清單     │ → templates/weekly_buy_picks_template.md
        └─────────────┘
```

## 3. 五個處理階段

1. **收集 Collect** — 依 `sources.yml` 取得當日訊號。現階段人工 / 半自動；`rss` 欄位已為自動化預留。
2. **分類 Classify** — 用 `trend_taxonomy.yml` 把訊號歸類、掛標籤。主編 agent 直接判讀 raw_signal_pack（中間 insight 層已於 2026-06-11 移除——從未實際運轉；趨勢加權評分 score_trends 已於 2026-06-14 移除——D14，趨勢挑選回歸主編判斷）。
3. **簡報 Brief** — `daily_trend_brief` prompt 產出當日 brief，封存到 `reports/daily/`。趨勢卡（`trend_analysis` prompt）是週深挖旁支，不在每日關鍵路徑上。
4. **對我最相關（在紅單品）** — brief 的 🎯 For Me 是情報層（單品｜是什麼｜在哪紅｜對我的意義｜價格/型號辨識用）,讓擁有者知道現在在紅什麼,**非買清單**（D15，2026-06-14）;不開獨立挑買卡（D9）,真要入手隨選再做定番調研（D10）。

## 4. 人機分工

- **腳本**：確定性的工作——填模板、算分數、排序、檔案管理。
- **AI（prompts）**：語意工作——判斷、摘要、撰寫、挑買建議。
- **人（我）**：拍板——最終取捨、品味、買不買。

刻意不讓 AI 全自動下結論。系統的價值是「幫我快」，不是「取代我的判斷」。

## 5. 擴充點（自動化現況與未來）

| 階段 | 現在 | 未來接什麼 |
|------|------|-----------|
| 收集 | RSS 半自動（`collect_raw_signals.py`）+ 人工巡檢 | 更多來源（非 RSS API；新增需人類拍板） |
| 分類/簡報 | AI 撰寫由對話中的 agent / 排程雲端 agent 做（**不接 repo 內 LLM API**，決策 D5） | — |
| 排程 | 月報由每月 1 號雲端 agent 自動產；daily 骨架每日 schedule 自動產（`daily-brief.yml`，2026-06-10 拍板開啟）+ 可手動 dispatch | — |
| 推送 | 無 | Telegram / Notion / Sheets（未拍板，先手動跑順再說） |
| 儲存 | Markdown 檔 | 之後可加 DB / 向量檢索做歷史回顧 |
| 自我檢查 | `validate_repo.py`（格式契約）+ `repo_health.py`（產線新鮮度、文件↔程式碼漂移、決策守衛 `data/decision_guards.yml`）+ `health.yml` 週期巡檢（WARN 自動開 issue） | issue 連續兩週沒人理 → 修產線或調整節奏宣告（lessons） |

## 6. 設計原則

1. **資料與內容分離** — 底層知識不被每日快照污染。
2. **格式即契約** — 所有產出走 `templates/`，下游工具好解析。
3. **先輕後重** — 先把流程跑順、累積資料，再決定上不上重型自動化（避免過早工程化）。
4. **可解釋的判斷** — 結論一定附理由與來源，不做黑箱（趨勢挑選＝主編判斷，不走自動評分，D14）。
5. **誠實** — 訊號弱就說弱，不確定就標「待驗證」，不編造熱度。
