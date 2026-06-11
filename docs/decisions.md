# Decisions — Style Superman 下一階段主編決策

> 本文件記錄 Style Superman 的主編決策。D1–D5 源自 `docs/codex_execution_plan.md`（已封存）§3 的第一輪「人類決策 Queue」；後續決策直接在本檔新增，不另開分檔。凡涉及品牌定位、對外發布節奏、費用或供應商選型者，仍需人類最終拍板；「不可回頭」的拍板要同步在 `data/decision_guards.yml` 建守衛。

## 決策總覽

| # | 決策題 | Codex 建議 | 待人類確認? |
|---|--------|------------|--------------|
| D1 | 韓潮是否獨立 monthly report | 已拍板：補 KR 來源、daily brief 固定追 KR、月報加韓潮 cross-market；獨立 KR 月報暫緩 | 否 |
| D2 | 月報排序固定 Top 5/10 或依訊號浮動 | 已拍板：月報主榜固定 Top 5，另設浮動觀察名單 3–5 條 | 否 |
| D3 | 是否新增挑買 shortlist 目錄 | 已拍板：方向採 `reports/buy_shortlist/YYYY-MM.md`；本輪不建實體目錄 | 否 |
| D4 | 來源 tier 調整原則 | 已拍板：採 tier 判斷原則；本輪不批量改 `data/`，另案 PR 再改 | 否 |
| D5 | LLM 供應商策略 | **已拍板：不接 API、C7 不做**（理由：排程雲端 agent 已自動產出 AI 報告，C7 屬重複造既有能力） | 否 |
| D6 | 2026-06-10 全域審計的四項工程提案 | **已拍板：四項全部否決、不可回頭**（`_common.py` 共用模組 / `field_contracts.yml` / repo_health 設定驅動重構 / 月報回補）——「看起來專業但增加熵」 | 否 |

---

## D1 — 韓潮要不要獨立 monthly report

### 選項

1. **立刻新增獨立韓潮 monthly report**
   例如 `reports/monthly/YYYY-MM-kr.md`，每月固定產出韓潮熱度速報。
2. **先留在 daily brief，月報只做 cross-market section**
   每日追蹤 KR 訊號；歐美 / 日潮月報中保留「韓潮外溢訊號」或「跨市場交集」小節。
3. **只在主題分析時處理韓潮**
   不進每日 / 每月固定節奏，等明確爆點再寫 `reports/analysis/`。

### 建議

採 **選項 2：先留在 daily brief，月報只做 cross-market section**。

### 理由

- 目前 `data/sources.yml` 的韓潮來源數量較少，且多數缺 RSS；立刻固定月報容易把單一來源訊號寫得過重。
- 韓潮對男裝很重要，但常透過 K-pop、名人造型、MUSINSA 零售與短影音擴散，較適合先在 daily brief 裡累積訊號，再觀察是否穩定形成月度主題。
- 先做 cross-market section 可保留韓潮敏感度，又不會讓月報變成「來源不足但硬湊榜」。
- 若連續 2–3 個月都有 5 條以上高可信 KR raw signals，且能轉成 2 條以上 headline / 挑買方向，再升級為獨立 KR monthly report。

### 拍板狀態

**已拍板。** 採「補 KR 來源 + daily brief 固定追 KR + 月報加韓潮 cross-market 小節」；**獨立 KR 月報暫緩**。維持升級門檻：連續 2–3 個月都有 5 條以上高可信 KR raw signals，且能轉成 2 條以上 headline / 挑買方向，再升級為獨立 KR monthly report。

---

## D2 — 月報排序固定 Top 5/10 還是依訊號浮動

### 選項

1. **固定 Top 5**
   每月只列 5 個最重要趨勢。
2. **固定 Top 10**
   每月固定列 10 個趨勢 / 單品 / 品牌。
3. **完全依訊號浮動**
   有幾個可信趨勢就列幾個，不強制數量。
4. **混合制：固定 Top 5 + 浮動觀察名單**
   主榜固定 Top 5，另列 3–5 個「watchlist / confirming signals」。

### 建議

採 **選項 4：固定 Top 5 + 浮動觀察名單**。

### 理由

- 固定 Top 5 能讓讀者快速理解「本月最該看什麼」，也方便未來做跨月回測。
- 固定 Top 10 在訊號不足月份容易灌水，違反 repo「不虛構 / 不硬湊」慣例。
- 完全浮動雖然誠實，但不利於月報模板、挑買節奏與長期比較。
- 「Top 5 + 觀察名單」可同時保留穩定輸出與訊號誠實度：主榜只收高信心題，觀察名單可放早期但未完全驗證的 trend。

### 拍板狀態

**已拍板。** 採混合制：月報主榜固定 Top 5，另列 3–5 條浮動「觀察名單 / confirming signals」。主榜只收最值得優先看的高信心題；觀察名單保留早期、跨市場或待確認訊號。

---

## D3 — 要不要新增挑買 shortlist 目錄

### 選項

1. **新增 `reports/buy_shortlist/`**
   把由 daily brief / monthly report 轉出的挑買卡 / 想入手方向放在 reports 底下。
2. **新增根目錄 `shortlist/`**
   把挑買 shortlist 當成與 `reports/` 平行的一級產品。
3. **暫不新增目錄**
   先把挑買方向放在 daily brief 或人工外部工具（Notion / Sheet）裡。

### 建議

採 **選項 1：新增 `reports/buy_shortlist/`**，但先只定為輕量 Markdown 挑買池；本輪不新增實體目錄，待下一個流程 PR 再建立。

### 理由

- `reports/` 已承擔「情報產物」角色，挑買卡是 daily / monthly 的下游，放在 `reports/` 底下比較符合現有資訊架構。
- 根目錄 `shortlist/` 會讓 repo 一級目錄變多，也容易和未來 Notion / Sheets 工具重疊。
- 先用 Markdown 挑買池可保持低成本；等到需要狀態欄位、入手日期、預算追蹤時，再決定是否引入 YAML frontmatter 或外部工具。
- 建議命名：`reports/buy_shortlist/YYYY-MM.md`，每月一檔，避免每日碎檔過多。

### 拍板狀態

**已拍板。** 方向採 `reports/buy_shortlist/YYYY-MM.md`（2026-06-05 個人挑買重定位後）；**本輪不新增實體目錄**，待下一個流程 PR 再建立或調整。
**已拍板（2026-06-10，擁有者）：採 (b) 移除。** 本 repo 沒有要拍片，純個人興趣：深挖趨勢、找出問題、收斂成挑買判斷。`reports/content_ideas/` 整組刪除（含排程 agent 依舊任務卡落地的 2026-06.md）。
**→ 重定位殘留總清（2026-06-11，擁有者拍板「深挖把拍攝相關都刪掉」）**：深掃全 repo + 雲端排程後清除最後一批內容生產殘留——`trend_taxonomy.yml` 的 `content_angle` 標籤組整組移除（挑買卡 `buy_angle` 已取代其功能）、`ai_collaboration.md` 殘留的發布者框架（品牌主編/hot-take 審稿）改寫為擁有者/品味終審、`reports/analysis/2026-us-jp-overlap.md`（重定位前產物、整份內容創作框架且無歷史豁免註記）依本案 (b) 前例刪除；守衛 pattern 補 `content_angle`。repo 外：月度速報 routine 任務卡（仍含「可拍選題」+ 直推 master）已更新為挑買方向 + 分支/PR 流程，與重定位無關的「IG 漲粉週報」routine 經擁有者確認為錯置，已停用。
**→ 挑買池落地（2026-06-10，擁有者直接需求）**：形態從原案「每月一檔」演進為**週檔** `reports/buy_shortlist/YYYY-Wnn.md`——「本週最值得買 Head-to-Toe」：4 區（頭/上身/下身/足）× 各 3 樣 + 為什麼是本週。工具鏈：`templates/weekly_buy_picks_template.md` / `prompts/weekly_buy_picks.md` / `scripts/generate_weekly_buy_picks.py`；validate 檢查命名、repo_health 盯斷更（落後 2 週 WARN）。首期 2026-W24。

---

## D4 — 來源 tier 調整原則

### 選項

1. **維持現有 tier，不新增細則**
   只沿用 `data/sources.yml` 的 `tier: 1/2/3`。
2. **建立 tier 判斷原則，但暫不批量改資料**
   先明確哪些能當 primary signal，哪些只能 confirmation。
3. **立刻重排所有來源 tier**
   直接修改 `data/sources.yml`，把社群、媒體、ranking 全部重分級。

### 建議

採 **選項 2：建立 tier 判斷原則，但暫不批量改資料**。

### 理由

- 本輪只因 D1 補必要 KR 來源；不批量重排既有 `data/` 來源 tier，因此不應在同一 PR 做全來源重分級。
- C6 RSS 收集會開始自動讀 `source_tier`，若沒有文字原則，工程很容易把「可抓到 RSS」誤解成「可信度最高」。
- tier 應同時看可驗證性、男裝相關性、訊號密度、是否一手資料，而不是只看知名度。

### 建議原則

#### 可作 Tier 1 / primary signal 的來源

- **可量化 ranking / platform data**：例如 Lyst、StockX 這類有明確榜單或平台數據的方法來源；但使用時仍需註明口徑限制。
- **高可信專業媒體且男裝 / 潮流訊號密度高**：例如 Hypebeast、Highsnobiety、Fashionsnap 等，可作新品、聯名、文化事件的 primary signal。
- **市場代表性零售 / 平台**：例如 MUSINSA 對韓國男裝有平台代表性；但若是 retailer 自家編輯推薦，仍要標明商業偏差。

#### 建議作 Tier 2 的來源

- **專業媒體但偏產業 / 文化解讀**：可補背景與脈絡，但不單獨證明熱度。
- **零售商 curated content / 發售頁**：可證明「被推」或「上架」，不能單獨證明「賣爆」。
- **區域性或垂直來源**：對特定市場有效，但需跨來源確認才升級為 headline。

#### 只能作 confirming signal / Tier 3 的來源

- **社群 hashtag、Reddit、TikTok 單一貼文**：可提示早期擴散，但容易受演算法與小樣本影響。
- **品牌新聞稿 / 公關稿**：可證明品牌動作，不可單獨證明趨勢熱度。
- **無方法說明的榜單 / affiliate listicle**：可參考內容角度，不應當作主要排名依據。

### 拍板狀態

**已拍板。** 採本節 tier 判斷原則；**本輪不批量修改 `data/` 既有來源 tier**。需要重分級時另開資料 PR，逐筆說明原因與口徑。

---

## D5 — LLM 供應商策略

### 選項

1. **先只保留手動 prompt 流程**
   C6 只產 raw signals，人類 / Codex 手動把 prompt 餵給 LLM。
2. **同時支援 Claude / OpenAI 真實 API**
   C7 直接實作多供應商 API。
3. **先做 vendor-neutral adapter，內建 manual/mock provider**
   工程先定 input/output 契約與測試替身；真實 provider 另案實作。

### 建議

採 **選項 3：先做 vendor-neutral adapter，內建 manual/mock provider**。

### 理由

- 這能讓 C7 先解決最重要的工程問題：raw signals、prompt、template、輸出 brief 之間的穩定介面。
- `manual` provider 保留現有人類 / Codex 主編流程，不因 API key 或費用卡住。
- `mock` provider 讓 tests / CI 可驗證「自動撰寫 brief」管線，不依賴外部 LLM，也不會因模型輸出漂移造成測試不穩。
- Claude / OpenAI 都可能適合，但真實 API 牽涉 key 管理、成本、資料外送與模型選型，不應由 Claude Code 在工程 PR 中自行決定。

### 已拍板（2026-06-04）

**不接 API、C7 不做。** 經檢討：

- 系統**已經**透過排程雲端 agent（每月歐美速報、Lyst Q2 watcher）自動產出 AI 撰寫的報告，且 agent 會上網查證、對照季榜、標信心——比腳本單次呼叫 API 更強。C7「腳本直接呼叫 LLM 寫 brief」有一半是**重複造已有能力**。
- 加真實 API 的唯一增益是「全自動無人值守」，但排程 agent 已接近此效果；代價卻是金鑰管理、每月帳單、額外失敗點與編造風險。違反「不為寫 code 而寫 code、先輕後重」。
- 需要 AI 寫 brief 時，把 `raw_signal_pack` 直接交給對話中的 Claude 或排程 agent 即可，無需 repo 內 API key。

> 註：此項原為 day-1 README roadmap 的願景被升級成「決策」，非實際需求（見檢討）。若日後真有無人值守的硬需求再重啟。

## D6 — 全域審計四項工程提案的處置

### 背景

2026-06-10 第一性原理全域審計（3 個獨立 agent 分區深讀 + 反向驗證）產出多項工程提案，
其中四項經評估屬「看起來專業但會增加熵」：

1. **scripts 層共用模組（`_common.py`）**（抽 yaml 載入 / die / ensure_utf8 樣板）——
   腳本獨立可跑 > 樣板去重；加共用模組 = 加耦合 + 加 import 失敗點。
2. **平行契約定義檔（`field_contracts`）**（prompt↔template 欄位對應表）——
   template 本身就是契約；第二套定義 = 兩套世界觀漂移風險，正是本 repo 踩過的坑。
3. **repo_health 設定驅動重構**（把檢查項外部化成 `health_checks` / `output_contracts` 設定檔）——
   現有 9 個檢查運作良好、執行快；YAGNI，檢查項破 15 個前不重啟。
4. **月報缺段落回補**（2026-06-eu.md 補現行 template 段落）——
   違反「reports 產出後不回改」鐵則；該檔已加歷史快照 banner。

### 已拍板（2026-06-11，Kai）

**四項全部否決，不可回頭。** 已建守衛 `audit-rejected-over-engineering`
（`data/decision_guards.yml`）擋識別字復活；第 4 項由快照鐵則 + 檔內 banner 防護。
若未來條件變化（如檢查項規模化、腳本數翻倍），依「決策過時時」慣例：先改本檔、再動守衛，不默默繞過。
