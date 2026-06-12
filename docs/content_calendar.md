# Flow Calendar — Style Superman

這份文件定義流程：**daily brief → 每週挑買 → 每月速報 → 主題分析**。它是流程 / 架構文件，不新增排名、銷量、百分比或未驗證趨勢結論。
（檔名沿用 `content_calendar.md` 以維持既有連結；定位已是個人興趣 + 挑買，非內容生產。）

核心目標：每天抓訊號、每週收斂成挑買決策、每月回看市場熱度、再把高價值議題沉澱成可長期引用的主題分析。

---

## 1. 流程總覽

```txt
原始來源 / 排行快照 / 社群與媒體訊號
        │
        ▼
Daily Brief（每日）：整理今日 3–5 個 headline trends + 🛒 對我有用
        │
        ├──► 每週挑買 shortlist：收斂 1–3 個真正想入手的方向
        │
        ▼
Monthly Heat Report（每月）：回看歐美品牌 / 單品熱度，標訊號層級與信心
        │
        ▼
Topic Analysis（每週至少一張，歐美優先）：把最強跨源趨勢寫成深挖卡
        │
        ▼
回饋資料層與評分規則：更新來源、taxonomy、權重、衣櫥回饋與下月 watchlist
```

---

## 2. 每日：Daily Brief → 挑買候選

**目的**：把當天訊號壓縮成我能立即參考的情報與「該不該買」的方向。

**輸入**：

- `data/sources.yml` 的來源巡檢結果。
- 新聞 / 品牌公告 / 發售 / 社群觀察等 raw signals。
- `scripts/score_trends.py` 的候選趨勢分數（可選）。
- 既有 taxonomy、brands、people 資料。

**輸出**：

- `reports/daily/YYYY-MM-DD.md`（含 `🛒 對我有用 For Me`）。
- 1–3 個可進入本週挑買 shortlist 的候選方向。
- 1–2 個 watchlist 伏筆。

**編輯規則**：

- 寧可少而準，不為湊數把弱訊號寫成 headline。
- 每個 headline 都要能回答：「是什麼 / 為什麼現在 / 對我（穿 / 買）有什麼用」。
- 不確定處標 `待查` 或 `（待驗證）`；不新增沒來源的排名、百分比、銷量。
- 語氣遵守 `docs/content_strategy.md`：自信但不裝、實用優先、快準有態度、誠實。

---

## 3. 每週：挑買 shortlist → 入手決策

**目的**：把 daily brief 的情報收斂成「真正想入手」的少數方向，避免衝動亂買。

**建議節奏**：每週收斂 1–3 個方向，依預算與衣櫥缺口調整。

**固定產物**：「本週最值得買 Head-to-Toe」→ `reports/buy_shortlist/YYYY-Wnn.md`（4 區 × 各 3 樣 + 為什麼是本週）。
跑 `python scripts/generate_weekly_buy_picks.py` 產骨架，依 `prompts/weekly_buy_picks.md` 填內容。

**週度整理清單**：

1. 回看過去 7 天 daily briefs，列出重複出現或分數高的趨勢。
2. 為每個候選趨勢給一段挑買判斷（值不值得買、在哪買、別買的情況），直接寫進週挑清單（D9：不開獨立挑買卡）。
3. 依 buy_angle 分類：staple 基本款 / upgrade 升級替換 / statement 亮點 / seasonal 當季 / experiment 嘗試。
4. 優先選 entry / mid 預算、好駕馭、能融入現有衣櫥的選項；splurge 要額外說清楚為什麼值得一次到位。
5. 對每項推薦做冷靜審核：有可驗證來源、價格合理、不是衣櫥已有的重複、不是被假稀缺推著買。

**輸出**：

- 本週 1–3 個想入手的方向（挑買 shortlist）。
- 每個方向的 buy_angle、預算帶、優先度、搭配方向。
- 下週要追的 watchlist。

---

## 4. 每月：Monthly Heat Report → 市場回看

**目的**：把單日雜訊收斂成月度男裝熱度地圖（歐美 + 日本兩條線，各自一份），供下月挑買與主題分析使用。

**輸入**：

- 當月 daily briefs。
- 該地區量化基準：歐美 `data/rankings/lyst-index.yml`、`stockx.yml`；日本 `mercari-jp.yml`（量化弱，主榜更依賴事件與媒體共識，信心保守）。
- 官方發售、聯名、秀程、pop-up、可讀全文媒體報導。
- 電商與社群觀察（若無公開 API 或可回查證據，只能當弱訊號）。

**輸出**：

- `reports/monthly/YYYY-MM-eu.md`、`reports/monthly/YYYY-MM-jp.md`（日本線 2026-07 起）
- 本月品牌 / 單品熱度排序（綜合判斷，非官方榜）。
- 訊號來源分層、信心標示、抓取限制。
- 與 Lyst / StockX 基準的差異。
- 2–3 條下月挑買方向或追蹤方向。

**硬規則**：

- 先寫訊號來源分層，再寫 Top list。
- 明確區分 `L2 已確認事件`（聯名、發售、秀程）與 `L4 弱訊號`（電商 best-seller 推測、403 snippet、社群體感）。
- L4 不可支撐「熱賣」「爆紅」「銷量成長」等硬結論；只能寫「待查」「零售端可見」「媒體提及」。
- 若當月訊號弱，報告要誠實降級，不硬湊 Top 10。

---

## 5. 每週至少一張：Topic Analysis → 長線資產

**目的**：把連續出現、值得壓注的題目沉澱為可長期引用的分析，不讓情報只停在日報。

**節奏（2026-06-11 Kai 拍板「歐美趨勢＋值得買做到極致」）**：**每週至少產出一張趨勢深挖卡，歐美趨勢優先**——
從本週訊號挑「最強的跨源趨勢」，依 `templates/trend_card_template.md` 跨源查證 → 生命週期 → 全價位帶落地 →
直連挑買判斷（範本見 `reports/analysis/2026-washed-denim.md`）。一年累積 ≈50 張卡＝自己的歐美趨勢資料庫。
訊號真的弱的週可以停一次，但要在週挑 shortlist 註明「本週無值得深挖的跨源趨勢」，不硬寫。

**選題條件**（符合任一即可）：

- 同一趨勢連續 2–4 週出現在 daily / monthly 產物。
- 同時有 L1/L2 強訊號與衣櫥回饋支持。
- 對我有明確實穿價值或挑買決策價值。
- 需要釐清市場誤解，例如「媒體在講，但我真的穿得上嗎、值得買嗎？」

**輸出位置**：`reports/analysis/`

**分析重點**：

- 趨勢定義與來源。
- 男裝視角的實穿 / 消費 / 文化解讀。
- 反方觀點與風險。
- 可以延伸成哪些挑買方向或衣櫥調整。
- 後續要回看的指標。

---

## 6. 回饋迴路

每次完成週挑買、月報或主題分析，都要回頭檢查：

- `data/sources.yml`：是否有新來源值得加入？舊來源是否失效？
- `data/trend_taxonomy.yml`：是否有分類裝不下的新現象？
- `docs/trend_scoring_rules.md`：評分權重是否符合實際命中率（買了之後真的穿）？
- `prompts/`：是否出現固定弱點，需要回頭硬化提示詞？
- `reports/`：是否留下可回看的證據鏈，而不是只留結論？

---

## 7. 角色分工

| 階段 | 主導 | 工具 / AI | 我（人）|
|------|------|-----------|---------|
| Daily brief 判斷 | AI 整理 | `prompts/daily_trend_brief.md` | 最終採用 |
| 每週挑買 | AI 產週挑清單 | `prompts/weekly_buy_picks.md` | 決定買 / 等 / 跳過 |
| Monthly report | AI 分層判斷 | `prompts/monthly_heat_report.md` | 確認信心、決定入手 |
| Topic analysis | AI 整合 | 工程 / 格式輔助 | 拍板 |

工程腳本負責確定性工作（填模板、算分、排序、檔案管理）；AI 負責語意整理與挑買建議；我負責品味與買不買。
