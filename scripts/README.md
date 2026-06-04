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

### `validate_repo.py`
檢查 repo 的基本契約：YAML 必填欄位、排行 rank 是否重複、template 必要段落、report 命名與標題。建議每次 PR 前跑一次。

```bash
python scripts/validate_repo.py
python scripts/validate_repo.py --data
python scripts/validate_repo.py --templates
python scripts/validate_repo.py --reports
```

### `ingest_ranking_snapshot.py`
安全地把「一筆新排行快照」加進 `data/rankings/<source>.yml`。預設 **dry-run**（只檢查不寫檔），確認契約都對再加 `--write`。寫入用文字插入，**保留既有快照的註解與排版**。

```bash
# 檢查（不寫檔）—— 預設
python scripts/ingest_ranking_snapshot.py --source lyst --input /tmp/lyst_q2.yml
cat /tmp/lyst_q2.yml | python scripts/ingest_ranking_snapshot.py --source lyst   # 或 stdin

# 通過檢查後真正寫入（放到 snapshots 最上方）
python scripts/ingest_ranking_snapshot.py --source lyst --input /tmp/lyst_q2.yml --write
```

檢查項：period 必填且不可與既有重複；Lyst rank 不重複/為整數；StockX 不可壓成單一 `ranking`；Mercari 必含 `brand_top` / `menswear_read`。輸入格式見 [templates/ranking_snapshot_template.md](../templates/ranking_snapshot_template.md)，範例見 `tests/fixtures/*_snapshot.yml`。

### `track_rankings.py`
讀取 `data/rankings/` 的排行快照（Lyst Index / StockX / Mercari），顯示最新榜並比對名次演化。模組說明見 [docs/rankings.md](../docs/rankings.md)。

```bash
python scripts/track_rankings.py                    # 全部（歐美 + 日本）
python scripts/track_rankings.py --region jp         # 只看日本（Mercari）
python scripts/track_rankings.py --region us-eu      # 只看歐美（Lyst + StockX）
python scripts/track_rankings.py --source lyst       # 單一來源：lyst/stockx/mercari
python scripts/track_rankings.py --source lyst --compare   # 比對最新兩季名次
python scripts/track_rankings.py --json              # 輸出 JSON
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
