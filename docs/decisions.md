# Decisions — Style Superman 下一階段主編決策

> 本文件記錄 Style Superman 的主編決策。D1–D5 源自第一輪工程規劃的「人類決策 Queue」（任務卡檔已於 2026-06-11 D7 移除，見 git 歷史）；後續決策直接在本檔新增，不另開分檔。凡涉及品牌定位、對外發布節奏、費用或供應商選型者，仍需人類最終拍板；「不可回頭」的拍板要同步在 `data/decision_guards.yml` 建守衛。

## 決策總覽

| # | 決策題 | Codex 建議 | 待人類確認? |
|---|--------|------------|--------------|
| D1 | 韓潮是否獨立 monthly report | 已拍板：補 KR 來源、daily brief 固定追 KR、月報加韓潮 cross-market；獨立 KR 月報暫緩 | 否 |
| D2 | 月報排序固定 Top 5/10 或依訊號浮動 | 已拍板：月報主榜固定 Top 5，另設浮動觀察名單 3–5 條 | 否 |
| D3 | 是否新增挑買 shortlist 目錄 | 已拍板：方向採 `reports/buy_shortlist/YYYY-MM.md`；本輪不建實體目錄 | 否 |
| D4 | 來源 tier 調整原則 | 已拍板：採 tier 判斷原則；本輪不批量改 `data/`，另案 PR 再改 | 否 |
| D5 | LLM 供應商策略 | **已拍板：不接 API、C7 不做**（理由：排程雲端 agent 已自動產出 AI 報告，C7 屬重複造既有能力） | 否 |
| D6 | 2026-06-10 全域審計的四項工程提案 | **已拍板：四項全部否決、不可回頭**（`_common.py` 共用模組 / `field_contracts.yml` / repo_health 設定驅動重構 / 月報回補）——「看起來專業但增加熵」 | 否 |
| D7 | 2026-06-11 第一性原理瘦身 | **已拍板（擁有者：「砍掉沒用的」）**：刪 article_to_insight（死迴圈）、codex_execution_plan（封存歷史）、google-trends 手動月拉（人類勞動依賴）；ai_collaboration 259→30 行；立「反熵原則」 | 否 |

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

---

## D7 — 第一性原理瘦身（2026-06-11）

### 背景

repo 上線 7 天的 git 證據：110 個 commit 中 76% 是系統自我維護、僅 14% 是情報產出（每產 1 份報告付 5.6 次維護成本）。
擁有者拍板「用第一性原理砍掉沒用的——什麼是我下個月就不用了」。本質需求只有一句：
**一個人，每天早上 5 分鐘，做出更好的買不買決策，並讓品味長期複利。**

### 判準（三問）

1. 它直接餵進一個買不買的決策嗎？
2. 它需要人類定期手動勞動嗎？（需要 = 下個月就會死）
3. 它是資料（複利資本）還是流程（折舊負債）？

### 已拍板：砍

- **article_to_insight prompt（prompts 層）**：「signal_type/credibility 待查 → 交給它補」的迴圈上線一週從未運轉過——
  主編 agent 直接判讀 raw pack 效果相同。典型的「文件互相引用、自我維持、無人發現沒在跑」死迴圈。
- **codex_execution_plan（docs 層，315 行）**：已封存的第一輪任務卡，git 歷史就是檔案館，不需要活目錄裡的副本。
- **google-trends 排行檔（data/rankings 層）+ 每月手動拉取流程**：每月 20 分鐘人類手動勞動、建立後一期都沒拉過。
  推翻 2026-06-11 上午的拍板——錯了就要快認。方法論存 git 歷史，有自動化途徑可復活。
- **`docs/ai_collaboration.md` 259 → ~30 行**：交接流程、任務卡模板、RACI 全表、範例 A/B/C 全砍——
  為「兩個 AI 產品的組織」設計的儀式，對單人＋agent 系統無約束力。留三條真正載重的：
  帽子原則、自我審查偏誤控制（不自我終審）、誰拍板。

### 已拍板：不砍（含對審計 agent 結論的修正）

- `prompts/trend_analysis.md` + `score_trends.py`：週趨勢深挖卡（washed-denim 主打卡）就是這條線產的，ALIVE。**（→ 2026-06-14 D14 部分推翻：`score_trends.py` 加權評分框架已全砍——實測它只在 smoke 空跑、趨勢挑選實際全靠主編判斷；`trend_analysis` 趨勢卡保留，但移除 0–5 評分段。）**
- `prompts/ranking_ingest.md` + `templates/ranking_snapshot_template.md`：Lyst Q2 watcher 雲端 routine 在 repo 外消費它們。
- **全部資料快照**（mercari 2022、kream 2025 等「舊」資料）：資料是複利資本、零維護成本；流程才是折舊負債。

### 反熵原則（隨 D7 確立，寫入 CLAUDE.md）

1. **新流程不得依賴人類定期手動勞動**——要嘛自動化、要嘛不做。
2. **新檢查只能由重複出現的教訓硬化而來**（單次事故記 lessons 即可）——防止免疫系統自我增生。
3. **長期主義的判準是維護/產出比**：第一週 76% 維護是建設期常態，下個月此比例必須倒轉（產出 > 維護）；
   每次月度回看時順手檢查。

---

## D8 — 終審 ≠ merge：例行產出驗證綠即自 merge（2026-06-12）

### 背景

挑買卡 PR #49 依舊規「內容判斷留人類終審」掛起等擁有者 merge。擁有者質疑：「每天可以推薦，
不要叫我 merge。進 main 要幹嘛？設計的第一性原理是？」——暴露 D7 反熵原則沒砍乾淨的最後一個死迴圈：
把「人類點 merge」當成終審，等於把擁有者變成產線的 blocking step（人類定期手動勞動），
他不點，卡就進不了系統記憶，隔天 brief 的交叉引用、價格基準全部斷裂。

### 第一性原理

- **main = 系統的長期記憶**（後續 brief 引用舊卡、價格基準對照、命中率回看），不是批准章。
- **系統的價值事件 = 擁有者讀到判斷 + 在現實中買 / 不買**——那是錢包投票，從來不是 git 事件。
- 「終審永遠是人類」的本意是**內容判斷的對錯由人類拍板**，不是「人類要點 merge 按鈕」。

### 拍板

- 例行產出（daily brief、挑買卡、週挑、月報）：保留**分支 + PR**（品質閘：CI 驗證 + diff 軌跡），
  **驗證綠即由 agent 自 merge，不留人**。
- 人類終審改為**事後反饋**：讀完覺得判斷錯 → 反饋記入 `decisions.md` / `lessons.md`，產線修正。
- **不變**：CLAUDE.md「不應該單獨做」清單照舊——新增來源、改 template 契約、花錢、對外發布、
  開新排程仍留人類拍板；本決策只解放「例行產出的 merge」這一步。
- 同步修改：`docs/ai_collaboration.md` §2/§3、`README.md`（守則行 + 自動化全貌表）、
  排程 agent 任務卡若有「留終審不自 merge」描述一併更新。

---

## D9 — 挑買卡停產：推薦回歸 brief 內（2026-06-12）

### 背景

D8 落地當天，擁有者再砍一層：「把挑買卡拿掉，就單純推薦就好。如果週報裡面有不錯的，
我自己會去查、自己會去買。」——挑買卡的深度欄位（怎麼搭 / 衣櫥缺口 / 哪裡買的完整選項）
是替擁有者做他本來就想自己做的功課，屬於過度服務；推薦的價值密度在 For Me 的一行
（單品｜價格｜通路｜時點｜一句為什麼）就已飽和。

### 拍板

- **停產**：prompts 層 buy_picks、templates 層 buy_pick_template 刪除（D7 前例：git 歷史即檔案館）；
  daily brief 的「值得入手」不再同日開卡，推薦只寫在 brief 內（五件事行動帳格式，
  第五件改為「一句為什麼 / 別買的條件」）。後續變化（價格、售罄）寫進新一天的 brief。
- **保留**：週挑 Head-to-Toe（`reports/buy_shortlist/`，每週收斂清單）與月報「本月挑買方向」
  ——這些是擁有者說的「週報裡面的推薦」，格式本來就是清單不是卡。`buy_angle` 標籤照用。
- **封存**：已產出的 3 張卡（reports/buy_picks/ 2026-06-11~12）依「reports 是封存快照」鐵則
  原地凍結不刪——舊 brief 連結著它們；資料是複利資本，流程才是折舊負債（D7）。
  - **（2026-06-14 反轉）** 擁有者拍板：獨立挑買卡是「之前的設計錯誤」，3 張卡全數刪除、
    `reports/buy_picks/` 目錄收掉；06-11 brief 連到卡的兩個 `→ 挑買卡` 尾連結一併清掉
    （For Me 內容不動，只拿掉壞掉的指標）。推薦此後只活在 brief For Me / 週挑內，不留卡形態任何痕跡。
- 守衛：`d9-no-buy-pick-cards` 擋住開卡流程被寫回活文件。

---

## D10 — 可購性門檻：推薦位只推買得到的（2026-06-12）

### 背景

擁有者否決「買後回填」「watchlist 價格盯梢」兩個延伸提案（「這個我確定用不到，誰整天在買東西，
頻率太低」），並指出推薦位的真 bug：「你推薦的都是最紅的，根本短時間買不到」——「值得入手」連日
全是限定聯名（nonnative×Timberland 完售前科、CDG 復刻不補貨、SI×NB 必搶、Teva×N.HOOLYWOOD
數量限定），對低頻買家可執行率趨近零。根因：上游訊號源（Hypebeast 系）天然偏發售新聞，
「新發售」被系統誤當「值得買」。**「紅」是訊號，「買得到」才是推薦資格。**

### 拍板（擁有者原文，2026-06-12）

- **可購性門檻**：「值得入手」（daily For Me）與週挑 15 樣只推**現在下單買得到、且下個月還買得到**
  的東西（定番、原版、GR 常販、穩定補貨款）。
- 抽選／數量限定／完售前科的限定聯名一律**降到訊號層**（頭條／地區區塊照報，當趨勢讀），
  **不得進推薦位**。
- 推薦理由**禁用「要搶」「錯過沒了」等限時話術**。
- **同場確定不做**：買後回填、價格盯梢（頻率太低用不到；出生前夭折，最便宜的刪除）。
- 觀察項：「⏰ 行動日」子項內容多為限定發售死線，與本門檻精神有張力——先保留，
  跑數日看擁有者實際使用再議（規則上線後看真實使用，不疊規則）。

---

## D11 — 品牌雷達：關鍵字觸發的 10 大品牌深挖（2026-06-12）

### 背景

擁有者需求：「我會給你關鍵字，你就給我當下最值得關注的 10 大最紅男性潮流品牌（全品項），
從頭到腳＋配件。」四個設計點先討論後拍板（「照建議落地」）。與 D10 同日——推「品牌」而非
限定單品，天然繞開「最紅＝買不到」的死結：品牌的定番永遠在貨架上。

### 拍板

- **對話觸發**（「深挖 <關鍵字>」），不排程、不定期（D7：不新增自動排程；用過即查，不是日課）。
- **分 tier 不給假精度**：🔥 領跑 ~3／📈 升溫 ~4／👀 早期 ~3，tier 內不排序；
  訊號不足就少於 10 並明說，不硬湊（沿用不虛構鐵則）。
- **三層證據**（媒體聲量／市場數據／話語層），每品牌至少兩層有料才入榜，出處附連結。
- **五欄**：為什麼現在紅／紅在哪／lane 相容度（對 `data/brands.yml`，紅但不是菜要直說）／
  不踩雷入手點（定番款，D10 相容）／風險。
- **覆蓋**：10 牌合計從頭到腳＋配件，配件不得缺席；不設硬配額。
- **存檔**：`reports/analysis/YYYY-MM-DD-brand-radar-<slug>.md`（封存快照，留回測鉤——
  3 個月後驗證 tier 預測，這是雷達與訂閱媒體的差異）。
- 工具：`prompts/brand_radar.md`；結構定義在 prompt 內，**不新增 template**（輕依賴；
  反覆使用且結構穩定後再升級成 template 契約）。

**→ 格式修正（2026-06-12 同日，擁有者反饋「一句話沒辦法好好描述亮點」）**：五欄拆成六欄——
「為什麼現在紅（一句）」改為「**是什麼**（一句，品牌本質）＋**為什麼現在紅**（1–3 句，亮點講滿）」，
兩欄合計 80–150 字（沿用 daily headline 的驗證額度）；📌 雷達三行維持一句話目錄職責。
首發日潮雷達同日以 v2 重發（比照 06-12 brief v2 前例：當日產物可同日格式重發，非回改歷史快照）。

---

## D12 — 看到問題就修：工程修正不需事前請示（2026-06-13）

### 背景

Sleep-mode 巡檢發現 health.yml 看門狗假成功（`--strict | tee` 在 Actions 預設 shell
無 pipefail，失敗被吃掉——巡檢體系的最後出口整條是斷的）等工程問題。agent 修完、
PR #73/#74 CI 綠後，merge 卡在授權模糊：「你修你負責的」被權限層判定不足以自 merge。
擁有者連兩句拍板：「你修你負責的」「看到問題就修」。

### 拍板

- **工程問題（bug、假成功、文件↔實作漂移、驗證缺口）看到就修，不需事前請示**——
  走 branch → 單主題 PR → CI 綠 → 自 merge。D8 的自 merge 從「例行產出」延伸到「工程修正」。
- **修的人負責到底**：驗證做到實機（不只本機綠），修壞了自己回滾、自己記 lessons。
- **不變**：CLAUDE.md「不應該單獨做」清單照舊——內容判斷、品牌觀點、新增來源、
  改 template 契約、花錢、對外發布、開新排程仍留人類拍板。本決策只解放工程修正的
  「請示 → 等人」這一步。
- 同步：CLAUDE.md Self-Evolution Loop 的 Propose 行。

---

## D13 — 歐美不拆每日兩區；歐洲深度走每週深挖位 + 收 Drapers（2026-06-13）

### 背景

擁有者問「歐洲跟美國資訊量夠不夠分開兩區」。先評估後實測：
- 近兩日 us-eu+global 訊號 美:歐 ≈ 40:6，歐洲專屬可用 RSS 來源實際只有 2 個（fucking-young、permanent-style）。
- 兩輪共測 40 個歐洲來源候選 URL（用 repo 自己的 parser 驗）：最對味的純男裝源（The Rake / nss / 032c / Pause / Mr Porter / SHOWstudio）無可用 RSS 或 parser 讀不到；能抓的多是音樂誌或 GQ 各國版（gq-korea 等級的生活風格稀釋），Hypebeast 法/德版是翻譯重複。
- 對 Numéro EN / Dazed 做 2 週 sitemap 產量量測：**Numéro EN 男裝 ≈0.21 條/天（且含泳裝誤判，真男裝近 0）、Dazed ≈0.8 條/天，多天為 0**。
- 關鍵洞察：**來源國籍 ≠ 內容地理**（permanent-style 英國卻在寫「What I wore in LA」）；歐洲男裝真訊號住在「全球源的歐洲覆蓋」+「事件驅動的男裝週」，不住在能抓的國別 feed 裡。

### 拍板

- **不開每日 EU 區、不拆歐美兩區**：肥料不足以撐每日一區，硬開會生出比 KR 更弱的慢性空區（撞 D7 反熵與「產出持續發生」）。
- **歐洲深度由 flow_calendar §5 每週深挖位承載**：優先輪替男裝週（SS27 Milan/Paris）、Pitti、歐洲品牌題；跨現有全球源 + 人工參考源（Dazed `/fashion`、The Rake、nss、032c）。
- **收 Drapers 進 `data/sources.yml`**（us-eu / media / tier2，RSS 實測可解析）：定位「零售/通路 intel」非 trend，餵 brief「值得買｜通路」軸，不當 headline 來源。
- **Dazed 不進每日自動源**：產量 ~0.8/天 + 女裝/文化稀釋，只當每週深挖位的人工參考源；Numéro EN 否決（~0.2/天、女裝/藝術/法文為主）。
- **不做**：加 GQ UK/IT/FR/DE、Esquire IT（gq-korea 稀釋陷阱）、Hypebeast 翻譯版（重複）。
- 待時間解鎖：若哪天歐洲男裝專源（nss/032c）願開可解析 feed，或每週深挖位連續數週都被歐洲題餵滿（=需求被證實），再重啟「是否獨立 EU 區」討論——先看 metric 再加，不先建空殼。

---

## D14 — 全砍 score_trends 加權評分框架（2026-06-14）

### 背景

「沒用過的功能」盤點時，score_trends.py（5 維度加權評分 + 分級）被列為候選。reconnaissance 確認：腳本本身只在 `tests/test_smoke.py --demo` 空跑，每日/週挑產線從不餵它真資料、SCORED_TRENDS input 從未使用；趨勢挑選 100% 靠主編 LLM 判斷。唯一實際「用到評分概念」的是趨勢卡（8 張，0–5 分 → 綜合分 → 分級），但那些分是**手算**的，沒有真的呼叫腳本。擁有者看過「這是砍正在用的框架」的警告後，仍拍板全砍（趨勢卡 0–5 評分對他無實際決策價值）。

### 拍板

- **刪 score_trends.py（scripts 層）+ trend_scoring_rules.md（docs 層）**。
- **趨勢卡移除評分段**：`templates/trend_card_template.md` 拿掉 `## 評分（0–5）` 整段；`validate_repo.py` 的 trend_card 必含字串改為只剩 `{{trend_name}}`；`prompts/trend_analysis.md` 移除「給 0–5 分餵 score_trends」指示。
- **產線文件同步**：`system_design.md`（管線移除「評分」階，trend cards 改週深挖旁支）、`operating_manual.md`（移除評分步驟並 renumber）、`flow_calendar.md`、`rankings.md`（「排行＝評分輸入」改為「排行＝L1 硬數據佐證」）、`scripts/README.md`、`README.md`、`prompts/daily_trend_brief.md`（移除 SCORED_TRENDS）、`daily_brief_template.md` footer、`ci.yml` 註解、`tests/test_smoke.py`（移除評分測試）。
- **不變**：趨勢挑選回歸主編判斷（本來就是現況，只是把沒接線的評分機制正式拿掉）。排行快照（Lyst/StockX…）仍是 L1 硬數據佐證，與評分無關、保留。
- 封存報告（reports/ 內舊趨勢卡、舊 daily）含評分段者不回改（封存快照原則）。

---

## D15 — 推薦框架從「買清單」改「在紅單品情報」（2026-06-14）

### 背景

擁有者質疑每日推薦的邏輯：① 他是**低頻買家**（repo lane 自己寫的），但系統每天硬擠「值得入手」買決策 → 沒買的堆成死重；「我沒買的那一堆要幹嘛？」② news-driven＝推最新貨，而最新＝限定/抽選/海外/當天死線＝**結構性難買**，跟他「重質感、定番、預算理性」的買法本質相反。釐清後擁有者點出真正想要的：**單品層是趨勢的具體化、是最直接的情報**——他要知道「現在歐美日韓在紅什麼單品」，**不一定要買**。所以問題不在「有單品推薦」，在把它**包裝成買決策**（值得入手｜價格｜通路｜時點｜死線）。

### 拍板

- **daily `🛒 對我有用 For Me`（行動帳/買清單）→ `🎯 對我最相關 For Me`（在紅單品情報層）**：每項＝**單品｜是什麼｜在哪紅（歐美/日/韓）｜對我衣櫥的意義｜價格/型號（辨識用）**。
- **目的是「知道」不是「買」**：價格/型號只是辨識；**砍掉死線/搶/別買條件等買壓力**；**難不難買不再是門檻**——最新/限定/海外的在紅單品照列（那正是「現在在紅什麼」的情報）。`⏰ 行動日` 子項移除。三行 `③ 要買嗎` → `③ 要記住`（今日最該記住的在紅單品）。
- **D10 重新界定 scope**：「推薦位只推買得到的定番」規範的是**真要入手那條**（擁有者開口才做的定番調研），不是這個每日情報位。日常 brief 不 push 買。
- **格式即契約同步**：`daily_brief_template.md`、`prompts/daily_trend_brief.md`、`validate_repo.py`、`repo_health.py`（產出契約段落改名、舊名續收以免凍結舊 brief 變紅）、`tests/test_smoke.py`、雲端填寫 routine、README / CLAUDE / flow_calendar / operating_manual / system_design / style_strategy。
- **週挑 Head-to-Toe（5 區×3 樣）同步轉**：「本週最值得買」→「本週在紅 Head-to-Toe」；每樣 buy_angle/預算帶/優先度/別買條件 → 是什麼/在哪紅/價格型號辨識用/為什麼這週在紅/炒作 vs 真；「🎯 如果本週只買一樣」→「🎯 本週最該記住的一個」。`weekly_buy_picks_template.md` / `prompts/weekly_buy_picks.md` / `validate_repo.py` / `generate_weekly_buy_picks.py` / README / flow_calendar 同步。檔/目錄名（buy_shortlist、weekly_buy_picks）保留以省 churn（內部識別字，語意已轉），屬已知小債。
- 封存報告（舊 daily 含 🛒 For Me 段）不回改；repo_health 產出契約以 tuple 同收新舊段落名。

---

## D16 — 砍掉雲端排程 routine，每日 brief 改全對話觸發（2026-06-14）

### 背景

每日 brief 原本兩段式自動化：GitHub Actions（台北 05:00）收 RSS 訊號 + 產空骨架直推 master，雲端 routine（claude-sonnet-4-6，台北 07:30）讀 signals 填內容、開 PR 自 merge。實跑暴露兩個結構問題：① **無人盯時品質退化**——routine 在 sandbox 連不到 RSS feed（PR #78 自述「28 源全降級」退 WebSearch），且 roundup/N選類清單常只填標題、不 WebFetch 挖 picks（擁有者 2026-06-13、06-14 兩度抓到「只有標題＝空殼」）。② 對照組:同一天擁有者在**對話**裡叫 agent（opus）認真跑——本機 collect 收到 427 則訊號、4 條 roundup 逐條 WebFetch 挖出 26 個單品、NB/Nike 各收斂成 1 則、看膩的款主動下架——產出明顯更詳細,擁有者明確說「我喜歡 你這次出來的東西 詳細多了」。結論:**規則硬化 ≠ 行為發生**,排程 routine 在無人值守下不會複製對話裡的品質,且每天還燒 routine 額度。

### 拍板

- **停用雲端 routine**「Style Superman — Daily Brief Fill」（trig_01WNyzzBQrNXL6p367UedBzY）：RemoteTrigger update `enabled:false`（API 無 delete，停用即拿掉）。
- **每日 brief 改全對話觸發**：擁有者說「早安」/「今天」→ agent 當場跑(本機 `collect_raw_signals.py` 收當日訊號 → 主編判讀 → roundup 逐條 WebFetch 挖 picks → 在對話端上完整 brief)。產出在對話讀，**不入 `reports/daily/`**（要封存再另議）。
- **`daily-brief.yml` 移除 `schedule:` cron**，保留 `workflow_dispatch` 當手動備援（本機 collect 失靈時，可在 egress 正常的 runner 手動收一次）。不刪檔。
- **0 支雲端 routine**：daily 連同週挑 / 月報 / Lyst Q2 全部對話觸發,合反熵 D7（不依賴常駐排程）、省額度。
- **文件同步**：README（系統的一天時間軸、自動化全貌表、檔案樹）、CHANGELOG。
- **可逆**：要重開排程只需還原 `daily-brief.yml` 的 cron + RemoteTrigger `enabled:true`；故不寫進 decision_guards.yml（非不可回頭的識別字）。

---

## D17 — 撤除 Mercari 日本量化板（2026-06-14）

### 背景

`track_rankings` 完整跑一次時,擁有者發現 Mercari 板是 **2013→2022 十週年回顧**,到 2026 已 **4 年陳貨**。查證:Mercari 唯一一次出乾淨「品牌成交榜」就是那份十週年回顧,之後官方年報(實查 2025 年報,涵蓋 2025-01-01~11-15)全轉成趨勢「搜尋詞」(LABUBU/動漫/K-pop),**無時尚品牌榜**。它當初被收只是 ZOZO(Akamai 擋)抓不到時的「退而求其次」。擁有者指示「先找替代,沒有就砍」。

### 替代源實測(2026-06-14,全擋)

WebFetch 實測 5 個當期日本榜:**ZOZO timeout、Rakuten 403、2nd STREET 403、BUYMA 404×2**——日本商業榜普遍 Akamai/bot 防護,無 headless 瀏覽器抓不到。WEAR 給穿搭貼文非銷售榜,metric 不同。**無可自動收的當期日本時尚榜。**

### 拍板

- **撤除 Mercari 板**:刪 `mercari-jp.yml`(data/rankings 層)+ 孤兒 fixture `mercari_snapshot.yml`(tests/fixtures 層,無測試引用)。
- **`track_rankings.py`**:移除 mercari source/region/show/choice;`--region jp` 改回報「日本量化板暫缺 + 原因」,不靜默空白。
- **`ingest_ranking_snapshot.py` / `validate_repo.py`**:移除 mercari 分支。
- **`generate_monthly_heat_report.py`**:日本 baseline 改空 tuple,`baseline_label` 優雅處理空基準(回報「無可自動收的量化基準」)。
- **日本月報定位**:全依 L2 事件確認 + L3 媒體共識,信心保守,撐不起標 `待查`。日本當期熱度看 daily brief「日潮」區(質化)。
- **文件同步**:README(四榜)、docs/rankings.md、scripts/README.md、flow_calendar.md、prompts/monthly_heat_report.md、prompts/brand_radar.md、data/sources.yml。
- **可逆**:哪天有可解析的當期日本時尚榜,重建 yml + 還原 track_rankings 即可。其他 ranking yml 內「與 Mercari 結構互相印證」的分析引述保留(引的是 Chanel→Uniqlo 歷史事實,非板的存在);reports/ 凍結快照不動。

---

## D18 — 新增來源前的兩道門：持續產出 + 權威（2026-06-14）

### 背景

撤掉 Mercari 板(D17)後討論補日本/歐美來源,擁有者拍板:**加任何新來源之前,要先確認**兩件事,否則別加。根因是這套系統踩過兩次「死權重」——Mercari 年報轉趨勢詞後不再出時尚榜(D17 撤)、google-trends 手動月拉建立後一期都沒拉(D7 砍)。來源不是越多越好,加錯會變維護負債、稀釋訊號。

### 拍板:加來源前兩關都過才收(寧缺勿濫)

1. **持續產出**:來源要「會一直出新內容」——查近 30 天更新頻率(至少每週數篇)。只在大事件才更新、或已半停更的不收(會變死權重)。
2. **夠權威**:有編輯判斷 / 一手資訊 / 行業地位,不是聚合農場或 SEO 內容站。

### 配套

- 新增來源仍是**內容判斷、需擁有者拍板**(沿用 CLAUDE.md「你不應該單獨做」);tier 不批量改(D4)。
- 加之前先 **WebFetch 實測可讀**,讀不到標 `body_fetchable: false`(roundup 不挖)。
- 門檻寫進 `data/sources.yml` 表頭(source-adder 會看到)+ CLAUDE.md「你不應該單獨做」。
- 反熵(D7)一致:寧缺勿濫,不堆會過時 / 半停更的來源。

---

## D19 — 手機速報層：白名單硬資訊源純機械抽取（2026-06-16）

### 背景

daily brief 只活在桌面 opus 對話裡（D16:全對話觸發、不入 `reports/daily/`），手機看不到；擁有者反映「我手機打早安拿不到這些資訊」。釐清出硬約束:**高品質深度 brief（趨勢判讀 + 挖 picks + For Me）綁桌面 opus + 逐條 WebFetch,不可能搬雲端不退化**（D16 砍 routine 的正是「無人盯 sonnet 退化成空殼 roundup」）。

關鍵轉念（擁有者提「為什麼不能給白名單」）:**白名單硬資訊源根本不需要 LLM 判讀**——`hypebeast` 系 / `sneakernews` / `wwd` / `fashionsnap` / `senken` / 錶源的 RSS summary 內就帶 SKU / 價格 / 發售日,純 Python 字串處理即可排成「今天有什麼上了 / 漲了 / 併了」的速報。空殼的本質是「LLM 假裝判讀其實沒料」,而機械抽取**根本不讓 LLM 判讀**,問題從根上不存在。

### 拍板:分兩層，速報走機械抽取、深度走對話

| | ⚡ 速報層（`generate_flash.py`，手機觸發） | 📰 深度版（對話 opus，桌面） |
|---|---|---|
| 任務 | 機械抽取硬資訊 | 判讀趨勢 + 挖 picks + For Me |
| 源 | 白名單發售 / 新品 / 併購 / 漲價硬源 | 全 484 則 |
| LLM | **零**（守 D5） | opus + 逐條 WebFetch |
| 輸出 | `reports/flash/<date>.md` | 對話端（不入庫，D16） |

### 配套

- 觸發走 `flash-brief.yml` 的 `workflow_dispatch`,**手機 GitHub App 手動按 = 有人盯那一次**——不違反 D16（砍的是無人值守 `schedule`,不是 `dispatch`）。刻意不加 `schedule`。
- 機械抽取會漏判「是不是衣服 / 是不是 roundup / 是否跨區重複」（靠關鍵字黑名單,貓抓老鼠永有漏網）→ 速報定位**接受帶一點雜訊**,精修留深度版。
- 白名單先放 `generate_flash.py` 常數,**暫不改 `sources.yml` 加欄位**（先觀察穩定再硬化,避免過早動源契約）。
- 可逆:刪 `generate_flash.py` + `flash-brief.yml` 即還原,故不寫 `decision_guards`。
