# Style Superman

> **個人男裝潮流情報 + 挑買決策系統**
> 每天把全球男性潮流訊號（日潮 / 韓潮 / 歐美）→ 收集 → 分類 → 主編判斷 → 收斂成「對我有用」的挑買判斷。

**這套系統服務的對象只有我自己**：一個追男裝潮流、會親手挑單品入手的玩家。
它**不是**內容生產 / 拍片管線，與 IG 漲粉 / 創作者經營**完全無關**——產出永遠不含「可拍選題」「content hooks」類東西（2026-06-05 拍板，守衛強制，見[防線](#防線怎麼防止系統跑偏)）。

**我唯一的工作是兩件事：讀，和買不買。** 每日 brief 由我說「早安」、agent 在對話當場跑出來（D16，2026-06-14：比排程 routine 品質高又省額度）；工程 / 健檢環節全自動（D8：驗證綠即自 merge）。覺得哪天判斷錯了，跟 agent 講一句——反饋會記進 [docs/decisions.md](docs/decisions.md) / [docs/lessons.md](docs/lessons.md)，產線修正。

---

## 系統的一天（時間軸）

```txt
我起床後     跟 agent 說「早安」→ agent 照 data/scan_units.yml 對日/韓/歐美 + 日系 lane
             各派一個平行唯讀 reader subagent（收 RSS + WebSearch/WebFetch 挖 picks、只回結構化 JSON；D27/D28）
             → orchestrator 收斂去重、補密度（任一區 <3 條主動補搜、不交白卷）
             → 在對話端上完整 brief（頭條 + 日/韓/歐美三區塊 + 🎯 For Me）
             → 我直接讀，先看最下面的 🎯 For Me（對我最相關的在紅單品）
```

> **2026-06-14 起：每日 brief 全對話觸發,沒有排程 routine（D16）。** 雲端 routine 在無人盯時會
> 退化成「只有標題的空殼 roundup」；對話裡 agent 認真跑(真收訊號 + 真 WebFetch 挖 picks)品質更高、
> 又省 routine 額度。產出在對話讀,不入 `reports/daily/`(要封存再說)。

> **手機在外、開不了電腦?** 從手機按一下 GitHub Actions 跑 `flash-brief.yml`,拿到 ⚡ Style 速報([reports/flash/](reports/flash/))——
> 白名單硬資訊源**純機械抽取(零 LLM)**,回答「今天有什麼上了/漲了/併了」+ 現成 SKU/價格/發售日。
> 趨勢判讀 + 挖 picks 仍是桌面對話深度版的活(D19,2026-06-16)。

**每週一**：說「早安」= daily + 週挑 Head-to-Toe **一起自動端上、不需額外關鍵字**（D25）。週挑不是週一現抓——每天 brief 的 🎯 For Me 在紅單品**累積進滾動候選池**，週一**收斂**（反覆出現=真在升、單日=雜訊；D26）。每週至少一張趨勢深挖卡（歐美優先，對話觸發）。
**每月初**：說一聲跑歐美 / 日本月報（**對話觸發**；日本線 2026-07 起）。Lyst Q2 出刊（7 月）時說一聲 ingest 進 rankings。
**每週一、四 09:00**：自動健檢巡檢——格式跑偏、文件↔程式碼漂移、月報斷更、**死源（liveness）**會**自動開 `repo-health` issue**，所以 GitHub 通知出現它 = 系統出事了，其他時候不用管。（daily 斷更看門狗已隨 D16 移除——brief 改對話觸發、不入 `reports/daily/`，無檔可數；**週挑落後 D29 後降 INFO**——仍顯示供參考，但不再讓巡檢變紅 / 不開 issue。）

---

## 產出說明書（你會收到什麼、怎麼讀）

### 📅 Daily Brief — [reports/daily/](reports/daily/)（每天）

- **先看最下面 `🎯 對我最相關 For Me`**——**在紅單品情報**（D15，非買清單）：**單品｜是什麼｜在哪紅（歐美/日/韓）｜對我衣櫥的意義｜價格/型號（辨識用）**。目的是知道現在在紅什麼,不催買;真要入手再開口（走定番調研）。
- 往上是 3–5 條頭條（每條固定回答「是什麼 / 為什麼是現在 / 對我的意義」）+ **三個地區區塊：🇯🇵 日潮 10–15 條、🇰🇷 韓潮 8–12 條、🌍 歐美 10–15 條**（每則兩行式：粗體標題行含日期/價格/來源 + 縮排一句簡介）+ 明日 watchlist。頭條＋區塊合計約 30–45 條/日。
- **讀法慣例**：連續趨勢用增量寫法——同一件事第二天只寫新增事實，背景用「讀法見 YYYY-MM-DD brief」回連，所以看到回連別當漏寫，是防止每天重講一遍。
- 訊號弱的日子會誠實寫「今日訊號偏弱」，不硬湊。

### ⚡ Style 速報 — [reports/flash/](reports/flash/)（手機可觸發，D19）

- **手機在外、開不了電腦時的速報層**：從手機開 GitHub Actions 手動跑 `flash-brief.yml`，白名單硬資訊源（hypebeast / sneakernews / WWD / fashionsnap / senken / 錶源…）**純機械抽取（零 LLM，守 D5）**，排成「今天有什麼上了 / 漲了 / 併了」+ 現成 SKU / 價格 / 發售日。
- **刻意不做趨勢判讀 / 不挖 picks / 不下熱度結論**——那是桌面對話深度版（opus）的活。只做機械抽取、不讓 LLM 假裝判讀，從根上不退化成被砍掉的「空殼 roundup」（D16）。
- 與深度版分流：速報落 `reports/flash/`、深度 brief 在對話讀（不入版控），互不踩。

### 🛍 週挑 Head-to-Toe — [reports/buy_shortlist/](reports/buy_shortlist/)（每週一，自動）

- **觸發**：每週一說「早安」= daily brief + 週挑一起端上，**不需關鍵字**（D25）。
- **怎麼挑**：不是週一現抓——每天 brief 的 🎯 For Me 在紅單品**累積進滾動候選池** `_candidates.draft.md`（gitignored），週一**收斂**：反覆出現=真在升（入選）、單日=雜訊（剔除）（D26）。
- 從頭到腳 **5 區（頭部 / 上身 / 下身 / 足部 / 配件）× 各 3 樣**，每樣含：是什麼｜在哪紅（歐美/日/韓）｜價格/型號（辨識用）｜為什麼這週在紅｜炒作 vs 真（週期位置）。
- 直接跳 **「🎯 本週最該記住的一個」**——15 樣裡訊號最強 × 最值得記住的那個。
- 這是「各部位在紅什麼」的情報榜（D15，**非買清單**）；難不難買不是門檻，真要入手再隨選。

### 📊 月度熱度速報 — [reports/monthly/](reports/monthly/)（每月，歐美 `-eu` + 日本 `-jp`）

- 主榜固定**品牌 Top 5 + 單品 Top 5**（含配件），收尾是「🛒 本月挑買方向」2–3 條。
- **信心標示怎麼讀**：每條掛訊號層級——L1 硬數據（Lyst / StockX 榜）＞ L2 已確認事件（官方公告、發售）＞ L3 多源媒體共識 ＞ L4 弱訊號（只能當觀察）。**L4 撐不起「熱賣 / 爆紅」這種話**，看到「待查」就是真的查不到，不是偷懶。
- 日本線量化基準弱（ZOZO 不可自動收），信心刻意保守，是特性不是缺陷。

### 🔬 趨勢深挖卡 — [reports/analysis/](reports/analysis/)（每週至少一張，歐美優先）

- 把連續 2–4 週出現的最強跨源趨勢寫成長線資產：跨源查證 → 生命週期 → 全價位帶落地 → 挑買判斷。範本：washed denim 卡。一年累積 ≈50 張 = 自己的趨勢資料庫。

### 🎯 品牌雷達 — 對話觸發（D11）

- 對話說 **「深挖 + 品牌 / 關鍵字」**（例：「深挖 A.PRESSE」「深挖 日系 elevated」）→ agent 產 **≤10 個品牌的雷達**：分 tier（動能 / 權威）+ **與我衣櫥的 lane 相容度** + 每個「是什麼 ＋ 為什麼現在」。把零散的品牌好奇變成結構化、可留存的情報，不再只活在對話裡。
- 範本 `prompts/brand_radar.md`；可存進 [reports/analysis/](reports/analysis/) 當主題分析，或當對話讀。**不排程**（D11）。

### 📈 想查什麼最紅（隨時）

在對話跟 AI 說「現在歐美/日本/韓國什麼最紅」——AI 讀 [data/rankings/](data/rankings/) **五榜快照**（歐美 Lyst / StockX、韓國 KREAM / MUSINSA、日本 SNKRDUNK，最新在上）回報。**不需打指令**（D21：人工看榜 CLI 已移除，擁有者只走對話）。
要**即時當期榜**時，AI 用 **Firecrawl keyless 對話端抓**（D22–D24）→ 反向驗證 → 寫一筆 dated 快照進 yaml：KREAM / MUSINSA 逐位榜（D23）、SNKRDUNK 日本球鞋轉售榜（D24，部分重開日本量化板）。**ZOZO 為 Akamai 級永久死界**（Firecrawl 也過不了）；日本服飾/精品量化仍空，看 daily brief 日潮區。Mercari 2013→2022 陳貨已撤（D17）。

---

## 自動化全貌（誰、什麼時候、跑什麼、怎麼提交）

| 執行者 | 時間 | 做什麼 | 提交方式 |
|---|---|---|---|
| 對話 agent（**唯一的內容入口**） | 說「早安」/ 需要時 | **每日 brief**（照 `scan_units.yml` 派工平行唯讀 reader → 收訊號 + WebFetch 挖 picks → orchestrator 收斂去重 → 對話端上，D27/D28）；趨勢深挖卡；**品牌雷達**（「深挖 A.PRESSE」式，D11）；**週挑**（週一說「早安」一起端）；**月報**（月初說一聲，歐美 / 日本，日本線 2026-07 起）；**Lyst Q2 ingest**（7 月榜出說一聲）；臨時任務 | 內容在對話讀（不入版控）；需封存 / 工程改動才走**分支 + PR**，驗證綠自 merge（D8） |
| GitHub Actions `flash-brief.yml` | **手機手動 dispatch**（D19） | ⚡ 速報：白名單硬源純機械抽取（零 LLM），落 `reports/flash/<date>.md` | 手機按一下 = 有人盯，不違 D16 砍排程 |
| GitHub Actions `health.yml` | 每週一、四台北 09:00 | `repo_health --strict` 巡檢（新鮮度 + 一致性 + 守衛 + 產出契約）+ `--liveness` 死源探針（continue-on-error，限速不算死） | 未過 / 偵測死源 → 自動開 / 更新 `repo-health` issue |

> daily-brief workflow 已於 **D30（2026-06-27）退役刪檔**——D16 後 daily 全對話觸發，該 workflow 與 D16 freeze gate 互斥、要交棒的 signals 又被 gitignore，實質無用。本機收 RSS 失靈時直接在本機跑 `generate_daily_brief.py`（見 docs/operating_manual.md）。
| GitHub Actions `ci.yml` | 每個 PR | validate + smoke（Python **3.9 + 3.12** 雙版）+ ruff lint（py39） | 紅燈 = 不能 merge |

> **0 支雲端 routine（D16，2026-06-14）。** 每日 brief 連同週挑 / 月報 / Lyst Q2 全部**對話觸發**——
> 排程 routine 在無人盯時品質退化（空殼 roundup），對話跑品質更高又省額度（合反熵 D7）。

**鐵則：所有內容產出由對話 agent 跑；要封存或工程改動一律走分支 + PR。** 直推 master 會繞過 CI 上的全部防線——這是殭屍任務卡第三例的教訓（[docs/lessons.md](docs/lessons.md)）。

**叫 agent 做事：** 守則在 [CLAUDE.md](CLAUDE.md)（開工先跑 `repo_health.py`）。例行產出與工程 PR 驗證綠即自 merge（D8）——我的終審是事後反饋，買不買的決策在現實世界，不在 git。

---

## 關鍵拍板（系統為什麼長這樣）

完整背景與選項見 [docs/decisions.md](docs/decisions.md)，這裡是速覽：

| # | 拍板 | 一句話 |
|---|------|--------|
| D1 | 韓潮不開獨立月報 | daily 固定 KR 追蹤 + 月報 cross-market 小節；KR 訊號量達門檻才升級 |
| D2 | 月報主榜固定 Top 5 | 另列浮動觀察名單收早期訊號——主榜只收高信心 |
| D3 | 挑買 shortlist 取代選題池 | 個人挑買重定位（2026-06-05）的落地，內容生產視角全面移除 |
| D4 | 來源 tier 不批量改 | 重分級走資料 PR 逐筆說明，來源可信度是內容判斷 |
| D5 | repo 內不接 LLM API | AI 撰寫走對話 agent；腳本只做確定性工作、不管 API key |
| D6 | 審計四提案全否決 | 共用模組 / 設定外部化等「看起來專業」的工程一律不做，守衛防回流 |
| D7 | 第一性原理瘦身 | 砍死迴圈與手動勞動依賴；立反熵三原則（新流程不得依賴人類定期手動勞動） |
| D8 | 終審 ≠ merge | 例行產出驗證綠即自 merge；main 是系統記憶不是批准章，我的終審是事後反饋 |
| D9 | 挑買卡停產 | 推薦只寫在 brief For Me / 週挑，深度功課我自己做 |
| D10 | 可購性門檻 | 推薦位只推「隨時買得到」的定番款；限定聯名只當訊號、不當入手點 |
| D11 | 品牌雷達 | 「深挖 <關鍵字>」對話觸發，產 ≤10 大品牌雷達（分 tier + lane 相容度）；不排程 |
| D12 | 看到問題就修 | 工程修正不需事前請示、修的人負責到底；內容判斷仍留人類 |
| D13 | 歐美不拆每日兩區 | 歐洲男裝肥料不足，深度走每週深挖位；順手收 Drapers 當零售 intel |
| D14 | score_trends 停用 | 砍加權評分框架，趨勢挑選回歸主編判斷（評分從未真正驅動挑選） |
| D15 | 推薦改在紅情報、非買清單 | brief For Me / 週挑從「買清單」轉「現在在紅什麼單品」；不催買、不附死線 |
| D16 | 砍雲端排程 routine | daily 連週挑 / 月報全對話觸發（說「早安」當場跑）；0 routine、省額度、品質更高 |
| D17 | 撤 Mercari 日本量化板 | 2013→2022 陳貨、年報已無時尚榜、替代源全 bot 擋；日本看 daily 日潮質化 |
| D18 | 新增來源兩道門 | 加來源前先驗 ① 近 30 天持續產出 ② 夠權威（非聚合 / SEO）；仍需擁有者拍板 |
| D19 | 速報層 generate_flash | 白名單硬源純機械抽取（零 LLM）；手機可獨立 dispatch，補桌面對話 brief 手機看不到的缺口 |
| D20 | Google 體系整合評估 | 不接常設源 / CLI / API / Cloud（Google 強項全落在被 D5/D7/D16 封死的內容層）；YT 話語層走對話臨場 WebSearch |
| D21 | 不建需離開對話的人工介面 | 移除排行看榜 CLI + 存榜助手（機器無呼叫者、擁有者只走對話）；排行資料改 AI 對話端直接編 yaml |
| D22 | 採用 Firecrawl keyless | 封鎖源 roundup 改 Firecrawl 對話端 scrape（免 key、結構化抽 picks）；限定對話端、不進腳本 |
| D23 | Firecrawl 重開韓國量化榜 | KREAM / MUSINSA 逐位榜由 AI 對話端 Firecrawl 抓→寫 dated 快照；確認 ZOZO 為 Akamai 級永久死界 |
| D24 | SNKRDUNK 重建日本球鞋板 | 日本量化板部分重開——球鞋轉售榜（日版 StockX）可 Firecrawl 抓；服飾/精品板仍空 |
| D25 | 週挑改「週一早安」自動觸發 | 週一說「早安」= brief + 週挑一起自動產出，不需關鍵字；週挑存檔（解掉看門狗空叫矛盾） |
| D26 | 週挑改每日累積候選池 | 每天 For Me 累積進滾動候選池 → 週一收斂（反覆出現=真在升、單日=雜訊），不週一現抓 |
| D27 | 多區掃描固化成宣告式 scan-manifest | 每日掃描照 `data/scan_units.yml` 派工給平行唯讀 reader subagent；主控＝對話 agent（非腳本）、不加 .py / 不接 API / 不排程 |
| D28 | market-researcher 骨架升級掃描編排 | 抄 financial-services 骨架紀律（角色分離 orchestrator/reader/auditor + reader 強制 JSON schema + 防注入），不引 runtime；reader 用 general-purpose（能查網）|
| D29 | 移除 patrol 對週挑硬 SLA | repo_health 週挑落後 warn→info；CI 不再為週挑逾期變紅（避免警告衰退成噪音、紅燈恢復「真壞了」語意）|
| D30 | 退役並刪除 daily-brief workflow | D16 後 daily 全對話觸發，該 workflow 與 D16 freeze gate 互斥、signals 又被 gitignore，實質無用 |

---

## 防線（怎麼防止系統跑偏）

1. **不虛構**：沒來源就標 `待查`；不編造名次、百分比、「爆紅」結論（[CLAUDE.md](CLAUDE.md) 核心假設）。
2. **決策守衛**（[data/decision_guards.yml](data/decision_guards.yml) + `repo_health.py`，ERROR / CI 擋）：「不可回頭」的拍板留下禁用識別字（清單見守衛檔本身），任何 PR 把它們寫回活文件直接紅燈——**排程 agent 拿舊任務卡產的東西進不了 master**。
3. **產出契約檢查**（WARN / 巡檢盯）：重定位（2026-06-05）之後產的 daily / monthly 必含現行段落（`🎯 對我最相關 For Me`／`🛒 本月挑買方向`）、不得含舊世界觀識別字；日期已過仍殘留 `{{…}}` 佔位 = 空轉殭屍 WARN。
4. **歷史快照不溯及**：`reports/` 是封存快照，產出後不回改；重定位前的舊報告掛豁免註記保留原樣，**不要**把它們改寫成新格式。
5. **D16 freeze gate**（[validate_repo.py](scripts/validate_repo.py) `DAILY_FREEZE_CUTOFF=2026-06-16`，CI 擋）：daily brief 對話即焚、不入 `reports/daily/`——任何日期 > 凍結線的 `reports/daily/*.md` 被 commit 進來直接 CI 紅、PR merge 不了（歷史檔 ≤06-16 grandfathered；flash 不在此列）。連四犯（06-23 routine + 06-24/25/26 平行 session）後從「靠記性」硬化成 gate（D16 機制化，2026-06-26）。
6. **教訓硬化路徑**：踩坑先記 [docs/lessons.md](docs/lessons.md)（soft note），反覆出現才硬化成檢查——不為單次事故加終身檢查（上方 D16 freeze gate 就是「連四犯才硬化」的範例）。

---

## 目錄結構

```txt
style-superman/
├── README.md                 # 你現在看的這份
├── CHANGELOG.md              # 系統演進紀錄（能力層變更）
├── CLAUDE.md                 # agent 執行守則（定位鐵則 + Self-Evolution Loop）
├── requirements.txt          # Python 相依（標準庫 + pyyaml）
├── .mcp.json                 # Firecrawl keyless MCP 設定（對話端即時榜抓取，D22）
├── data/                     # 知識底層（長期維護，不是快照）
│   ├── sources.yml           # 情報來源 43 個（31 個可 RSS 自動收；撤 Mercari D17、加錶源 Fratello/Monochrome）
│   ├── trend_taxonomy.yml    # 趨勢分類體系（系統的「語言」）
│   ├── trend_history.yml     # 趨勢生命週期基準（炒作 vs 真趨勢；雷達 / 深挖 prompt 引用）
│   ├── brands.yml            # 追蹤品牌（contemporary lane + 日本デニム殿堂 + amekaji 古著魂；taste:anchor 標個人品味錨點）
│   ├── people.yml            # 追蹤人物
│   ├── decision_guards.yml   # 決策守衛：禁用識別字（CI 強制）
│   ├── scan_units.yml        # 每日掃描派工清單（日/韓/歐美 + 日系 lane，配額/維度/reader schema；D27/D28）
│   └── rankings/             # 量化排行快照（最新在上；即時榜由 Firecrawl 對話端抓 D22–D24）
│       ├── lyst-index.yml    #   歐美：Lyst Index 季度
│       ├── stockx.yml        #   歐美：StockX 年度
│       ├── kream.yml         #   韓國：KREAM 轉售（Firecrawl 重開 D23）
│       ├── musinsa.yml       #   韓國：MUSINSA 銷售榜（Firecrawl 重開 D23）
│       └── snkrdunk.yml      #   日本：SNKRDUNK 球鞋轉售（日版 StockX，D24 重建）
├── reports/                  # 封存快照（產出後不回改）
│   ├── daily/                # 每日 brief（YYYY-MM-DD.md）
│   ├── flash/                # ⚡ 速報（YYYY-MM-DD.md；手機 dispatch，純機械抽取 D19）
│   ├── buy_shortlist/        # 週挑 Head-to-Toe（YYYY-Wnn.md）
│   ├── monthly/              # 月度熱度速報（YYYY-MM-eu.md 歐美；YYYY-MM-jp.md 日本，2026-07 起）
│   └── analysis/             # 趨勢深挖卡 + 主題分析（每週至少一張，歐美優先）
├── prompts/                  # AI 內容工作模板（與 templates 欄位互為契約）
│   ├── daily_trend_brief.md          # 每日 brief
│   ├── weekly_buy_picks.md           # 週挑 Head-to-Toe
│   ├── monthly_heat_report.md        # 月度熱度速報
│   ├── trend_analysis.md             # 趨勢深挖卡
│   ├── brand_radar.md                # 品牌雷達（「深挖 <關鍵字>」，D11）
│   ├── daily_scan_orchestration.md   # 每日多區掃描派工＋收斂協定（D27/D28）
│   ├── region_reader.md              # 單區/lane 掃描工人（唯讀 + 防注入 + 只回 schema JSON，D28）
│   ├── scan_auditor.md               # brief 唯讀稽核（配額/格式/For Me 契約 → pass/fail，D28）
│   └── ranking_ingest.md             # 排行快照 ingest 指引
├── templates/                # 產出物固定格式（格式即契約）
├── scripts/                  # 自動化腳本（用法見 scripts/README.md）
│   ├── generate_daily_brief.py          # brief 骨架（--with-rss 含收集）
│   ├── generate_weekly_buy_picks.py     # 週挑骨架
│   ├── generate_monthly_heat_report.py  # 月報骨架
│   ├── generate_flash.py                # ⚡ 速報：白名單硬源純機械抽取（零 LLM，D19）
│   ├── collect_raw_signals.py           # RSS → raw_signal_pack
│   ├── track_rankings.py                # 月報用的純函式 helper（lyst 季對季比對）
│   ├── validate_repo.py                 # 格式契約檢查（CI）
│   └── repo_health.py                   # 健檢：新鮮度 + 一致性 + 守衛 + 產出契約 +（--liveness 死源探針）
├── tests/                    # smoke 測試（無需 pytest）
├── docs/
│   ├── system_design.md         # 架構設計
│   ├── style_strategy.md        # 情報支柱、調性與個人成功指標
│   ├── flow_calendar.md         # daily → weekly → monthly → analysis 節奏
│   ├── operating_manual.md      # 營運手冊
│   ├── ai_collaboration.md      # 帽子原則 + 不自我終審 + 誰拍板（D7 已瘦身）
│   ├── rankings.md              # 排行快照方法論（口徑分開、不硬湊）
│   ├── decisions.md             # 方向決策紀錄（D1–D30）
│   └── lessons.md               # 教訓簿（殭屍任務卡三例都在這）
└── .github/workflows/
    ├── ci.yml                # PR validate + smoke（3.9 + 3.12）+ ruff
    ├── flash-brief.yml       # ⚡ 速報：手機 dispatch、純機械抽取（D19）
    └── health.yml            # 週一、四 --strict 巡檢 + 死源 liveness，未過/死源自動開 issue
```

---

## 快速開始

```bash
pip install pyyaml

python scripts/generate_daily_brief.py   # 產今天的 brief 骨架
python scripts/repo_health.py            # 系統還活著嗎
```

修改任何東西之後的驗收三件套：

```bash
python scripts/validate_repo.py
python tests/test_smoke.py
python scripts/repo_health.py --consistency
```

---

## 設計理念

1. **資料與內容分離** — `data/` 是長期知識底層（複利資本），`reports/` 是封存快照，互不污染。
2. **人機協作** — 腳本負責確定性工作（骨架、排行追蹤、檔案管理），AI 負責語意整理與挑買建議，人（我）負責品味與買不買。
3. **格式即契約** — 所有產出走 `templates/`；改欄位必須同步 prompts / docs / 腳本。
4. **輕依賴、先輕後重** — 標準庫 + pyyaml；不在 repo 內接 LLM API（D5），AI 撰寫走對話 agent。
5. **反熵**（D7）— 新流程不得依賴人類定期手動勞動；**健康的終極指標是「產出有沒有持續發生」**（非 commit 比例——D16 後產出對話即焚、commit 比例量不到，2026-06-19 修正）。
6. **產出有沒有持續發生，比工程漂不漂亮重要。**

詳見 [docs/system_design.md](docs/system_design.md)；節奏見 [docs/flow_calendar.md](docs/flow_calendar.md)；決策見 [docs/decisions.md](docs/decisions.md)。

---

## Roadmap

- [x] 資料底層 + Rankings 模組（歐美 / 韓 / 日五榜；KREAM/MUSINSA Firecrawl 重開 D23、SNKRDUNK 日本球鞋板 D24、ZOZO 確認永久死界）
- [x] CI（validate + smoke）+ 週期健檢巡檢（自動開 issue）
- [x] RSS 收集事實層（RSS 源擴到 31、每源抓取 10 → 25；新增來源走 D18 門檻）
- [x] AI 撰寫走對話 agent（D5：不接 repo 內 LLM API；D16：0 排程 routine、全對話）
- [x] Self-Evolution Loop（repo_health Next Actions + lessons 硬化路徑 + 決策守衛）
- [x] 每日產線（時區 bug 已修）→ D16 改對話觸發、無排程；daily 斷更看門狗隨之移除（無檔可監控）
- [x] Daily brief 行動帳 + 密度規則；週挑 / 週趨勢深挖卡節奏
- [x] 重定位殘留總清（2026-06-11：內容生產視角標籤組移除、routine 任務卡去殭屍化、全自動產出改分支+PR）
- [x] 第一性原理瘦身（2026-06-11 D7：砍死迴圈 prompt、封存任務卡、手動月拉流程；立反熵原則）
- [x] 終審 ≠ merge（2026-06-12 D8）；挑買卡停產、推薦回歸 brief 內（2026-06-12 D9）
- [x] 配件全週期覆蓋（週挑第 5 區；daily / monthly 配件同等納入）；粉絲增長殘留二次深掃
- [x] ⚡ 速報層（D19，2026-06-16）：白名單硬源純機械抽取（零 LLM）、手機可 dispatch，補桌面深度 brief 手機看不到的缺口
- [x] 採用 Firecrawl keyless 對話端（D22–D24，2026-06-20/21）：封鎖源 roundup 挖 picks、重開韓國/日本量化榜（不進腳本）
- [x] 週挑「週一早安自動觸發 + 每日累積候選池 → 週一收斂」（D25/D26，2026-06-23）：解掉休眠 + 看門狗空叫
- [x] scan-manifest 編排（D27/D28，2026-06-23）：每日掃描固化成 `data/scan_units.yml` + 平行唯讀 reader subagent（角色分離 + 強制 schema + 防注入）；配額對齊既定 brief、密度地板防交白卷
- [ ] 推送通知（未拍板；傾向用既有據點，不加新平台）
- [ ] 更多非 RSS 來源（視需求，不硬刮反爬站）

完整演進見 [CHANGELOG.md](CHANGELOG.md)。
