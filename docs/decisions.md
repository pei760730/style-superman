# Decisions — Style Superman 下一階段主編決策

> 本文件記錄 Style Superman 的主編決策。D1–D5 源自第一輪工程規劃的「人類決策 Queue」（任務卡檔已於 2026-06-11 D7 移除，見 git 歷史）；後續決策直接在本檔新增，不另開分檔。凡涉及品牌定位、對外發布節奏、費用或供應商選型者，仍需人類最終拍板；「不可回頭」的拍板要同步在 `data/decision_guards.yml` 建守衛。
>
> **輪替規則（2026-07-06）**：本檔只保留**全量總覽表 + 最近 5 條完整條目**；Record 新決策時若完整條目超過 5 條，同 PR 把最舊的整段搬進 `docs/decisions-archive.md`（完整脈絡查 archive 或 git 歷史）。

## 決策總覽（D1–D39 全量；完整敘事 D1–D31 見 `docs/decisions-archive.md`）

| # | 拍板結論（一句話） | 日期 | guard |
|---|--------------------|------|-------|
| D1 | 韓潮不開獨立月報：補 KR 源、daily 固定追 KR、月報加 cross-market 小節 | 首輪（2026-06-04 前後） | 無 |
| D2 | 月報主榜固定 Top 5 + 浮動觀察名單 3–5 條 | 首輪（2026-06-04 前後） | 無 |
| D3 | 挑買池採 reports/buy_shortlist/（後演進為週檔）；內容生產殘留（選題池等）全清 | 首輪；追記至 2026-06-11 | 有：positioning-no-content-production |
| D4 | 立來源 tier 判斷原則；不批量重排既有 tier | 首輪（2026-06-04 前後） | 無 |
| D5 | 不接 repo 內 LLM API、C7 不做；AI 撰寫走對話 agent | 2026-06-04 | 有：d5-no-llm-api-in-repo |
| D6 | 全域審計四項工程提案全部否決、不可回頭（共用模組／平行契約檔／設定驅動重構／月報回補） | 2026-06-11 | 有：audit-rejected-over-engineering |
| D7 | 第一性原理瘦身＋立反熵原則（不依賴人類定期勞動；新檢查只由重複教訓硬化） | 2026-06-11 | 無 |
| D8 | 終審 ≠ merge：例行產出驗證綠即自 merge；人類終審改事後反饋 | 2026-06-12 | 無 |
| D9 | 挑買卡停產、推薦回歸 brief 內（2026-06-14 反轉封存：3 卡全刪、目錄收掉） | 2026-06-12 | 有：d9-no-buy-pick-cards |
| D10 | 可購性門檻：真要入手那條只推買得到的定番；限定聯名降訊號層（scope 由 D15 重界定） | 2026-06-12 | 無 |
| D11 | 品牌雷達：對話觸發的 10 大品牌深挖（分 tier、三層證據、六欄、存 analysis 快照） | 2026-06-12 | 無 |
| D12 | 工程問題看到就修不請示：branch→PR→CI 綠→自 merge，修的人負責到底（D34 起分場執行：daily 場只登記、工程場修） | 2026-06-13 | 無 |
| D13 | 不拆歐美兩區；歐洲深度走每週深挖位；收 Drapers（tier2 通路 intel） | 2026-06-13 | 無 |
| D14 | 全砍 score_trends 加權評分框架；趨勢挑選回歸主編判斷 | 2026-06-14 | 無 |
| D15 | 推薦框架從「買清單」改「在紅單品情報」：🎯 對我最相關 For Me，不催買 | 2026-06-14 | 無 |
| D16 | 砍雲端排程 routine，daily brief 全對話觸發、對話即焚不入庫（2026-06-26 加 validate gate） | 2026-06-14 | 無 |
| D17 | 撤除 Mercari 日本量化板（4 年陳貨、替代源實測全擋） | 2026-06-14 | 無 |
| D18 | 新增來源兩道門：近 30 天持續產出＋夠權威，寧缺勿濫 | 2026-06-14 | 無 |
| D19 | 手機速報層：白名單硬資訊源純機械抽取（generate_flash，零 LLM） | 2026-06-16 | 無 |
| D20 | 不接任何 Google 常設整合；YT 話語層走對話臨場查 | 2026-06-17 | 無 |
| D21 | 不建需擁有者離開對話操作的人工介面；移除看榜 CLI＋存榜助手 | 2026-06-20 | 無 |
| D22 | 採用 Firecrawl keyless 補封鎖源 roundup（限對話端 MCP，不進腳本） | 2026-06-20 | 無 |
| D23 | Firecrawl 重開韓國量化榜（KREAM／MUSINSA）；ZOZO 標永久死界 | 2026-06-20 | 無 |
| D24 | 用 SNKRDUNK 重建日本球鞋轉售量化板（部分逆轉 D17 的留空） | 2026-06-21 | 無 |
| D25 | 週挑改「週一早安」自動觸發、存檔 reports/buy_shortlist/ | 2026-06-23 | 無 |
| D26 | 週挑改「每日累積候選池 → 週一收斂」，不週一現抓 | 2026-06-23 | 無 |
| D27 | 多區掃描固化成宣告式 scan-manifest（主控＝對話 agent，不做會跑 subagent 的腳本） | 2026-06-23 | 無 |
| D28 | 抄 market-researcher 骨架的結構紀律不抄 runtime（roles／output_schema／防注入；訂正：reader 用 general-purpose） | 2026-06-23 | 無 |
| D29 | 移除 patrol 對週挑的硬 SLA（repo_health 降 INFO），D25/D26 機制保留 | 2026-06-24 | 無 |
| D30 | 退役刪除 daily-brief workflow（與 D16 freeze gate 機制互斥） | 2026-06-27 | 無 |
| D31 | Lyst 看門狗改「發布寬限」模型（季末＋45 天未 ingest 才警） | 2026-07-03 | 無 |
| D32 | 死源偵測加「重試再判死」降偽陽性（追記：頭牌實例真因是 UA／egress 視角） | 2026-07-03 | 無 |
| D33 | 廢雲端排程 daily 代理，daily 純對話觸發 | 2026-07-04 | 無 |
| D34 | Session 分場紀律＋驗收單一入口（token 成本） | 2026-07-06 | 無 |
| D35 | 速報改純對話觸發，廢 flash-brief.yml 按鈕層 | 2026-07-25 | 無 |
| D36 | 正文抓取改本機優先（fetch_article.py）；`body_fetchable` 是「視角 × 源」的量測，封源要附本機證據 | 2026-07-28 | 無（validate_repo 契約檢查） |
| D37 | daily For Me 由對話 agent 回流 gitignored 候選池，作為唯一 writer | 2026-07-30 | 無 |
| D38 | rankings 硬數據保留並成為週挑「炒作 vs 真」必引依據 | 2026-07-30 | 無 |
| D39 | reader 證據等級、不可讀登記與負面結論對照組納入 schema 契約 | 2026-08-15 | 無（validate_repo 契約檢查） |

## D34 — Session 分場紀律 + 驗收單一入口（token 成本，2026-07-06）

### 背景
- 真實 API 用量（按 message.id 去重）：單日 cache_read 一個月 10.1M→27.8M（2.75x）、尾端 context 171K→336K；內容還原證實大宗是工程 side-quest 疊在舊 context 上續滾（6/27 的 85%、7/5 的 100%，7/5 更跨兩天續用同場）。
- 7/5 場 33 個驗收 Bash（38%）各揹全量 context 串跑三條驗收；`tests/test_smoke.py` 內部本就執行 validate_repo 與 repo_health --consistency（與 CI 同源，ci.yml 明註不重複跑）。

### 拍板
- **驗收單一入口** `tests/test_smoke.py`：可用 `python tests/test_smoke.py` 直接執行，也可由 pytest 收集並執行同一套 `main()`；每輪 patch 收尾只跑一種，單獨除錯才直呼個別腳本。
- **Session 分場**：一場一事（daily 或一個 PR 週期）、跨日不續場、換模型重審開新場或派 repo-auditor subagent、收場儀式主動總結——這是 D12「看到就修」的分場執行（批次修），不是回到請示制；不觸 D16/D33（開場本來就一句話）。
- **Bash 衛生**（合併指令、gh/git 絕對路徑、等 CI 單呼叫、MERGE 授權措辭）+ **記帳收斂**（decisions ≤12 行、lessons ≤5 行、收場前一次寫完）+ **帳本 grep 索引讀法**（主迴圈禁止整讀三帳本），全數寫入 CLAUDE.md 對應節。
- **量測判準／升級 tripwire**：成功＝單日 cache_read 回到 8–12M 區間；一個月後複查（2026-08-06 前後）若 session 尾端 context 仍 >200K 或單場驗收執行 >20 次 → 啟動 D7 第二波硬化（結構性工具下沉／檢查）。

### 可逆 / guards
- 可逆（純行為約定，還原 CLAUDE.md / scripts/README.md 相關節即回復）。無禁用識別字，不寫 decision_guards。

## D36 — 正文抓取改「本機優先」，`body_fetchable` 正名為視角量測（2026-07-28，擁有者「認真修 把它修好」）

### 背景

2026-07-28 daily brief 交付時，我把 Permanent Style 的 Luca Museo 棉西裝評測、GQ 亞麻襯衫 13 選、drapers 的 Frasers/Hugo Boss 收購三條**整條不列**，理由是「WebFetch 403、Firecrawl 備援沒掛上」。擁有者要求深挖，本機實測七源打臉這個理由：

| 源 | WebFetch 視角 | 本機視角（瀏覽器 UA） |
|---|---|---|
| permanent-style / gq / esquire / drapers / bof / fratello | 403 或空殼 | **200**，正文與價格齊全（PS $3,800、GQ $120/$90/$50/$118/$345/$148、Timex $199→$133、drapers 收購案數字、BoF LVMH 數字） |
| put-this-on / wwd-japan | 403（2026-06-14 標記） | **200** 全文 |
| sneakernews | 403 | **403（換 bot UA 亦然）＝真站級封鎖** |

**七個裡六個是假陰性。**

### 根因（四層）

1. `data/sources.yml` 的 `body_fetchable` 是 2026-06-14 用**單一視角（WebFetch）**量出來的，卻被寫成「源的永久屬性」，還被 `prompts/daily_trend_brief.md` 引用成硬規則。
2. **同一個概念錯誤 repo 已經修過一次、但沒橫向套用**：#186 四次誤殺 → #193「視角感知分類」已在 RSS 死活軸硬化（`403＝blocked＝活著但拒收本視角，永不判死`），正文抓取軸卻仍把 403 當永久事實。
3. **D22 的備援（Firecrawl MCP）在真正跑 brief 的環境不存在**：`.mcp.json` 設了 server，但實跑 session 沒掛上工具 → 規則寫的三層備援實際只有一層。
4. **能用的路早就在 repo 裡、只差沒接線**：`collect_raw_signals.py` 用本機 urllib + 瀏覽器 UA 打同一批站全 200（#177 已為此改過 UA），但它只收 RSS 不收正文。#177 那次**只改了 UA、沒回頭複驗 `body_fetchable` 名單**，假陰性就這樣留了 44 天。

### 拍板

- **新增 `scripts/fetch_article.py`**（本機、純機械、零 LLM，守 D5）：URL → 標題 / 發佈日 / 正文純文字；退出碼分辨 403（本視角被拒）／連不上／正文過短（付費牆・JS 殼）。**本機專用**：Actions egress 會 403，不進 CI、不排程。
- **取內文順序改為**：① 本機 `fetch_article.py` → ② WebFetch → ③ Firecrawl（若掛得上，明文標註「不保證存在」）→ ④ 才整條不列。
- **`body_fetchable` 正名**：判定視角＝**本機**（brief 實跑的地方，D30/D35）；標 `false` 必須附 `body_fetch_note`（本機實測日期＋現象），`validate_repo.check_sources` 會擋。六個假陰性撤旗標，sneakernews 保留並附證據。
- 不新增來源（D18 不動）：`fetch_article` 對不在 sources.yml 的網域只印提醒、不擋——單次引用 ≠ 收進來源清單。

### 可逆 / guards

可逆（刪腳本 + 還原旗標即回復）。**不寫 `decision_guards`**：這裡要擋的不是某個識別字，而是「沒有本機證據就封源」，已用 `validate_repo` 契約檢查硬化（比識別字守衛更貼題）；回歸鎖在 `tests/test_smoke.py` 9i / 9i-2（含 `known_domains` 的 `lstrip("www.")` 字元集合陷阱）。延續 #193 視角感知、D5 零 LLM、D18 不新增來源、D30/D35 本機執行。

---

## D37 — daily For Me 回流候選池：對話 agent 為唯一 writer（2026-07-30）

### 背景

`_candidates.draft.md`（D26 候選池）**沒有任何 writer**：`generate_daily_brief.py` 不寫它、`generate_weekly_buy_picks.py` 只帶「訊號依據」文字不讀它。每日 For Me 是對話端 ephemeral（D16）、寫完即焚 → 池停在 2026-07-04、週挑週一收斂看不到本週 lane 料 → **W28/W30 漂成通用榜的根因**。守 D5（腳本不呼叫 LLM）：不能靠腳本讀 ephemeral brief 回填。

### 拍板

- **每日收斂 Step 6（`prompts/daily_scan_orchestration.md`）**：對話 agent 交付 For Me 後，把當日 For Me **追加**進 `_candidates.draft.md`（gitignored 草稿、非 commit）；同單品次數 +1、更新新事實。此為 daily→weekly 複利的**唯一接口**。
- 週挑（`prompts/weekly_buy_picks.md` input 0）本就以候選池為收斂主依據 → 接上後 W32 起吃得到本週 lane 料。
- 守 D5/D16：writer 是對話 agent、非腳本；池是 gitignored 草稿、不入版控、不改 ephemeral 契約。

### 可逆 / guards

可逆（回退 orchestration Step 6 即可）。**不寫 guards**：這是「行為要發生」的正向流程、非「禁某識別字」，靠文件規則 + 每日執行硬化（守 CLAUDE.md「能用文件規則就別寫 code」）；上線後看真實使用（若又停更＝行為沒發生，追根因不補規則，D 規則紀律）。延續 D26 候選池、D29 週挑落後只 INFO。

---

## D38 — rankings 硬數據脊椎：救不砍，週挑「炒作 vs 真」必交叉引用（2026-07-30）

### 背景

`data/rankings/*.yml`（Lyst / KREAM / MUSINSA / SNKRDUNK / StockX）D21 後改「AI 對話中直接編」，但**沒人編 → 全停在 6 月**（Lyst 6/12、StockX 6/10）、health「Lyst 落後 2 季」。週挑「炒作 vs 真」目前純判讀、無量化背書＝半套。問：救還是砍。

### 拍板

- **救（deepen），不砍**：rankings 是「炒作 vs 真」唯一客觀依據，砍了週挑核心使命（找溢價陷阱/季節錯位）就沒硬地基。
- **機制（`prompts/weekly_buy_picks.md` 挑選規則）**：「炒作 vs 真」從只對照 `trend_history` 升級成**必加對照 `data/rankings` 量化名次** + 新鮮度守則（逾發布 lag 明標過期、對話端刷新）。
- **刷新紀律**：MUSINSA 抓 `주간`週榜（集計 confirmed 當年）非 `월간`月榜陷阱（承 C）；反爬站走 Firecrawl/WebFetch 反驗後寫 dated 快照（D22–D24）。
- **範圍誠實**：本 PR 只上機制；5 個 6 月快照的實際 data 刷新是另一次驗證 pass（KREAM/SNKRDUNK/Lyst 反爬、本 session 未掛 Firecrawl → 不編假數字）。

### 可逆 / guards

可逆（回退挑選規則即可）。不寫 guards（正向流程）。承 C（週榜非月榜）、D22–D24（反爬快照）、D29（health 不因 rankings 落後變紅）。

---

## D39 — reader 證據紀律納入 schema 契約（2026-08-15，擁有者派工拍板）
### 背景
CIOTA（08-04/06）、KR 來源健康檢查（08-11）、A.PRESSE（08-15）三次把渲染／讀取結果升級成「停更、死、全完售」事實；reader JSON 又沒留下未讀與驗證層級。
### 拍板
- item 必填 `evidence`（親測／轉述未複核）；選填 `unreadable[]` 登記讀不到，`control_checks[]` 留負面結論的對照組。
- reader 固定官網優先、讀不到不下結論、負面結論先跑對照組；電商完售判讀原始 HTML。
- `validate_repo.check_reader_schema_contract` 交叉檢查 schema 與 prompt JSON 範例，擋漏必填、未知欄位與 enum 外值。
### 可逆 / guards
可逆（回退 schema、prompt 與 check 即可）。不寫識別字 guard；契約 gate 與 `test_smoke` 正反向探針直接擋漂移。
