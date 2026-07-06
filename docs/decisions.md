# Decisions — Style Superman 下一階段主編決策

> 本文件記錄 Style Superman 的主編決策。D1–D5 源自第一輪工程規劃的「人類決策 Queue」（任務卡檔已於 2026-06-11 D7 移除，見 git 歷史）；後續決策直接在本檔新增，不另開分檔。凡涉及品牌定位、對外發布節奏、費用或供應商選型者，仍需人類最終拍板；「不可回頭」的拍板要同步在 `data/decision_guards.yml` 建守衛。
>
> **輪替規則（2026-07-06）**：本檔只保留**全量總覽表 + 最近 5 條完整條目**；Record 新決策時若完整條目超過 5 條，同 PR 把最舊的整段搬進 `docs/decisions-archive.md`（完整脈絡查 archive 或 git 歷史）。

## 決策總覽（D1–D34 全量；完整敘事 D1–D30 見 `docs/decisions-archive.md`）

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
| D12 | 工程問題看到就修不請示：branch→PR→CI 綠→自 merge，修的人負責到底 | 2026-06-13 | 無 |
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

---

## D31 — Lyst 看門狗改「發布寬限」模型（2026-07-03，兩端同日並行、以 merge #177 定案；本條為補記錄）

### 背景

2026-07-02 排程「Repo Health Patrol」首次紅（6/29 還綠）：`--strict` 唯一觸發 WARN＝「Lyst 快照落後 2 季（最新 2026-Q1）」。真因是**純日曆季差判定的結構缺陷**：新一季 Lyst Index 在季結束後約 3–4 週才發布（Q2'25＝7/23 實證；Q2'26 於 7/3 實查尚未發布），所以每年 1/4/7/10 月頭約六週 `behind` 必跳 2——**保證假警報**，但當下根本無資料可 ingest（D21 後 ingest 是對話端手動編 yaml、無自動管線可「斷」）。6/29 還在 Q2（落後 1 季）故綠、7/1 進 Q3 落後變 2 故紅，「同一份資料三天內綠轉紅」即此。patrol cron 每週一・四（`0 1 * * 1,4`），不修＝每週兩發紅通知到 Kai。

### 兩端並行與定案過程（誠實記錄）

同日兩個 session 平行修同一問題：
- Session A（本機開工巡檢）：AskUserQuestion 攤三選項，擁有者先拍「門檻 2→3」（`LYST_STALE_QUARTERS` 2→3），開 PR #175。
- Session B：直接做**發布寬限模型**並實彈驗證（Q2'26 未發布），開 PR #177。
- Session B 於 CI 綠後 merge **#177**；擁有者事後在對帳 session 以 AskUserQuestion **明確重拍板：留 #177、關 #175** → 定案。#175 被超越關閉未合：門檻 2→3 治標（每季頭六週的假警報只是延後到落後 3 的年份才消失），發布寬限模型治本（結構上消滅日曆季差假警報、且該警時警得更早——Q2 逾 ~8/14 未 ingest 即警，不用等到落後 3 季）。

### 拍板：發布寬限模型（#177 實作）

- 刪 `LYST_STALE_QUARTERS`，新 `LYST_PUBLISH_LAG_DAYS = 45`：上一季索引要「季結束 + 45 天」後才算**可 ingest**；只有「已發布逾寬限、卻沒 ingest」才 WARN，其餘 INFO。
- 語意：紅＝「有東西可以 ingest 而沒人動」，不再是「日曆走到季界」。Q2'26 若 ~8/14 後仍未 ingest，巡檢會正確重新變紅。
- 同 PR 順修 UA 誤殺三源（見 D32 追記）。

### 可逆 / guards

可逆（還原 `check_lyst_staleness` 為季差判定即回復）。無禁用識別字。延續 D21（ingest 對話化）、D29（內容節奏不該讓看門狗長期紅）、D7 反熵、「警告必配修復」。教訓另記 lessons（多端並行：同日兩案修同一問題，先 merge 者勝，後案要主動對帳、別硬 rebase 搶進）。

## D32 — 死源偵測加「重試再判死」降偽陽性（2026-07-03，開工巡檢 → 擁有者 AskUserQuestion 拍板；與 D31 同 session）

### 背景

追 D31（7/2 patrol 紅）時一併發現：`--liveness` 死源偵測是**單次探測**，外站瞬斷會抽風誤報。實證三天三組不同「死源」、且互不重疊、隔天全恢復：

- 2026-06-16：gq-korea / w-korea / vogue-korea（KR 三源 unreachable）
- 2026-07-02：bof（403）/ heddels（empty 200）/ permanent-style（empty 200）
- 2026-07-03：0 死源（上述全部活著）

每次瞬斷都被當死源追進 issue #122（6/16 那組就是它開的 issue；liveness 步驟有 `|| true`、死源本身不弄紅 job——7/2 的 job 紅是 strict/Lyst 的事，見 D31）。單探測偽陽性讓「死源」清單失去可信度（真死 vs 瞬斷分不出）。

### 邊界：只降偽陽性，不碰撤源

**撤不撤源是內容判斷、留擁有者**（D17/D18）；本決策只讓「判定死源」這個機械動作更準，不動撤源流程。liveness 仍 opt-in、不進 `--strict`（外站抖動不該讓 CI flaky，此原則不變）。

### 拍板：dead/empty/unreachable 重打一次再定讞

- `check_source_liveness` 對 dead/empty/unreachable 隔 `LIVENESS_RETRY_DELAY_SEC`（2s）重打一次，**二次仍非活**才算死源。
- **429（ratelimited）與 ok 不重打**：429 有自己的退避（`fetch_feed` 已處理），重打只會火上加油招更多 429；ok 無需重打。
- `_confirm` nested helper 包住可注入的 `probe` → 真重試邏輯可被 smoke 測（stub 首打 dead/empty/unreachable、重打回 ok → 斷言不誤報死源、且 429/ok 只打一次）；既有保序測試傳 `retry_delay=0` 維持快與確定性。
- 教訓記 `docs/lessons.md`（2026-07-03 死源抽風節）。

### 可逆 / guards

可逆（移除 `_confirm` 重試、`ex.map` 改回直接 `probe` 即還原）。無禁用識別字，不寫 `decision_guards`（純偵測穩健化、非識別字禁令）。延續 D17/D18（撤源仍留擁有者）、D7 反熵（由重複出現的抽風教訓硬化而來，非憑空加檢查）。

### 追記（2026-07-03 深審訂正）：兩組「瞬斷」實例事後都不是瞬斷

#177 實彈驗證推翻本決策背景段的病因：**7/2 三源（bof/heddels/permanent-style）是自報身分的 bot UA（StyleSupermanBot/0.1）被 WAF 擋**——同 URL 換瀏覽器 UA 即回滿 RSS（120KB/18KB/394KB）。封鎖是**間歇性**的（7/3 同在本機、同 bot UA：早上探測全過、稍後實測被擋——同視角不同結果），症狀因此長得像瞬斷；對症解是換 UA，重試只是偶爾矇過；**6/16 KR 三源是 Actions 美國 egress 地理不可達**（lessons 2026-06-16 節早有記錄）。即：驅動本決策的兩組頭牌實例，真因分別是 UA 與地理，皆非瞬斷。**重試機制保留**——它防的是真瞬斷（DNS 抖、暫時 5xx、網路 hiccup），成本 2 秒、有回歸鎖；但「死源」判讀的第一嫌疑人應是**探測視角**（egress 地理、UA），不是對面死了。lessons 同步訂正。

---

## D33 — 廢掉雲端排程 daily 代理，daily 純對話觸發（2026-07-04，擁有者 AskUserQuestion 拍板 A）

### 背景

2026-07-04 雲端排程代理（claude-code-on-the-web 遠端環境）按使用者任務提示填寫 `reports/daily/2026-07-04.md`，完成填寫後執行 `validate_repo.py` 觸發 D16 gate（凍結線 2026-06-16，之後的 daily 一律擋）。

衝突點：
- **任務提示**：填完 brief → 驗證全綠 → 開分支 → commit → push → PR → 自 merge
- **D16（2026-06-14 拍板）**：daily brief「對話即焚」、不入 `reports/daily/`；`validate_repo` 已對凍結線後的 daily 設死擋
- **CLAUDE.md**：「矛盾就停，記入 decisions.md 待拍板，不執行」

當日 brief 內容（WebSearch 多源補齊，RSS 全降級）已寫完，但因 validate_repo 紅燈未 commit，內容透過 PushNotification 傳遞給擁有者。gate 正確擋下、代理乖乖 escalate 未硬 commit——迴圈端到端跑通。

### 拍板：A（廢掉雲端排程，daily 純對話）

擁有者 2026-07-04 拍板：**不要任何雲端排程 daily 代理**。daily brief 維持「喊『早安』→ 對話端 opus 判讀 → 對話即焚」的現況（D16 未動）；擁有者「單純看、有喜歡自己會記錄」，不需要每天一支雲端排程去產、去 commit。

- **理由**：第一性原理「先刪除」——雲端排程 daily 是 pre-D16 世界觀的殘留（殭屍任務卡）；D16 早已決定 daily 對話即焚，這支排程本質上與 D16 衝突、每天撞 gate = 結構性註定失敗。廢掉根因，不是放寬防線。
- **證據**：① 2026-07-04 查 RemoteTrigger routines API `{"data":[]}`＝已無在跑的雲端 routine（無需 disable，已空）。② D16 gate 於當日實證擋下雲端誤 commit、代理正確 escalate。③ 擁有者明示偏好「對話即焚 / 自己會記錄」。
- **失效條件（何時重議）**：若擁有者未來想要「每天早上主動收到手機速報」，重開時走 **notify-only**（雲端只 PushNotification、絕不 commit/PR）或 flash 機械速報（D19）——**絕不走「雲端版 commit 進 reports/daily/」**（那會重開復發 4 次的 direct-to-master 破口，被本條與 D16 明令排除）。
- **B / C 已否決**：B（解凍 gate 讓雲端版進庫）與擁有者「對話即焚」相反、重開 rogue-commit 破口；C（雲端走 flash 加 schedule）給既有手機 dispatch 加自動排程 = 再引入 D16 所戒的無人值守自動化。兩者皆不採。

### 可逆 / guards

可逆（本條純方向拍板，未改任何 code；未來重開 notify-only/flash 排程即偏離本條，需新決策）。`flash-brief.yml` 維持 **僅 workflow_dispatch、無 schedule**（D19/D30），本條不動它。延續 D16（對話即焚）、D7 反熵（新流程不得依賴無人值守排程去產 daily）、CLAUDE.md「矛盾就停」。

## D34 — Session 分場紀律 + 驗收單一入口（token 成本，2026-07-06）

### 背景
- 真實 API 用量（按 message.id 去重）：單日 cache_read 一個月 10.1M→27.8M（2.75x）、尾端 context 171K→336K；內容還原證實大宗是工程 side-quest 疊在舊 context 上續滾（6/27 的 85%、7/5 的 100%，7/5 更跨兩天續用同場）。
- 7/5 場 33 個驗收 Bash（38%）各揹全量 context 串跑三條驗收；`tests/test_smoke.py` 內部本就執行 validate_repo 與 repo_health --consistency（與 CI 同源，ci.yml 明註不重複跑）。

### 拍板
- **驗收單一入口** `python tests/test_smoke.py`：每輪 patch 收尾跑一次；單獨除錯才直呼個別腳本（CLAUDE.md Validate 行 + 驗收命令區 + scripts/README.md 同步）。
- **Session 分場**：一場一事（daily 或一個 PR 週期）、跨日不續場、換模型重審開新場或派 repo-auditor subagent、收場儀式主動總結——這是 D12「看到就修」的分場執行（批次修），不是回到請示制；不觸 D16/D33（開場本來就一句話）。
- **Bash 衛生**（合併指令、gh/git 絕對路徑、等 CI 單呼叫、MERGE 授權措辭）+ **記帳收斂**（decisions ≤12 行、lessons ≤5 行、收場前一次寫完）+ **帳本 grep 索引讀法**（主迴圈禁止整讀三帳本），全數寫入 CLAUDE.md 對應節。

### 可逆 / guards
- 可逆（純行為約定，還原 CLAUDE.md / scripts/README.md 相關節即回復）。無禁用識別字，不寫 decision_guards。
