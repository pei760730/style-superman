# Decisions — Style Superman 下一階段主編決策

> 本文件回應 `docs/codex_execution_plan.md` §3 的「人類決策 Queue」。Codex 在這裡給出建議方案與理由；凡涉及品牌定位、對外發布節奏、費用或供應商選型者，仍需人類最終拍板。

## 決策總覽

| # | 決策題 | Codex 建議 | 待人類確認? |
|---|--------|------------|--------------|
| D1 | 韓潮是否獨立 monthly report | 先留在 daily brief 與月報 cross-market section，不立刻獨立月報 | 是 |
| D2 | 月報排序固定 Top 5/10 或依訊號浮動 | 固定主榜 Top 5，另設「觀察名單」浮動 3–5 條 | 是 |
| D3 | 是否新增 content idea 目錄 | 先新增 `reports/content_ideas/`，不新增根目錄 `content_pool/` | 是 |
| D4 | 來源 tier 調整原則 | Tier 1 僅給可驗證且高訊號密度來源；社群與公關稿多數作 confirming signal | 是 |
| D5 | LLM 供應商策略 | 先做 vendor-neutral adapter + manual/mock provider；真實 Claude/OpenAI API 另案拍板 | 是 |

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
- 韓潮對男裝內容很重要，但常透過 K-pop、名人造型、MUSINSA 零售與短影音擴散，較適合先在 daily brief 裡累積訊號，再觀察是否穩定形成月度主題。
- 先做 cross-market section 可保留韓潮敏感度，又不會讓月報變成「來源不足但硬湊榜」。
- 若連續 2–3 個月都有 5 條以上高可信 KR raw signals，且能轉成 2 條以上 headline / short video ideas，再升級為獨立 KR monthly report。

### 待人類確認?

**是。** 這會影響 Style Superman 是否把韓潮定位成獨立內容支柱；需人類確認品牌是否要主動強化 KR 覆蓋。

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
- 完全浮動雖然誠實，但不利於月報模板、短影音選題節奏與長期比較。
- 「Top 5 + 觀察名單」可同時保留穩定輸出與訊號誠實度：主榜只收高信心題，觀察名單可放早期但未完全驗證的 trend。

### 待人類確認?

**是。** 排序數量會影響月報閱讀體驗、內容產量與後續短影音節奏；需人類確認是否偏好精簡或大量盤點。

---

## D3 — 要不要新增 content idea 目錄

### 選項

1. **新增 `reports/content_ideas/`**
   把由 daily brief / monthly report 轉出的短影音、圖文、hot-take 選題放在 reports 底下。
2. **新增根目錄 `content_pool/`**
   把選題池當成與 `reports/` 平行的一級產品。
3. **暫不新增目錄**
   先把選題放在 daily brief 或人工外部工具（Notion / Sheet）裡。

### 建議

採 **選項 1：新增 `reports/content_ideas/`**，但先只定為輕量 Markdown 選題池；本輪不新增實體目錄，待下一個內容流程 PR 再建立。

### 理由

- `reports/` 已承擔「情報產物」角色，content ideas 是 daily / monthly 的下游，放在 `reports/` 底下比較符合現有資訊架構。
- 根目錄 `content_pool/` 會讓 repo 一級目錄變多，也容易和未來 Notion / Sheets 排程工具重疊。
- 先用 Markdown 選題池可保持低成本；等到需要狀態欄位、發布日期、平台分發時，再決定是否引入 YAML frontmatter 或外部工具。
- 建議命名：`reports/content_ideas/YYYY-MM.md`，每月一檔，避免每日碎檔過多。

### 待人類確認?

**是。** 選題池是否留在 repo，取決於人類的實際拍攝 / 排程工具；若已主要使用 Notion，repo 只需保留精華或回測資料。

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

- 本輪 scope 不碰 `data/`，因此不應直接改來源 tier。
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

### 待人類確認?

**是。** 來源 tier 會影響自動化權重與內容可信度；人類需確認哪些來源符合 Style Superman 的市場觀點，之後再另開資料 PR 修改 `data/sources.yml`。

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

### 待人類確認?

**是。** 人類需拍板是否允許真實 API provider、優先供應商、API key 管理方式與每月成本上限。未拍板前，C7 只應實作 `manual` / `mock` 與可擴充 adapter 介面。
