# System Design — Style Superman

## 1. 定位

Style Superman 是一套 **Men's Fashion & Culture Intelligence System**。它的工作不是收集文章，而是把每天的潮流雜訊，轉成「有觀點、可評分、可變現」的情報。

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
        ┌─────────────┐     prompts/article_to_insight.md
        │ 原始訊號 raw │ ───────────────► 結構化 insight
        └──────┬──────┘
               │ (2) 分類 classify  ← trend_taxonomy.yml
               ▼
        ┌─────────────┐     prompts/trend_analysis.md
        │ trend cards  │ ───────────────► templates/trend_card_template.md
        └──────┬──────┘
               │ (3) 評分 score  ← scripts/score_trends.py
               ▼
        ┌─────────────┐
        │ 排序後趨勢   │
        └──────┬──────┘
               │ (4) 簡報 brief  ← prompts/daily_trend_brief.md
               ▼
        ┌─────────────┐
        │ Daily Brief  │ → reports/daily/YYYY-MM-DD.md
        └──────┬──────┘
               │ (5) 選題 ideate  ← prompts/short_video_ideas.md
               ▼
        ┌─────────────┐
        │ 內容選題卡   │ → templates/short_video_idea_template.md
        └─────────────┘
```

## 3. 五個處理階段

1. **收集 Collect** — 依 `sources.yml` 取得當日訊號。現階段人工 / 半自動；`rss` 欄位已為自動化預留。
2. **分類 Classify** — 用 `trend_taxonomy.yml` 把訊號歸類、掛標籤。`article_to_insight` 負責榨乾單篇。
3. **評分 Score** — `score_trends.py` 用加權公式排序，決定主打 / 採用 / 觀察 / 暫存。
4. **簡報 Brief** — `daily_trend_brief` prompt 產出當日 brief，封存到 `reports/daily/`。
5. **選題 Ideate** — `short_video_ideas` prompt 把趨勢轉成可拍選題。

## 4. 人機分工

- **腳本**：確定性的工作——填模板、算分數、排序、檔案管理。
- **AI（prompts）**：語意工作——判斷、摘要、撰寫、選題。
- **人**：拍板——最終取捨、品味、與品牌調性的對齊。

刻意不讓 AI 全自動發布。系統的價值是「幫人快」，不是「取代人的判斷」。

## 5. 擴充點（未來自動化）

| 階段 | 現在 | 未來接什麼 |
|------|------|-----------|
| 收集 | 人工 / RSS 欄位預留 | RSS reader、IG/TikTok API、爬蟲 |
| 分類/簡報 | 手動跑 prompt | LLM API（Claude / OpenAI）自動撰寫 |
| 排程 | 手動 | GitHub Actions（`daily-brief.yml`）/ n8n |
| 推送 | 無 | Telegram bot、Notion、Google Sheets |
| 儲存 | Markdown 檔 | 之後可加 DB / 向量檢索做歷史回顧 |

## 6. 設計原則

1. **資料與內容分離** — 底層知識不被每日快照污染。
2. **格式即契約** — 所有產出走 `templates/`，下游工具好解析。
3. **先輕後重** — 先把流程跑順、累積資料，再決定上不上重型自動化（避免過早工程化）。
4. **可解釋的評分** — 分數一定附理由，不做黑箱。
5. **誠實** — 訊號弱就說弱，不確定就標「待驗證」，不編造熱度。
