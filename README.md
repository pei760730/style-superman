# Style Superman

> **個人男裝潮流情報 + 挑買決策系統**
> 每天把全球男性潮流訊號（日潮 / 韓潮 / 歐美）→ 收集 → 分類 → 評分 → 收斂成「對我有用」的挑買判斷。

**這套系統服務的對象只有我自己**：一個追男裝潮流、會親手挑單品入手的玩家。
它**不是**內容生產 / 拍片管線，與 IG 漲粉 / 創作者經營**完全無關**——產出永遠不含「可拍選題」「content hooks」類東西（2026-06-05 拍板，守衛強制，見[防線](#防線怎麼防止系統跑偏)）。

---

## 每天怎麼用（擁有者手冊）

**每天早上（07:00 後，手機看 GitHub 就行）：**

1. 開 [reports/daily/](reports/daily/) 點今天的日期。
2. **先看最下面的 `🛒 對我有用 For Me`**——行動帳格式：單品｜價格｜通路（可點）｜時點｜下一步。
3. 「值得入手」的完整判斷（怎麼搭 / 風險 / 別買的情況）在 [reports/buy_picks/](reports/buy_picks/) 的當日挑買卡。
4. 有空再往上讀 4 條頭條（每條都有「對我的意義」）和快訊。

**每週：**

- [reports/buy_shortlist/](reports/buy_shortlist/) 的週挑（`YYYY-Wnn.md`）——從頭到腳 4 區 × 3 樣 +「如果本週只買一樣」。
- [reports/analysis/](reports/analysis/) 每週至少一張趨勢深挖卡（歐美優先；跨源查證 → 生命週期 → 全價位帶 → 挑買判斷，範本：washed denim 卡）。

**每月：** [reports/monthly/](reports/monthly/) 的熱度速報 +「本月挑買方向」——歐美（`-eu.md`）＋日本（`-jp.md`，2026-07 起）。

**想查什麼最紅：** `python scripts/track_rankings.py`（加 `--region kr|jp|us-eu` 過濾），或直接看 [data/rankings/](data/rankings/) 快照。

**懷疑系統死了：** `python scripts/repo_health.py`——一切綠就沒事；daily 斷更 / 契約跑偏會被週一、四的自動巡檢抓到並**自動開 issue**，所以 GitHub 通知出現 `repo-health` issue = 要處理。

**叫 agent 做事：** 守則在 [CLAUDE.md](CLAUDE.md)（開工先跑 `repo_health.py`）。brief 內容與挑買判斷的 PR 一律留我終審；工程 PR 看 CI 綠再 merge。

---

## 自動化全貌（誰、什麼時候、跑什麼、怎麼提交）

| 執行者 | 時間 | 做什麼 | 提交方式 |
|---|---|---|---|
| GitHub Actions `daily-brief.yml` | 每天台北 07:00 | 產當日 brief **骨架**（填模板 + RSS 28 源收集；無 LLM，決策 D5） | ⚠ 骨架**直推 master**（純腳本、確定性產出） |
| 對話 / 排程 agent（內容填寫） | 骨架產出後 | 填 brief 趨勢內容、開挑買卡、週挑、深挖卡 | **分支 + PR**，內容判斷留我終審 |
| 雲端 routine「歐美月度熱度速報」 | 每月 1 號 | 產當月歐美速報（含本月挑買方向） | **分支 + PR**（2026-06-11 起，原直推已改） |
| 雲端 routine「日本月度熱度速報」 | 每月 1 號 | 產當月日本速報（2026-07 首跑；量化基準 Mercari，信心保守） | **分支 + PR** |
| 雲端 routine「Lyst Q2 watcher」 | 7 月每週一 | Lyst Index Q2 出刊就 ingest 進 rankings | **分支 + PR**（同上） |
| GitHub Actions `health.yml` | 每週一、四台北 09:00 | `repo_health --strict` 巡檢（新鮮度 + 一致性 + 守衛 + 產出契約） | 未過 → 自動開 / 更新 `repo-health` issue |
| GitHub Actions `ci.yml` | 每個 PR | validate + smoke 測試 | 紅燈 = 不能 merge |

**鐵則：除了 daily 骨架，所有自動產出一律走分支 + PR。** 直推 master 會繞過 CI 上的全部防線——這是殭屍任務卡第三例的教訓（[docs/lessons.md](docs/lessons.md)）。

---

## 防線（怎麼防止系統跑偏）

1. **不虛構**：沒來源就標 `待查`；不編造名次、百分比、「爆紅」結論（[CLAUDE.md](CLAUDE.md) 核心假設）。
2. **決策守衛**（[data/decision_guards.yml](data/decision_guards.yml) + `repo_health.py`，ERROR / CI 擋）：「不可回頭」的拍板留下禁用識別字（清單見守衛檔本身），任何 PR 把它們寫回活文件直接紅燈——**排程 agent 拿舊任務卡產的東西進不了 master**。
3. **產出契約檢查**（WARN / 巡檢盯）：重定位（2026-06-05）之後產的 daily / monthly 必含現行段落（`🛒 對我有用 For Me`／`🛒 本月挑買方向`）、不得含舊世界觀識別字；日期已過仍殘留 `{{…}}` 佔位 = 空轉殭屍 WARN。
4. **歷史快照不溯及**：`reports/` 是封存快照，產出後不回改；重定位前的舊報告掛豁免註記保留原樣，**不要**把它們改寫成新格式。
5. **教訓硬化路徑**：踩坑先記 [docs/lessons.md](docs/lessons.md)（soft note），反覆出現才硬化成檢查——不為單次事故加終身檢查。

---

## 系統管線

| 階段 | 能力 | 產出 |
|------|------|------|
| 1. 收集 | RSS 28 源自動收集（42 來源清單，含不可自動收的榜單站） | raw_signal_pack（事實層） |
| 2. 分類 | 依 taxonomy 歸類（單品 / 輪廓 / 配色 / 品牌 / 人物 / 文化） | 結構化 trend cards |
| 3. 評分 | 熱度 / 成長性 / **可駕馭度 wearability** 打分 | 排序後的 trend 清單 |
| 4. 簡報 | 轉成可閱讀的 Daily Brief（行動帳收尾） | `reports/daily/YYYY-MM-DD.md` |
| 5. 挑買 | 轉成「該不該買 / 怎麼搭 / 在哪買 / 別買的情況」 | 挑買卡 / 週挑 / 深挖卡 |
| 6. 累積 | 長期沉澱：季度榜快照可比對名次演化 | `data/` + `reports/` 歷史 |

---

## 目錄結構

```txt
style-superman/
├── README.md                 # 你現在看的這份
├── CHANGELOG.md              # 系統演進紀錄（能力層變更）
├── CLAUDE.md                 # agent 執行守則（定位鐵則 + Self-Evolution Loop）
├── requirements.txt          # Python 相依（標準庫 + pyyaml）
├── data/                     # 知識底層（長期維護，不是快照）
│   ├── sources.yml           # 情報來源 42 個（28 個可 RSS 自動收）
│   ├── trend_taxonomy.yml    # 趨勢分類體系（系統的「語言」）
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
│   ├── buy_picks/            # 單品挑買卡（YYYY-MM-DD-<slug>.md，daily「值得入手」同日觸發）
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
│   ├── score_trends.py                  # 趨勢評分
│   ├── track_rankings.py                # 排行檢視 + 名次演化
│   ├── ingest_ranking_snapshot.py       # 安全加入排行快照
│   ├── validate_repo.py                 # 格式契約檢查（CI）
│   └── repo_health.py                   # 健檢：新鮮度 + 一致性 + 守衛 + 產出契約
├── tests/                    # smoke 測試（無需 pytest）
├── docs/
│   ├── system_design.md         # 架構設計
│   ├── content_strategy.md      # 情報支柱與個人成功指標（檔名沿用，定位已是個人挑買）
│   ├── content_calendar.md      # daily → weekly → monthly → analysis 節奏
│   ├── trend_scoring_rules.md   # 評分規則（wearability 等維度）
│   ├── operating_manual.md      # 營運手冊
│   ├── ai_collaboration.md      # 帽子原則 + 不自我終審 + 誰拍板（D7 已瘦身）
│   ├── rankings.md              # 排行快照方法論（口徑分開、不硬湊）
│   ├── decisions.md             # 方向決策紀錄（D1–D7）
│   └── lessons.md               # 教訓簿（殭屍任務卡三例都在這）
└── .github/workflows/
    ├── ci.yml                # PR validate + smoke
    ├── daily-brief.yml       # 每日骨架（台北 07:00；日期以 Asia/Taipei 顯式計算）
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

1. **資料與內容分離** — `data/` 是長期知識底層，`reports/` 是封存快照，互不污染。
2. **人機協作** — 腳本負責確定性工作（骨架、評分、檔案管理），AI 負責語意整理與挑買建議，人（我）負責品味與買不買。
3. **格式即契約** — 所有產出走 `templates/`；改欄位必須同步 prompts / docs / 腳本。
4. **輕依賴、先輕後重** — 標準庫 + pyyaml；不在 repo 內接 LLM API（D5），AI 撰寫走對話 / 雲端 agent。
5. **產出有沒有持續發生，比工程漂不漂亮重要。**

詳見 [docs/system_design.md](docs/system_design.md)；節奏見 [docs/content_calendar.md](docs/content_calendar.md)；決策見 [docs/decisions.md](docs/decisions.md)。

---

## Roadmap

- [x] 資料底層 + 評分規則 + Rankings 模組（歐美 / 日 / 韓五榜）
- [x] CI（validate + smoke）+ 週期健檢巡檢（自動開 issue）
- [x] RSS 收集事實層（17 → 25 → 28 源，三輪深挖）
- [x] AI 撰寫走排程雲端 agent（D5：不接 repo 內 LLM API）
- [x] Self-Evolution Loop（repo_health Next Actions + lessons 硬化路徑 + 決策守衛）
- [x] 每日產線實跑（時區 bug 已修；斷更有看門狗）
- [x] Daily brief 行動帳 + 密度規則；挑買卡 / 週挑 / 週趨勢深挖卡節奏
- [x] 重定位殘留總清（2026-06-11：內容生產視角標籤組移除、routine 任務卡去殭屍化、全自動產出改分支+PR）
- [x] 第一性原理瘦身（2026-06-11 D7：砍死迴圈 prompt、封存任務卡、手動月拉流程；立反熵原則）
- [ ] 推送通知（未拍板；傾向用既有據點，不加新平台）
- [ ] 更多非 RSS 來源（視需求，不硬刮反爬站）

完整演進見 [CHANGELOG.md](CHANGELOG.md)。
