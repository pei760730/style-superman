# Style Superman

> **個人男裝潮流情報 + 挑買決策系統**
> 每天把全球男性潮流訊號（日潮 / 韓潮 / 歐美）→ 收集 → 分類 → 主編判斷 → 收斂成「對我有用」的挑買判斷。

**這套系統服務的對象只有我自己**：一個追男裝潮流、會親手挑單品入手的玩家。
它**不是**內容生產 / 拍片管線，與 IG 漲粉 / 創作者經營**完全無關**——產出永遠不含「可拍選題」「content hooks」類東西（2026-06-05 拍板，守衛強制，見[防線](#防線怎麼防止系統跑偏)）。

**我唯一的工作是兩件事：讀，和買不買。** 系統其餘環節全自動（D8：驗證綠即自 merge，沒有任何一步等我點按鈕）。覺得哪天判斷錯了，跟 agent 講一句——反饋會記進 [docs/decisions.md](docs/decisions.md) / [docs/lessons.md](docs/lessons.md)，產線修正。

---

## 系統的一天（時間軸）

```txt
台北 05:00   GitHub Actions 產 brief 骨架 + 收 RSS signals（純腳本，不判讀）→ 直推 master
台北 07:30   雲端 routine「每日 brief 內容填寫」讀 signals → 濾噪音、歸類、主編判讀
             → 填入頭條 + 三地區區塊（日/韓/歐美）+ For Me → 開分支 PR → CI 綠 → 自 merge
我起床後     手機開 GitHub → reports/daily/ 點今天 → 先看最下面的 🎯 For Me（對我最相關的在紅單品）
             （或跟 agent 說「早安」，直接端上來）
```

**每週一**：說「早安」= daily + 週挑 Head-to-Toe 一起端上（5 區 × 3 樣，收斂上週 7 天情報；**對話觸發，不是排程**）。每週至少一張趨勢深挖卡（歐美優先，對話觸發）。
**每月初**：說一聲跑歐美 / 日本月報（**對話觸發**；日本線 2026-07 起）。Lyst Q2 出刊（7 月）時說一聲 ingest 進 rankings。
**每週一、四 09:00**：自動健檢巡檢——daily 斷更、格式跑偏會**自動開 `repo-health` issue**，所以 GitHub 通知出現它 = 系統出事了，其他時候不用管。

---

## 產出說明書（你會收到什麼、怎麼讀）

### 📅 Daily Brief — [reports/daily/](reports/daily/)（每天）

- **先看最下面 `🎯 對我最相關 For Me`**——**在紅單品情報**（D15，非買清單）：**單品｜是什麼｜在哪紅（歐美/日/韓）｜對我衣櫥的意義｜價格/型號（辨識用）**。目的是知道現在在紅什麼,不催買;真要入手再開口（走定番調研）。
- 往上是 3–5 條頭條（每條固定回答「是什麼 / 為什麼是現在 / 對我的意義」）+ **三個地區區塊：🇯🇵 日潮 6–10 條、🇰🇷 韓潮 4–8 條、🌍 歐美 6–10 條**（一行一則含日期/價格）+ 明日 watchlist。頭條＋區塊合計 20–30 條/日。
- **讀法慣例**：連續趨勢用增量寫法——同一件事第二天只寫新增事實，背景用「讀法見 YYYY-MM-DD brief」回連，所以看到回連別當漏寫，是防止每天重講一遍。
- 訊號弱的日子會誠實寫「今日訊號偏弱」，不硬湊。

### 🛍 週挑 Head-to-Toe — [reports/buy_shortlist/](reports/buy_shortlist/)（每週）

- 從頭到腳 **5 區（頭部 / 上身 / 下身 / 足部 / 配件）× 各 3 樣**，每樣含 buy_angle、預算帶、優先度、「為什麼是本週」、「風險 / 別買的情況」。
- 直接跳 **「🎯 如果本週只買一樣」**——15 樣裡風險最低 × 依據最硬的那個。
- 預算帶強制分佈（entry / mid / splurge 都要有），不會整張都是貴貨。

### 📊 月度熱度速報 — [reports/monthly/](reports/monthly/)（每月，歐美 `-eu` + 日本 `-jp`）

- 主榜固定**品牌 Top 5 + 單品 Top 5**（含配件），收尾是「🛒 本月挑買方向」2–3 條。
- **信心標示怎麼讀**：每條掛訊號層級——L1 硬數據（Lyst / StockX 榜）＞ L2 已確認事件（官方公告、發售）＞ L3 多源媒體共識 ＞ L4 弱訊號（只能當觀察）。**L4 撐不起「熱賣 / 爆紅」這種話**，看到「待查」就是真的查不到，不是偷懶。
- 日本線量化基準弱（ZOZO 不可自動收），信心刻意保守，是特性不是缺陷。

### 🔬 趨勢深挖卡 — [reports/analysis/](reports/analysis/)（每週至少一張，歐美優先）

- 把連續 2–4 週出現的最強跨源趨勢寫成長線資產：跨源查證 → 生命週期 → 全價位帶落地 → 挑買判斷。範本：washed denim 卡。一年累積 ≈50 張 = 自己的趨勢資料庫。

### 📈 想查什麼最紅（隨時）

`python scripts/track_rankings.py`（加 `--region kr|jp|us-eu` 過濾），或直接看 [data/rankings/](data/rankings/) 五榜快照（Lyst / StockX / Mercari / KREAM / MUSINSA，最新在上、可比對名次演化）。

---

## 自動化全貌（誰、什麼時候、跑什麼、怎麼提交）

| 執行者 | 時間 | 做什麼 | 提交方式 |
|---|---|---|---|
| GitHub Actions `daily-brief.yml` | 每天台北 05:00 | 產當日 brief **骨架** + `--with-rss` 收當日 RSS signals 落檔（純腳本、無 LLM，D5） | ⚠ 骨架 + signals **直推 master**（確定性產出） |
| 雲端 routine「每日 brief 內容填寫」 | 每天台北 07:30 | 讀 Actions 收的 signals → 填當日 brief（頭條 / 日韓歐美三區塊 / For Me）；已填則跳過 | **分支 + PR**，CI 綠自 merge（D8） |
| 對話 agent（**唯一的非排程入口**） | 需要時 | 深挖卡；**週挑**（週一說「早安」一起端）；**月報**（月初說一聲，歐美 / 日本，日本線 2026-07 起）；**Lyst Q2 ingest**（7 月榜出說一聲）；臨時任務 | **分支 + PR**，驗證綠即自 merge（D8） |
| GitHub Actions `health.yml` | 每週一、四台北 09:00 | `repo_health --strict` 巡檢（新鮮度 + 一致性 + 守衛 + 產出契約） | 未過 → 自動開 / 更新 `repo-health` issue |
| GitHub Actions `ci.yml` | 每個 PR | validate + smoke 測試 | 紅燈 = 不能 merge |

> **只有 daily 一支雲端 routine**（起床前要備好，值得排程）。週挑 / 月報 / Lyst Q2 一律**對話觸發**——低頻產物不開常駐 routine（省額度、合反熵 D7）。

**鐵則：除了 daily 骨架 + signals，所有產出一律走分支 + PR。** 直推 master 會繞過 CI 上的全部防線——這是殭屍任務卡第三例的教訓（[docs/lessons.md](docs/lessons.md)）。

**叫 agent 做事：** 守則在 [CLAUDE.md](CLAUDE.md)（開工先跑 `repo_health.py`）。例行產出與工程 PR 驗證綠即自 merge（D8）——我的終審是事後反饋，買不買的決策在現實世界，不在 git。

---

## 十四個拍板（系統為什麼長這樣）

完整背景與選項見 [docs/decisions.md](docs/decisions.md)，這裡是速覽：

| # | 拍板 | 一句話 |
|---|------|--------|
| D1 | 韓潮不開獨立月報 | daily 固定 KR 追蹤 + 月報 cross-market 小節；KR 訊號量達門檻才升級 |
| D2 | 月報主榜固定 Top 5 | 另列浮動觀察名單收早期訊號——主榜只收高信心 |
| D3 | 挑買 shortlist 取代選題池 | 個人挑買重定位（2026-06-05）的落地，內容生產視角全面移除 |
| D4 | 來源 tier 不批量改 | 重分級走資料 PR 逐筆說明，來源可信度是內容判斷 |
| D5 | repo 內不接 LLM API | AI 撰寫走對話 / 雲端 agent；腳本只做確定性工作、不管 API key |
| D6 | 審計四提案全否決 | 共用模組 / 設定外部化等「看起來專業」的工程一律不做，守衛防回流 |
| D7 | 第一性原理瘦身 | 砍死迴圈與手動勞動依賴；立反熵三原則（新流程不得依賴人類定期手動勞動） |
| D8 | 終審 ≠ merge | 例行產出驗證綠即自 merge；main 是系統記憶不是批准章，我的終審是事後反饋 |
| D9 | 挑買卡停產 | 推薦只寫在 brief For Me / 週挑，深度功課我自己做 |
| D10 | 可購性門檻 | 推薦位只推「隨時買得到」的定番款；限定聯名只當訊號、不當入手點 |
| D11 | 品牌雷達 | 「深挖 <關鍵字>」對話觸發，產 ≤10 大品牌雷達（分 tier + lane 相容度）；不排程 |
| D12 | 看到問題就修 | 工程修正不需事前請示、修的人負責到底；內容判斷仍留人類 |
| D13 | 歐美不拆每日兩區 | 歐洲男裝肥料不足，深度走每週深挖位；順手收 Drapers 當零售 intel |
| D14 | score_trends 停用 | 砍加權評分框架，趨勢挑選回歸主編判斷（評分從未真正驅動挑選） |

---

## 防線（怎麼防止系統跑偏）

1. **不虛構**：沒來源就標 `待查`；不編造名次、百分比、「爆紅」結論（[CLAUDE.md](CLAUDE.md) 核心假設）。
2. **決策守衛**（[data/decision_guards.yml](data/decision_guards.yml) + `repo_health.py`，ERROR / CI 擋）：「不可回頭」的拍板留下禁用識別字（清單見守衛檔本身），任何 PR 把它們寫回活文件直接紅燈——**排程 agent 拿舊任務卡產的東西進不了 master**。
3. **產出契約檢查**（WARN / 巡檢盯）：重定位（2026-06-05）之後產的 daily / monthly 必含現行段落（`🎯 對我最相關 For Me`／`🛒 本月挑買方向`）、不得含舊世界觀識別字；日期已過仍殘留 `{{…}}` 佔位 = 空轉殭屍 WARN。
4. **歷史快照不溯及**：`reports/` 是封存快照，產出後不回改；重定位前的舊報告掛豁免註記保留原樣，**不要**把它們改寫成新格式。
5. **教訓硬化路徑**：踩坑先記 [docs/lessons.md](docs/lessons.md)（soft note），反覆出現才硬化成檢查——不為單次事故加終身檢查。

---

## 目錄結構

```txt
style-superman/
├── README.md                 # 你現在看的這份
├── CHANGELOG.md              # 系統演進紀錄（能力層變更）
├── CLAUDE.md                 # agent 執行守則（定位鐵則 + Self-Evolution Loop）
├── requirements.txt          # Python 相依（標準庫 + pyyaml）
├── data/                     # 知識底層（長期維護，不是快照）
│   ├── sources.yml           # 情報來源 42 個（29 個可 RSS 自動收）
│   ├── trend_taxonomy.yml    # 趨勢分類體系（系統的「語言」）
│   ├── trend_history.yml     # 趨勢生命週期基準（炒作 vs 真趨勢；雷達 / 深挖 prompt 引用）
│   ├── brands.yml            # 追蹤品牌（含 contemporary lane 錨點）
│   ├── people.yml            # 追蹤人物
│   ├── decision_guards.yml   # 決策守衛：禁用識別字（CI 強制）
│   └── rankings/             # 量化排行快照（最新在上，可比對演化）
│       ├── lyst-index.yml    #   歐美：Lyst Index 季度
│       ├── stockx.yml        #   歐美：StockX 年度
│       ├── mercari-jp.yml    #   日本：Mercari 二手成交
│       ├── kream.yml         #   韓國：KREAM 轉售
│       └── musinsa.yml       #   韓國：MUSINSA 銷售榜
├── reports/                  # 封存快照（產出後不回改）
│   ├── daily/                # 每日 brief（YYYY-MM-DD.md）
│   ├── buy_shortlist/        # 週挑 Head-to-Toe（YYYY-Wnn.md）
│   ├── monthly/              # 月度熱度速報（YYYY-MM-eu.md 歐美；YYYY-MM-jp.md 日本，2026-07 起）
│   └── analysis/             # 趨勢深挖卡 + 主題分析（每週至少一張，歐美優先）
├── prompts/                  # AI 內容工作模板（與 templates 欄位互為契約）
├── templates/                # 產出物固定格式（格式即契約）
├── scripts/                  # 自動化腳本（用法見 scripts/README.md）
│   ├── generate_daily_brief.py          # brief 骨架（--with-rss 含收集）
│   ├── generate_weekly_buy_picks.py     # 週挑骨架
│   ├── generate_monthly_heat_report.py  # 月報骨架
│   ├── collect_raw_signals.py           # RSS → raw_signal_pack
│   ├── track_rankings.py                # 排行檢視 + 名次演化
│   ├── ingest_ranking_snapshot.py       # 安全加入排行快照
│   ├── validate_repo.py                 # 格式契約檢查（CI）
│   └── repo_health.py                   # 健檢：新鮮度 + 一致性 + 守衛 + 產出契約
├── tests/                    # smoke 測試（無需 pytest）
├── docs/
│   ├── system_design.md         # 架構設計
│   ├── style_strategy.md        # 情報支柱、調性與個人成功指標
│   ├── flow_calendar.md         # daily → weekly → monthly → analysis 節奏
│   ├── operating_manual.md      # 營運手冊
│   ├── ai_collaboration.md      # 帽子原則 + 不自我終審 + 誰拍板（D7 已瘦身）
│   ├── rankings.md              # 排行快照方法論（口徑分開、不硬湊）
│   ├── decisions.md             # 方向決策紀錄（D1–D14）
│   └── lessons.md               # 教訓簿（殭屍任務卡三例都在這）
└── .github/workflows/
    ├── ci.yml                # PR validate + smoke
    ├── daily-brief.yml       # 每日骨架 + 收 RSS signals（台北 05:00；日期以 Asia/Taipei 顯式計算）
    └── health.yml            # 週一、四 --strict 巡檢，未過自動開 issue
```

---

## 快速開始

```bash
pip install pyyaml

python scripts/generate_daily_brief.py   # 產今天的 brief 骨架
python scripts/track_rankings.py         # 看最紅品牌 / 單品排行
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
4. **輕依賴、先輕後重** — 標準庫 + pyyaml；不在 repo 內接 LLM API（D5），AI 撰寫走對話 / 雲端 agent。
5. **反熵**（D7）— 新流程不得依賴人類定期手動勞動；維護/產出比是系統健康的終極指標。
6. **產出有沒有持續發生，比工程漂不漂亮重要。**

詳見 [docs/system_design.md](docs/system_design.md)；節奏見 [docs/flow_calendar.md](docs/flow_calendar.md)；決策見 [docs/decisions.md](docs/decisions.md)。

---

## Roadmap

- [x] 資料底層 + Rankings 模組（歐美 / 日 / 韓五榜）
- [x] CI（validate + smoke）+ 週期健檢巡檢（自動開 issue）
- [x] RSS 收集事實層（17 → 25 → 28 源，三輪深挖）
- [x] AI 撰寫走排程雲端 agent（D5：不接 repo 內 LLM API）
- [x] Self-Evolution Loop（repo_health Next Actions + lessons 硬化路徑 + 決策守衛）
- [x] 每日產線實跑（時區 bug 已修；斷更有看門狗）
- [x] Daily brief 行動帳 + 密度規則；週挑 / 週趨勢深挖卡節奏
- [x] 重定位殘留總清（2026-06-11：內容生產視角標籤組移除、routine 任務卡去殭屍化、全自動產出改分支+PR）
- [x] 第一性原理瘦身（2026-06-11 D7：砍死迴圈 prompt、封存任務卡、手動月拉流程；立反熵原則）
- [x] 終審 ≠ merge（2026-06-12 D8）；挑買卡停產、推薦回歸 brief 內（2026-06-12 D9）
- [x] 配件全週期覆蓋（週挑第 5 區；daily / monthly 配件同等納入）；粉絲增長殘留二次深掃
- [ ] 推送通知（未拍板；傾向用既有據點，不加新平台）
- [ ] 更多非 RSS 來源（視需求，不硬刮反爬站）

完整演進見 [CHANGELOG.md](CHANGELOG.md)。
