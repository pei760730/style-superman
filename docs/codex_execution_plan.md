# Codex Execution Plan — Style Superman

> 這是 Codex 依 `docs/ai_collaboration.md` 實際跑完第一輪 repo review 後留下的執行計畫。目的不是再寫一份抽象分工，而是把「下一步該做什麼」拆成 Claude Code / 人類可以直接接手的任務卡。

## 0. 本輪 Codex 判斷

目前 repo 已經是一個可運作的 **男性潮流情報 MVP**：

- `data/` 已有來源、taxonomy、品牌、人物與排行快照。
- `scripts/` 已能產 daily brief 骨架、趨勢評分、檢視排行。
- `prompts/` + `templates/` 已形成內容契約。
- `reports/` 已有 daily、monthly、analysis 三種產物。

Codex 本輪不急著改腳本邏輯，優先做三件事：

1. **補齊工程交接面**：讓 Claude Code 有清楚的 repo 指令與任務卡。
2. **修正文件導覽落差**：README 要反映目前已存在的 monthly / ranking prompt 與 template。
3. **鎖定下一階段工程順序**：先 validation，再 ingestion，再 LLM / 推送；不要反過來先做重型自動化。

---

## 1. 內容契約現況

| 契約 | 位置 | 狀態 | Codex 決策 |
|------|------|------|------------|
| Daily Brief | `templates/daily_brief_template.md` + `prompts/daily_trend_brief.md` | 可用 | 保持 Markdown 結構穩定；工程只填骨架，主編判斷由 Codex / 人類做。 |
| Trend Card | `templates/trend_card_template.md` + `prompts/trend_analysis.md` | 可用 | 五維度分數必須附理由，仍是 `score_trends.py` 的核心輸入契約。 |
| Short Video Idea | `templates/short_video_idea_template.md` + `prompts/short_video_ideas.md` | 可用 | 只由 headline trends 轉出，不要把弱訊號硬轉成選題。 |
| Ranking Snapshot | `templates/ranking_snapshot_template.md` + `prompts/ranking_ingest.md` | 可用但需驗證器 | 下一步應由 Claude Code 補 schema validation，避免 YAML 手填出錯。 |
| Monthly Heat Report | `templates/monthly_heat_report_template.md` + `prompts/monthly_heat_report.md` | MVP | 月報是綜合判斷，不是官方榜；每條都要有來源與信心。 |

---

## 2. Claude Code 任務卡

以下任務按建議順序排列。每張卡都可以獨立開 PR，但不要同一個 PR 混太多方向。

### C1 — Repo validation CLI（已完成：`scripts/validate_repo.py`）

**Goal**  
新增一個 validation 入口，讓人工 / AI 修改 YAML、templates、reports 後可以快速檢查格式與基本契約。

**Scope**

- 可修改：`scripts/validate_repo.py`、`scripts/README.md`、必要的 `docs/` 說明。
- 不要修改：`data/` 的內容事實、既有 `reports/` 文字判斷。

**Contract**

- Command: `python scripts/validate_repo.py`
- Optional flags:
  - `--data`：只檢查 `data/*.yml` 與 `data/rankings/*.yml`
  - `--templates`：檢查模板檔是否存在必要 section / placeholder
  - `--reports`：檢查 reports 命名與基本標題
- Output:
  - 成功：列出檢查項與 `✅`
  - 失敗：列出檔案、欄位、問題原因，exit code `1`

**Minimum checks**

- `data/sources.yml` 每個 source 有 `id/name/type/region/tier/url` 或明確允許的空值。
- `data/brands.yml` 每個 brand 有 `id/name/region/segment/tier/watch`。
- `data/people.yml` 每個 person 有 `id/name/role/region/influence/watch`。
- `data/rankings/*.yml` 有 `source/snapshots`，且 snapshots 是 list。
- Lyst snapshot 的 `brands` rank 不重複；`products` rank 不重複。
- StockX snapshot 不被硬湊成單一 ranking list。
- Mercari snapshot 保留 `brand_top` / `menswear_read` 口徑。

**Acceptance checks**

```bash
python scripts/validate_repo.py
python scripts/validate_repo.py --data
python scripts/validate_repo.py --templates
```

### C2 — Ranking ingest helper

**Goal**  
降低更新 Lyst / StockX / Mercari 快照時的手填錯誤，把「AI 轉 YAML」後的資料先經過 dry-run 檢查。

**Scope**

- 可修改：`scripts/track_rankings.py` 或新增 `scripts/ingest_ranking_snapshot.py`、`scripts/README.md`、`docs/rankings.md`。
- 不要修改：現有 snapshots 的事實內容，除非 validation 發現純格式錯誤。

**Contract**

- Input: 一個 YAML 檔或 stdin，內容是新 snapshot block。
- Command example:

```bash
python scripts/ingest_ranking_snapshot.py --source lyst --input /tmp/lyst.yml --dry-run
```

- Dry-run 只印出會插入哪個檔案、period、rank count、可能問題；不寫檔。
- 真寫入需要 `--write`，並把新 snapshot 放到 `snapshots:` 最上方。

**Acceptance checks**

```bash
python scripts/ingest_ranking_snapshot.py --source lyst --input tests/fixtures/lyst_snapshot.yml --dry-run
python scripts/track_rankings.py --source lyst --compare
```

### C3 — Daily brief source pack format

**Goal**  
在接 RSS / LLM 前，先定義 `RAW_SIGNALS` 的穩定中間格式，避免 daily prompt 每天吃到不同形狀的資料。

**Scope**

- 可修改：新增 `templates/raw_signal_pack_template.md` 或 `docs/raw_signal_contract.md`、`prompts/article_to_insight.md`、`prompts/daily_trend_brief.md`。
- 不要修改：`reports/daily/` 已產出的歷史檔。

**Contract**

Raw signal 至少包含：

```yaml
- source_id: ""
  source_tier: 1
  region: jp|kr|us-eu|global
  url: ""
  title: ""
  published: "YYYY-MM-DD|待查"
  summary: ""
  signal_type: item|silhouette|color|material|style|brand|person|culture
  credibility: high|medium|low
```

**Acceptance checks**

```bash
python scripts/generate_daily_brief.py --date 2099-01-01 --draft
```

### C4 — Monthly heat report generator MVP

**Goal**  
把現有 `prompts/monthly_heat_report.md` 與 `templates/monthly_heat_report_template.md` 接成一個半自動骨架產生器，先不做全自動 web 判斷。

**Scope**

- 可修改：新增 `scripts/generate_monthly_heat_report.py`、`scripts/README.md`、`docs/operating_manual.md`。
- 不要修改：月報中的品牌 / 單品判斷；骨架可以留 `待填`。

**Contract**

- Command:

```bash
python scripts/generate_monthly_heat_report.py --month 2026-06 --region us-eu
```

- Output: `reports/monthly/YYYY-MM-eu.md`
- 若檔案已存在，不覆蓋；可用 `--draft` 產 `.draft.md`。
- 自動帶入最新 Lyst period、StockX period、來源清單摘要。

**Acceptance checks**

```bash
python scripts/generate_monthly_heat_report.py --month 2099-01 --region us-eu --draft
```

### C5 — Test fixtures + CI smoke checks

**Goal**  
讓核心腳本有最小穩定驗收，避免後續自動化一改就壞。

**Scope**

- 可修改：`tests/`、`.github/workflows/`、`scripts/README.md`。
- 不要修改：內容資料本身。

**Minimum checks**

```bash
python scripts/score_trends.py --demo
python scripts/generate_daily_brief.py --date 2099-01-01 --draft
python scripts/track_rankings.py --json
python scripts/validate_repo.py
```

---

## 3. 人類決策 Queue

這些不是 Claude Code 該自行決定的事，請人類 / Codex 先拍板：

1. **是否要把「韓潮」拉成獨立 monthly report**，或先只在 daily brief 裡追蹤。
2. **月報排序要不要固定 Top 5 / Top 10**，還是依訊號強弱浮動。
3. **是否要新增 content calendar 目錄**，例如 `reports/content_ideas/` 或 `content_pool/`。
4. **來源 tier 調整**：哪些來源能算 tier 1，哪些只能做 confirming signal。
5. **LLM 供應商策略**：Claude / OpenAI 是否都要支援，還是先只保留 prompt 手動流程。

---

## 4. Codex 後續固定節奏

每次 Claude Code 完成工程 PR 後，Codex 應做以下 review：

1. 跑相關 smoke check。
2. 檢查 README / operating manual / scripts README 是否同步。
3. 檢查 templates / prompts / scripts 的欄位契約是否一致。
4. 把新能力記進 `CHANGELOG.md`。
5. 如果涉及內容判斷，標出哪些是來源事實、哪些是 Style Superman 解讀。

---

## 5. 下一個建議 PR

**C1 已完成。下一個建議 PR：C2 — Ranking ingest helper。**

原因：validation 已能守住資料契約；下一步應降低更新 Lyst / StockX / Mercari 快照時的手填風險，先做 dry-run ingest，再考慮全自動來源抓取。
