# Style Superman

> **Men's Fashion & Culture Intelligence System**
> 男性潮流 / 穿搭 / 文化趨勢的每日情報中樞

這不是一個普通的筆記倉庫，而是一套「每天自動把全球男性潮流訊號 → 整理 → 分類 → 評分 → 轉成可用內容」的情報系統。

---

## 這套系統在做什麼

| 階段 | 能力 | 產出 |
|------|------|------|
| 1. 收集 | 每日抓取潮流訊號（日潮 / 韓潮 / 歐美） | 原始來源清單 |
| 2. 分類 | 依 taxonomy 把訊號歸類（單品 / 輪廓 / 配色 / 品牌 / 人物） | 結構化 trend cards |
| 3. 評分 | 用熱度 / 成長性 / 內容潛力打分 | 排序後的 trend 清單 |
| 4. 簡報 | 轉成可閱讀的 Daily Brief | `reports/daily/YYYY-MM-DD.md` |
| 5. 選題 | 轉成短影音 / 社群貼文選題 | 內容點子卡 |
| 6. 累積 | 長期沉澱成趨勢資料庫 | `data/` + `reports/` 歷史 |
| 7. 串接 | 未來接 AI / RSS / n8n / Telegram / Notion / Sheets | 自動化管線 |

---

## 目錄結構

```txt
style-superman/
├── README.md                 # 你現在看的這份
├── CHANGELOG.md              # 版本與系統演進紀錄
├── CLAUDE.md                 # Claude Code 在本 repo 的執行守則
├── requirements.txt           # Python 相依套件
├── .gitignore
├── data/                     # 系統的「知識底層」（人工 + 機器共同維護）
│   ├── sources.yml           # 情報來源清單（站點 / 帳號 / RSS / 排行）
│   ├── trend_taxonomy.yml    # 趨勢分類體系
│   ├── brands.yml            # 追蹤中的男裝品牌
│   ├── people.yml            # 追蹤中的關鍵人物
│   └── rankings/             # 定期可量化排行快照（可長期比對）
│       ├── lyst-index.yml    #   歐美：Lyst Index 季度（最紅品牌+單品）
│       ├── stockx.yml        #   歐美：StockX 年度/年中（熱銷實數）
│       ├── mercari-jp.yml    #   日本：Mercari 二手成交需求
│       ├── kream.yml         #   韓國：KREAM 限量/轉售成交量（韓版 StockX）
│       └── musinsa.yml       #   韓國：MUSINSA 平台銷售榜（最大男裝電商）
├── reports/
│   ├── daily/                # 每日 brief 產出（按日期命名）
│   ├── monthly/              # 月度熱度速報（歐美，YYYY-MM-eu.md），排程自動生成
│   ├── content_ideas/        # 每月選題池（YYYY-MM.md；候選→已排→已拍→發布）
│   └── analysis/             # 主題分析（如跨市場交集），可累積回看
├── prompts/                  # 餵給 AI 的提示詞模板
│   ├── daily_trend_brief.md
│   ├── trend_analysis.md
│   ├── article_to_insight.md
│   ├── short_video_ideas.md
│   ├── ranking_ingest.md
│   └── monthly_heat_report.md
├── scripts/                  # 自動化腳本
│   ├── generate_daily_brief.py          # 支援 --with-rss 收集 raw_signal_pack
│   ├── generate_monthly_heat_report.py  # 月度歐美速報骨架
│   ├── collect_raw_signals.py           # RSS → raw_signal_pack（事實層）
│   ├── score_trends.py
│   ├── track_rankings.py     # 排行快照檢視 + 名次演化比對
│   ├── ingest_ranking_snapshot.py  # 安全加入排行快照（dry-run + 寫入）
│   ├── validate_repo.py      # PR 前 smoke validation（格式契約）
│   ├── repo_health.py        # 自我健康檢查（產線新鮮度 + 文件↔程式碼漂移 + Next Actions）
│   └── README.md
├── tests/                    # 最小驗收
│   ├── test_smoke.py         #   核心腳本 smoke（9 項，無需 pytest）
│   └── fixtures/             #   ingest 快照 + RSS feed 合成測試範例
├── templates/                # 產出物的固定格式
│   ├── daily_brief_template.md
│   ├── trend_card_template.md
│   ├── short_video_idea_template.md
│   ├── ranking_snapshot_template.md
│   ├── monthly_heat_report_template.md
│   └── raw_signal_pack_template.md  # RAW_SIGNALS 中間格式契約
├── docs/                     # 系統設計與營運手冊
│   ├── system_design.md
│   ├── content_strategy.md
│   ├── content_calendar.md      # Daily → weekly → monthly → analysis 內容生產線
│   ├── trend_scoring_rules.md
│   ├── operating_manual.md
│   ├── ai_collaboration.md      # 主編 / 工程 / 人類角色手冊（model-agnostic）
│   ├── codex_execution_plan.md  # 第一輪工程任務卡（已封存，C1–C6 完成）
│   ├── decisions.md             # 主編決策紀錄（D1–D5 已拍板）
│   └── lessons.md               # 教訓簿（soft note → 反覆出現 → 硬化成檢查）
└── .github/
    └── workflows/
        ├── ci.yml            # PR smoke checks
        └── daily-brief.yml   # 每日自動跑 brief 的排程
```

---

## 快速開始

```bash
# 1. 安裝相依套件（目前只用標準庫 + pyyaml）
pip install pyyaml

# 2. 產出今天的 daily brief（草稿骨架）
python scripts/generate_daily_brief.py

# 3. 對趨勢資料打分
python scripts/score_trends.py

# 4. 看最紅品牌 / 熱銷單品排行（歐美 Lyst+StockX／日本 Mercari／韓國 KREAM+MUSINSA）
python scripts/track_rankings.py
```

每日的成品會落在 [reports/daily/](reports/daily/)，命名為 `YYYY-MM-DD.md`。

---

## 設計理念

1. **資料與內容分離** — `data/` 是長期知識底層，`reports/` 是每日快照，互不污染。
2. **人機協作** — 腳本負責骨架與評分，AI（透過 `prompts/`）負責語意整理與選題，人負責拍板。
3. **格式即契約** — 所有產出都走 `templates/`，方便日後被 n8n / Notion / Sheets 解析。
4. **先輕後重** — 先把流程跑順、累積資料，再決定要不要上重型自動化。

詳見 [docs/system_design.md](docs/system_design.md)。內容策略見 [docs/content_strategy.md](docs/content_strategy.md)，Daily → weekly → monthly → analysis 的生產線見 [docs/content_calendar.md](docs/content_calendar.md)。AI 分工與交接規則見 [docs/ai_collaboration.md](docs/ai_collaboration.md)；Codex 已拆好的下一步工程任務見 [docs/codex_execution_plan.md](docs/codex_execution_plan.md)，主編決策建議與待確認事項見 [docs/decisions.md](docs/decisions.md)。

---

## Roadmap

- [x] Repo 結構與資料底層
- [x] Daily brief 骨架腳本
- [x] 趨勢評分規則
- [x] Rankings 模組（歐美 Lyst+StockX／日本 Mercari／韓國 KREAM+MUSINSA，可長期比對）
- [x] Codex / Claude Code / 人類協作分工手冊
- [x] Codex 第一輪系統 review + Claude Code 工程任務卡
- [x] PR smoke validation + GitHub Actions CI
- [x] RSS 收集 → raw_signal_pack（事實層；C6）
- [x] AI 撰寫報告 — 已由排程雲端 agent 達成（不另接 repo 內 LLM API；見 docs/decisions.md D5）
- [x] Self-Evolution Loop — `repo_health.py`（自我檢查 + Next Actions）+ `docs/lessons.md`（教訓硬化路徑）+ `CLAUDE.md` agent 工作迴圈
- [ ] **讓每日產線真的跑起來**（目前最重要：daily brief 斷更會被 health check 警告）
- [ ]（視需求）接入更多來源抓取（非 RSS API / 爬蟲）
- [ ] 推送到 Telegram / Notion（未拍板）
- [ ] 短影音選題自動排程

完整演進見 [CHANGELOG.md](CHANGELOG.md)。
