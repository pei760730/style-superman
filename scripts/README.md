# scripts/

Style Superman 的自動化腳本。目前皆為純 Python（標準庫 + `pyyaml`），不需重型相依。

## 安裝

```bash
pip install pyyaml
```

## 腳本一覽

### `generate_daily_brief.py`
產出當日 Daily Brief 的骨架草稿，寫到 `reports/daily/YYYY-MM-DD.md`。

```bash
python scripts/generate_daily_brief.py                 # 今天
python scripts/generate_daily_brief.py --date 2026-06-04
python scripts/generate_daily_brief.py --draft         # 產 *.draft.md（不入版控）
```

它只負責「填日期 + 套模板 + 來源摘要」，實際趨勢內容由 AI（`prompts/daily_trend_brief.md`）或人工補上。

### `score_trends.py`
對趨勢清單做加權評分與排序。權重與分級門檻見 [docs/trend_scoring_rules.md](../docs/trend_scoring_rules.md)。

```bash
python scripts/score_trends.py --demo                  # 用內建範例驗證
python scripts/score_trends.py --input trends.json     # 讀外部清單
python scripts/score_trends.py --demo --json           # 輸出 JSON
```

輸入 JSON 格式：

```json
[
  {"name": "barrel jeans", "heat": 4, "growth": 5,
   "longevity": 3, "content_potential": 4, "accessibility": 3}
]
```

## 日常流程（手動版）

```bash
# 1. 產出今天的骨架
python scripts/generate_daily_brief.py

# 2. 收集訊號 → 用 prompts/ 讓 AI 整理 → 填進 brief
# 3. 把候選趨勢整理成 trends.json
# 4. 評分排序，決定主打哪幾個
python scripts/score_trends.py --input trends.json
```

## 後續規劃
- 接 RSS / API 自動收集（`sources.yml` 的 `rss` 欄位已預留）
- 接 LLM 自動撰寫 brief 全文
- 接推送（Telegram / Notion / Sheets）

詳見 [docs/operating_manual.md](../docs/operating_manual.md)。
