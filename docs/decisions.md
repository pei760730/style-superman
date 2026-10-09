# Decisions — Style Superman 下一階段主編決策

> 本文件記錄 Style Superman 的主編決策。D1–D5 源自第一輪工程規劃的「人類決策 Queue」（任務卡檔已於 2026-06-11 D7 移除，見 git 歷史）；後續決策直接在本檔新增，不另開分檔。凡涉及品牌定位、對外發布節奏、費用或供應商選型者，仍需人類最終拍板；「不可回頭」的拍板要同步在 `data/decision_guards.yml` 建守衛。
>
> **輪替規則（2026-07-06）**：本檔只保留**全量總覽表 + 最近 5 條完整條目**；Record 新決策時若完整條目超過 5 條，同 PR 把最舊的整段搬進 `docs/decisions-archive.md`（完整脈絡查 archive 或 git 歷史）。

## 決策總覽（D1–D41 全量；完整敘事 D1–D36 見 `docs/decisions-archive.md`）

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
| D40 | 自我進化迴圈補判斷軸：週挑複驗數／教訓重演計數／雷達回測扳機 + 派工跳過清單改推導 | 2026-09-03 | 無（info 級 health 檢查；文件規則） |
| D41 | 隨選單品調研落成對話規格：結論先行、尺寸用量測比基準、證據分層；避羊毛但不延伸到其他天然纖維 | 2026-10-09 | 無 |

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

## D40 — 自我進化迴圈補判斷軸（2026-09-03，擁有者「全優化」）
### 背景
迴圈（Observe→…→Learn→Next）量的全是流程衛生，判斷準不準零量測。08-29 三個錯（假死源、假 SPA、同文件違反自訂規則）的教訓全在 lessons.md 裡卻沒在動手時出現；D7「反覆出現才硬化」沒有計數器（六條自標重演無人硬化）；D11 承諾的三個月回測沒有扳機。
### 拍板
- 週挑 header 加「上週複驗：推薦 N ／ 複驗 N ／ 須更正 N」（來源＝候選池 ⚠️ 區塊，非新調查）；`check_weekly_review` 印出，缺欄位 info 提醒；W36 起算、之前 grandfather。
- 派工 prompt 的「跳過／不可讀」清單只能從 `data/sources.yml` 的 `body_fetchable:false`＋`body_fetch_note` 推導，不得手打（orchestration Step 1）。
- lessons.md soft note 標 `重演：N｜已硬化：…／未硬化`；`check_lessons_recurrence` 對 Soft 區 N ≥ 3 未標已硬化者印「該硬化了」（門檻取自本檔「不踩第三次」）。
- `check_radar_backtest_due`：`*brand-radar*` 快照滿 90 天且無 `-backtest.md` 兄弟檔 → info。**若雷達確認停用（06-19 後無產出），連 D11 一起收、此檢查同刪。**
- 三個檢查全 info 級：health.yml 走 `--strict`，判斷軸是儀表不是告警（D29）。
### 可逆 / guards
可逆（刪三個 check、還原模板欄位與 prompt 段落即可）。不寫識別字 guard；`test_repo_health` 正反向探針釘邊界（起算週、門檻 N 與 N−1、90 天當天與前一天、兄弟檔、非雷達檔名）。符合 D7：四條皆由重複教訓硬化（三例同根、六條自標重演、D11 承諾兩週後到期而無扳機）。

## D41 — 隨選單品調研落成對話規格（2026-10-09，擁有者派工）
### 背景
D10／D15 留下「真要入手是隨選的另一條（定番調研）」，但 repo 只有 6 處指標句、沒有規格；擁有者貼截圖問買不買時，回答品質全靠當場發揮（品牌史開場、拿尺碼標籤斷言能穿、羊毛不標、查不到被講成划算）。
### 拍板
- 規格在 `prompts/item_research.md`：單件第一行結論、多件先前三名再表格；尺寸只用「商品量測 vs 已有合身衣物量測」；無標籤分三層；賣家／官方／推測分開、動態資訊附查詢時間；查不到不說便宜稀有；最多問 2 題且須改變決定。
- 擁有者偏好：避羊毛；不延伸到其他天然纖維。混紡「寫比例、降一級」與其他獸毛「照常評估、附一句照顧提醒」是本條提出的解讀，擁有者可改。
- 仍對話即答、不落檔、不開卡（D9 不變）；基準量測只在對話／agent 端，不進 repo。回歸對照組 `tests/fixtures/item_research/cases.yml`（全合成）。
### 可逆 / guards
可逆（刪 prompt 與 fixture、還原指標句）。不寫 guard：識別字層無可擋之物，開卡回流已由 d9 guard 覆蓋。
