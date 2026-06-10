# Prompt — 本週最值得買 Head-to-Toe（週挑）

> 用途：每週把過去 7 天的情報收斂成「從頭到腳 4 區 × 各 3 樣」的挑買榜。
> 輸出格式嚴格遵守 `templates/weekly_buy_picks_template.md`，產出存 `reports/buy_shortlist/YYYY-Wnn.md`。

## 你的輸入（按優先序）

1. **本週 daily briefs**（`reports/daily/` 過去 7 天）——「為什麼是本週」的主要依據
2. **排行快照**（`data/rankings/*.yml` 最新一筆）——長期需求 / 保值 / 熱度的硬數據
3. **品牌追蹤**（`data/brands.yml`）——擁有者的品味錨點（日系素材主義 lane 為 tier 1）
4. **主題分析**（`reports/analysis/`）——lane 級深度脈絡

## 挑選規則

- **每區恰好 3 樣**：頭部（帽 / 墨鏡 / 頭部配件）、上身（上衣 / 外套）、下身（褲 / 裙外免）、足部（鞋 / 靴）。
- **「為什麼是本週」是本產物的靈魂**：必須引用 ≥1 條可驗證來源（brief 日期＋訊號、rankings 快照 period、analysis 檔名）。
  只有長期數據而無本週訊號的單品，要明說「無本週新訊號，靠長期數據」——不要假裝有時效性。
- **不虛構**：價格 / 折扣 / 發售日沒查到就標 `待查`；單源訊號要標「單源待確認」。
- **區分事實與解讀**：來源講的是什麼、你推論的是什麼，分開寫。
- **預算帶要有分佈**：12 樣中 entry / mid / splurge 都要出現，不可全是 splurge（這是挑買榜，不是願望清單）。
- **「找出問題」視角**：每樣寫「風險 / 別買的情況」——炒作 vs 真趨勢、溢價陷阱、季節錯位（夏天買帽 T 要說等季末）、
  「趨勢到頂時買經典原版而不是溢價聯名版」這類反向判斷是加分項。
- **連續性**：與上週重複的單品原則上不重挑，除非訊號明顯升級（要寫明升級了什麼）。
- **「只買一樣」**：12 樣中挑風險最低 × 依據最硬的一樣，講清楚為什麼是它。

## buy_angle / 預算帶 / 優先度 詞彙表

- buy_angle：`staple` 基本款 ／ `upgrade` 升級替換 ／ `statement` 亮點 ／ `seasonal` 當季 ／ `experiment` 嘗試
- 預算帶：`entry` 入門 ／ `mid` 中段 ／ `splurge` 一次到位
- 優先度：`now` 現在買 ／ `this-season` 這季內 ／ `watch` 再觀察

## 產出流程

1. 跑 `python scripts/generate_weekly_buy_picks.py` 產骨架（自動帶週期、本週 briefs 清單、rankings 摘要）。
2. 依上述規則填 12 樣 + 只買一樣 + 一句話總結。
3. 跑 `python scripts/validate_repo.py` 自驗格式。
