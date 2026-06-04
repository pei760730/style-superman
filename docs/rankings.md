# Rankings Module — Style Superman

定期、可量化的「最紅品牌 / 熱銷單品」排行模組。把分散的權威榜收斂成**可長期比對**的結構化資料。

## 為什麼要這個

Daily Brief 是「敘述性」的趨勢觀察；Rankings 是「量化性」的硬數據。兩者互補：
- Brief 告訴你「學院風很紅」；Rankings 告訴你「Ralph Lauren 排第 6、升了還是降了」。
- 累積多期後能回答最重要的問題：**誰在升、誰在退、我們當初看準了沒。**

## 來源（都免費）

### 🇺🇸🇪🇺 歐美
| 來源 | 給什麼 | 頻率 | 性質 / 限制 |
|------|--------|:----:|------------|
| **Lyst Index** | 最紅品牌 Top 20 + 最熱單品 Top 10 | 季度 | 權威但**全性別、偏精品**（女裝權重高）→ 男裝需過濾 |
| **StockX** | 最暢銷球鞋/服飾/配件、成長最快品牌 | 年度 + 年中 | 轉售**實數**，**偏球鞋/街頭**（男裝代表性最強）；涵蓋不到精品成衣 |

Lyst 補精品/設計師視角，StockX 補街頭/球鞋實銷，兩者互補。

### 🇯🇵 日本
日本**沒有單一威望榜**，靠「EC 即時銷售榜」+「二手成交需求」兩條腿：

| 來源 | 給什麼 | 頻率 | 性質 / 限制 |
|------|--------|:----:|------------|
| **ZOZOTOWN** | 男裝即時銷售榜（可分類） | 即時/日 | 大眾走量，抓不到尖端日潮；⚠ JS 動態頁，自動抓取需 headless |
| **Mercari** | 二手成交品牌榜 = 需求黏性 | 報告不定期 | 日本版 StockX，更廣、非球鞋導向 |

> ⚠ **日本鐵則**：EC/二手榜只反映**大眾脈動**（Uniqlo/Nike/連帽T）。尖端日潮（visvim/Kapital/設計師）
> 在**媒體與街拍**（`sources.yml` region: jp 的 media：Fashionsnap / MEN'S NON-NO / Houyhnhnm / POPEYE）。
> 追日潮必須**量化榜 + 媒體街拍兩條腿一起看**，落差比西方大。

## 檔案結構

```txt
data/rankings/
├── lyst-index.yml     # 歐美：季度，最新放最上
├── stockx.yml         # 歐美：年度/年中
├── zozotown.yml       # 日本：EC 即時銷售（觀察/採集）
└── mercari-jp.yml     # 日本：二手成交需求
templates/ranking_snapshot_template.md   # 新增一期時複製的格式
prompts/ranking_ingest.md                # 用 AI 把新報告轉成 YAML
scripts/track_rankings.py                # 檢視最新榜 + 比對名次演化
```

## 日常操作

### 看現在的榜
```bash
python scripts/track_rankings.py                 # 全部（歐美 + 日本）
python scripts/track_rankings.py --region jp      # 只看日本（ZOZO + Mercari）
python scripts/track_rankings.py --region us-eu   # 只看歐美（Lyst + StockX）
python scripts/track_rankings.py --source lyst    # 單一來源（lyst/stockx/zozo/mercari）
```

### 新一期發布時（季度 / 年度）
1. 用 `prompts/ranking_ingest.md` 把報告轉成 YAML（或手動照 `templates/ranking_snapshot_template.md` 填）。
2. 貼到對應 `.yml` 的 `snapshots:` **最上面**（最新在前）。
3. 跑 `python scripts/track_rankings.py --source <lyst|stockx>` 自驗格式。

### 比對演化（累積 2 期以上才有意義）
```bash
python scripts/track_rankings.py --source lyst --compare
```
會用我們自己的歷史算出每個品牌名次的 ↑ / ↓ / 新進 / 掉榜，而非只看來源標示。

## 與評分系統的關係

Rankings 是 `score_trends.py` 的**外部佐證輸入**：一個趨勢若同時出現在 Lyst 上升品牌或 StockX 熱銷榜，它的 `heat` / `growth` 分就有客觀依據，而非純主觀判斷。

## 目前資料

| 來源 | 已記錄 |
|------|--------|
| Lyst Index | 2026-Q1（Chanel 首度登頂；SL 立領外套單品 #1，MoM +5,550%）|
| StockX | 2025 全年（ASICS Gel-1130 最暢銷；跑鞋品牌全面起飛）|
| ZOZOTOWN | 2026-06 觀察（oversized + logo + 機能布；⚠ 非官方逐位排名）|
| Mercari | 2013→2022（成交 #1 Chanel→Uniqlo）|

下一期：Lyst Q2 2026（已設排程）、StockX 2026 年中、ZOZO 待 headless 抓取做逐位榜。

## ⚠ 待補：ZOZO 逐位排名

ZOZO 排行頁是 JS 動態渲染，WebFetch 抓不到逐位名次（會逾時）。目前 `zozotown.yml`
記的是「觀察到的熱賣單品」（`method: search-observed`），不是官方 1–N 榜。
要做真正的逐位排名，需 headless browser（Playwright/Puppeteer）抓取，屆時把 `method`
改為 `official-ranking` 並為每個 item 加 `rank` 欄（`track_rankings.py` 已支援這格式，會自動顯示名次）。

## 誠實標註

- 數字一律照原始報告，沒確認的留空/標「待查」，不編造（見根目錄 `CLAUDE.md`）。
- 口徑差異要標清楚：全站 vs 品牌內、MoM vs YoY、需求 vs 搜尋。
- Lyst 偏女裝/精品，別把它的單品榜直接當男裝榜——看 `menswear_focus` 欄與 StockX 交叉驗證。
