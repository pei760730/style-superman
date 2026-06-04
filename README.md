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
├── .gitignore
├── data/                     # 系統的「知識底層」（人工 + 機器共同維護）
│   ├── sources.yml           # 情報來源清單（站點 / 帳號 / RSS / 排行）
│   ├── trend_taxonomy.yml    # 趨勢分類體系
│   ├── brands.yml            # 追蹤中的男裝品牌
│   ├── people.yml            # 追蹤中的關鍵人物
│   └── rankings/             # 定期可量化排行快照（可長期比對）
│       ├── lyst-index.yml    #   歐美：Lyst Index 季度（最紅品牌+單品）
│       ├── stockx.yml        #   歐美：StockX 年度/年中（熱銷實數）
│       ├── zozotown.yml      #   日本：ZOZOTOWN EC 即時銷售
│       └── mercari-jp.yml    #   日本：Mercari 二手成交需求
├── reports/
│   └── daily/                # 每日 brief 產出（按日期命名）
├── prompts/                  # 餵給 AI 的提示詞模板
│   ├── daily_trend_brief.md
│   ├── trend_analysis.md
│   ├── article_to_insight.md
│   └── short_video_ideas.md
├── scripts/                  # 自動化腳本
│   ├── generate_daily_brief.py
│   ├── score_trends.py
│   ├── track_rankings.py     # 排行快照檢視 + 名次演化比對
│   └── README.md
├── templates/                # 產出物的固定格式
│   ├── daily_brief_template.md
│   ├── trend_card_template.md
│   └── short_video_idea_template.md
├── docs/                     # 系統設計與營運手冊
│   ├── system_design.md
│   ├── content_strategy.md
│   ├── trend_scoring_rules.md
│   └── operating_manual.md
└── .github/
    └── workflows/
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

# 4. 看最紅品牌 / 熱銷單品排行（Lyst Index + StockX）
python scripts/track_rankings.py
```

每日的成品會落在 [reports/daily/](reports/daily/)，命名為 `YYYY-MM-DD.md`。

---

## 設計理念

1. **資料與內容分離** — `data/` 是長期知識底層，`reports/` 是每日快照，互不污染。
2. **人機協作** — 腳本負責骨架與評分，AI（透過 `prompts/`）負責語意整理與選題，人負責拍板。
3. **格式即契約** — 所有產出都走 `templates/`，方便日後被 n8n / Notion / Sheets 解析。
4. **先輕後重** — 先把流程跑順、累積資料，再決定要不要上重型自動化。

詳見 [docs/system_design.md](docs/system_design.md)。

---

## Roadmap

- [x] Repo 結構與資料底層
- [x] Daily brief 骨架腳本
- [x] 趨勢評分規則
- [x] Rankings 模組（Lyst Index + StockX，可長期比對）
- [ ] 接入真實來源抓取（RSS / API）
- [ ] AI 自動撰寫 brief 全文
- [ ] 推送到 Telegram / Notion
- [ ] 短影音選題自動排程

完整演進見 [CHANGELOG.md](CHANGELOG.md)。
