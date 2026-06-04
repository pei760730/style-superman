# Raw Signal Pack — 中間格式契約（C3）

在接 RSS / API / LLM **之前**，先把「每天收集到的原始訊號」固定成一個穩定格式，
讓 `prompts/daily_trend_brief.md` 的 `RAW_SIGNALS` 每天吃到一樣的形狀，不會因來源不同而亂。

> 這是**契約**，不是內容判斷。一筆 raw signal = 一條「來源說了什麼」，**還沒**經過 Style Superman 的趨勢判斷。
> 判斷在 daily brief / trend card 那層做（見 `docs/content_strategy.md`、`prompts/`）。

## 格式（YAML，list of signals）

```yaml
signals:
  - source_id: ""          # 對應 data/sources.yml 的 id（如 hypebeast / fashionsnap）
    source_tier: 1          # 1=核心 2=常態 3=輔助（取自該來源 tier）
    region: jp|kr|us-eu|global
    url: ""
    title: ""
    published: "YYYY-MM-DD|待查"
    summary: ""             # 1–2 句，來源說了什麼（事實，非推論）
    signal_type: item|silhouette|color|material|style|brand|person|culture  # 對應 trend_taxonomy.yml categories
    credibility: high|medium|low   # 一手報導=high；轉述/公關稿=medium；推測/單一來源=low
```

## 欄位規則

| 欄位 | 規則 |
|------|------|
| `source_id` | 必須是 `data/sources.yml` 既有的 id；新來源先加進 sources.yml |
| `signal_type` | 必須是 `data/trend_taxonomy.yml` 的 category id |
| `summary` | 只寫**來源說了什麼**（事實）；不要在這層下「會紅 / 該追」的判斷 |
| `published` | 不確定就 `待查`，不要猜日期 |
| `credibility` | 公關稿要識別並降為 medium/low；但品牌動態本身仍是有效訊號 |

## 鐵則（見根目錄 `CLAUDE.md`「不虛構」）

- 一筆 signal 對應一個可查證的來源（有 `url`）。沒來源的「體感」不進 raw pack。
- **不在 raw 層編造熱度 / 排名 / 百分比**；那些要嘛來自 `data/rankings/`（硬數據），要嘛在 brief 層標成觀察。
- raw pack 是中間產物，**不入長期版控**（放 `/tmp` 或本地工作區即可）；入庫的是 brief / trend card / rankings。

## 怎麼被使用

```
收集（RSS / 人工 / 未來 API）
   → 每篇用 prompts/article_to_insight.md 榨成 signal
   → 彙整成本檔格式的 raw_signal_pack（RAW_SIGNALS）
   → 餵給 prompts/daily_trend_brief.md 產出 daily brief
```

> 註：目前收集仍為人工 / 半自動；本契約是為日後 `generate_daily_brief.py` 接真實來源預留的穩定介面（見 `docs/codex_execution_plan.md` C3）。
