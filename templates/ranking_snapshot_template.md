# Ranking Snapshot Template

每當 Lyst / StockX 發布新一期，**複製對應的 YAML 區塊、填入新資料、貼到該檔 `snapshots:` 最上面**（最新放最上）。
之後跑 `python scripts/track_rankings.py --compare` 就能看出名次演化。

---

## Lyst Index（季度）→ 貼到 `data/rankings/lyst-index.yml`

```yaml
  - period: "YYYY-Qn"          # 例 2026-Q2
    published: "YYYY-MM"
    methodology: "如有改版才填"
    notes: >
      本季重點：誰登頂、誰暴漲、哪個單品 MoM 飆升、有無聯名/事件驅動。
    brands:                    # Top 20，move = 相對上季：new / re-entry / +N / -N / =
      - { rank: 1,  name: "",  move: new }
      # … 到 rank 20
    products:                  # Top 10
      - { rank: 1, brand: "", item: "", note: "如有 % 變化填這" }
      # … 到 rank 10
    menswear_focus:            # 手動標：本季與男裝相關的訊號
      - ""
```

## StockX（年度 / 年中）→ 貼到 `data/rankings/stockx.yml`

```yaml
  - period: "YYYY-annual"      # 或 YYYY-midyear
    published: "YYYY-Qn"
    report: "Big Facts YYYY"   # 或 Current Culture Index
    best_seller_sneaker: { brand: "", item: "", note: "" }
    apparel_top:         { brand: "", item: "", note: "" }
    accessory_top:       { brand: "", item: "", note: "" }
    all_time_best_seller:{ brand: "", item: "", note: "" }
    notable_new_models:        # 各品牌年度最佳新款（品牌口徑）
      - { brand: "", item: "", note: "" }
    fastest_growing_brands:    # YoY
      - { brand: "", change: "+N%" }
    menswear_focus:
      - ""
```

---

### 填寫紀律
- **只填有來源的數字**，沒確認的名次/百分比留空或標 `（待查）`，不要編（見 docs/operating_manual 與根目錄 CLAUDE.md「不虛構」）。
- StockX 報告混用「全站最暢銷」與「各品牌最佳新款」兩種口徑——**分欄記錄，不要硬湊成一條 1–10 排名**。
- 填完跑 `python scripts/track_rankings.py --source <lyst|stockx>` 自驗格式無誤。
