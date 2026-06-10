# Codex Execution Plan — Style Superman

> **📦 已封存（2026-06-10）**：本文件是第一輪工程任務的歷史紀錄——C1–C6 全部完成、C7 已 dropped（D5）。
> 它**不再是現役待辦來源**；現役待辦由 `python scripts/repo_health.py` 的 Next Actions 產生，
> 方向決策見 `docs/decisions.md`。保留本檔是為了決策可回溯（任務卡格式仍可參考 §2）。

> 這是 Codex 依 `docs/ai_collaboration.md` 實際跑完第一輪 repo review 後留下的執行計畫。目的不是再寫一份抽象分工，而是把「下一步該做什麼」拆成 Claude Code / 人類可以直接接手的任務卡。

## 0. 本輪 Codex 判斷

目前 repo 已經是一個可運作的 **男性潮流情報 MVP**：

- `data/` 已有來源、taxonomy、品牌、人物與排行快照。
- `scripts/` 已能產 daily brief 骨架、趨勢評分、排行檢視、排行 ingest、月報骨架與 repo validation。
- `prompts/` + `templates/` 已形成內容契約，且已有 `raw_signal_pack` 中間格式。
- `reports/` 已有 daily、monthly、analysis 三種產物。
- `tests/` + GitHub Actions 已有 smoke checks，可在 PR 前守住基本契約。

Codex 本輪不急著改腳本邏輯，優先做三件事：

1. **補齊工程交接面**：讓 Claude Code 有清楚的 repo 指令與任務卡。
2. **修正文件導覽落差**：README 要反映目前已存在的 monthly / ranking / raw signal 能力。
3. **鎖定下一階段工程順序**：C1–C5 已完成；下一步先接 RSS 收集到 `raw_signal_pack`，再做 vendor-neutral LLM brief adapter。

---

## 1. 內容契約現況

| 契約 | 位置 | 狀態 | Codex 決策 |
|------|------|------|------------|
| Daily Brief | `templates/daily_brief_template.md` + `prompts/daily_trend_brief.md` | 可用 | 保持 Markdown 結構穩定；工程只填骨架，主編判斷由 Codex / 人類做。 |
| Trend Card | `templates/trend_card_template.md` + `prompts/trend_analysis.md` | 可用 | 五維度分數必須附理由，仍是 `score_trends.py` 的核心輸入契約。 |
| Buy Pick 挑買卡 | `templates/buy_pick_template.md` + `prompts/buy_picks.md` | 可用 | 只由 headline trends 轉出；誠實給「買 / 等 / 跳過」，不要把弱訊號硬轉成「現在最該買」。 |
| Ranking Snapshot | `templates/ranking_snapshot_template.md` + `prompts/ranking_ingest.md` | 已有 ingest + validation | 維持 dry-run 優先；正式寫入前必須可被 `validate_repo.py` 檢查。 |
| Monthly Heat Report | `templates/monthly_heat_report_template.md` + `prompts/monthly_heat_report.md` | MVP | 月報是綜合判斷，不是官方榜；每條都要有來源與信心。 |
| Raw Signal Pack | `templates/raw_signal_pack_template.md` | 契約已定 | raw 層只存來源事實，不做「會紅 / 該追」判斷；C6 會把 RSS 收集接到此格式。 |

---

## 2. Claude Code 任務卡

以下任務按建議順序排列。每張卡都可以獨立開 PR，但不要同一個 PR 混太多方向。C6 之後屬 **Claude Code 的工程範圍**；Codex 只在本文件定規格、做後續 review，不在本輪修改 `scripts/` / `tests/` / CI。

### ✅ C1 — Repo validation CLI（已完成：`scripts/validate_repo.py`）

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

### ✅ C2 — Ranking ingest helper（已完成：`scripts/ingest_ranking_snapshot.py`）

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

### ✅ C3 — Daily brief source pack format（已完成：`templates/raw_signal_pack_template.md`）

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

### ✅ C4 — Monthly heat report generator MVP（已完成：`scripts/generate_monthly_heat_report.py`）

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

### ✅ C5 — Test fixtures + CI smoke checks（已完成）

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

### C6 — RSS 收集 → `raw_signal_pack`（Claude Code 工程範圍）

**Goal**
讓 `generate_daily_brief.py` 可從 `data/sources.yml` 中有 RSS 的來源收集當日 / 近 N 日文章，轉成符合 `templates/raw_signal_pack_template.md` 的 `raw_signal_pack`，供人工或後續 LLM 撰寫 brief 使用。

**Scope**

- 可修改：`scripts/generate_daily_brief.py`、必要時新增 `scripts/collect_raw_signals.py` / parser helper、`scripts/README.md`、`tests/` fixtures、`docs/operating_manual.md`。
- 不要修改：`prompts/`、`templates/` 契約、`data/` 既有內容事實、`reports/` 已發布內容。
- RSS 收集只處理 `data/sources.yml` 既有且 `rss` 非空的來源；新增來源需另開資料 PR 並由人類確認。
- C6 只做「來源事實收集與格式化」，不做 trend scoring、不做 headline 判斷、不呼叫 LLM。

**Contract**

- Command examples:

```bash
python scripts/generate_daily_brief.py --date 2026-06-04 --draft --with-rss --raw-signals-out /tmp/raw_signal_pack.yml
python scripts/generate_daily_brief.py --date 2026-06-04 --draft --with-rss --lookback-days 2
```

- Input:
  - `data/sources.yml`：讀取 `id/name/region/type/tier/url/rss`。
  - RSS / Atom feed：解析 article `title/link/published/summary`；不要求抓全文。
  - CLI options：`--with-rss` 啟用收集；`--lookback-days N` 預設 `1`；`--raw-signals-out PATH` 可把 raw pack 寫到指定檔案。
- Output:
  - raw pack YAML 必須符合 `templates/raw_signal_pack_template.md` 的 `signals:` list 結構。
  - brief draft 可新增一段 `RAW_SIGNALS` / `待整理來源訊號`，貼上 YAML 或摘要；若無訊號則明確寫 `今日 RSS 未取得可用訊號`。
  - raw pack 預設不寫入 repo 長期路徑；若使用者指定 repo 內路徑，仍不得自動 commit。
- Field mapping:
  - `source_id/source_tier/region` 來自 `data/sources.yml`。
  - `url/title/published/summary` 來自 RSS；日期解析失敗填 `待查`，不可猜。
  - `signal_type` RSS 無法可靠判斷時填 `culture` 或 `style`，並在 summary 保持事實語氣；不要編造 taxonomy 細分。
  - `credibility` 預設依 source tier / type 給初值：tier 1 media/ranking 可為 `high`，tier 2 可為 `medium`，社群 / tier 3 / 轉述型內容為 `medium` 或 `low`；規則需寫入 README 或 docs。
- Error handling:
  - 單一 feed 失敗不得讓整體命令失敗；輸出 warnings，其他來源照跑。
  - 全部 feed 失敗時 exit code 可仍為 `0`（因 daily draft 可生成），但必須在輸出與 draft 中標明沒有取得 raw signals。
  - 網路 timeout、非 XML、日期解析失敗都要有可讀 warning。

**Acceptance checks**

```bash
python scripts/generate_daily_brief.py --date 2099-01-01 --draft --with-rss --raw-signals-out /tmp/raw_signal_pack.yml
python scripts/generate_daily_brief.py --date 2099-01-01 --draft --with-rss --lookback-days 2
python scripts/validate_repo.py
python -m unittest discover -s tests
```

### ~~C7 — LLM 自動撰寫 brief adapter 介面~~（DROPPED，2026-06-04）

> **不做。** 經檢討（見 `docs/decisions.md` D5）：系統已透過排程雲端 agent 自動產出 AI 報告，C7 屬重複造既有能力；加真實 API 違反「不為寫 code 而寫 code」。需要 AI 寫 brief 時把 `raw_signal_pack` 交給對話中的 Claude / 排程 agent 即可。日後若有無人值守硬需求再重啟。以下原規格僅留作紀錄。

**Goal（原）**
在不綁定 Claude / OpenAI / 其他供應商的前提下，先建立「把 raw signals + prompt/template 轉成完整 daily brief」的 adapter 介面，讓未來可替換 LLM provider，也可保留手動 prompt 流程。

**Scope**

- 可修改：`scripts/generate_daily_brief.py`、必要時新增 `scripts/llm_adapter.py`、`scripts/README.md`、`tests/` fixtures、`docs/operating_manual.md`。
- 不要修改：`prompts/`、`templates/` 契約、`data/` 內容事實、`reports/` 已發布內容。
- C7 只定工程介面與 dry-run / mock 行為；真實 API key、供應商選型與費用策略需人類拍板（見 `docs/decisions.md`）。

**Contract**

- Adapter interface（可用 Python class / function / protocol 實作，命名由 Claude Code 決定，但需文件化）：
  - Input:
    - `date: YYYY-MM-DD`
    - `raw_signal_pack: dict | str`（符合 C3/C6 契約）
    - `brief_template: str`（來自 `templates/daily_brief_template.md`）
    - `prompt_template: str`（來自 `prompts/daily_trend_brief.md`，但本任務不改 prompt）
    - `provider: manual|mock|claude|openai|...`
    - optional `model`, `temperature`, `max_tokens`
  - Output:
    - 完整 Markdown brief 字串，能寫入 `reports/daily/YYYY-MM-DD.md` 或 `.draft.md`。
    - metadata dict：`provider/model/generated_at/raw_signal_count/warnings`。
  - Error handling:
    - provider 不存在、缺 API key、API timeout、回傳空內容時，不得覆蓋既有 brief；改回 manual draft 並輸出明確 warning。
    - LLM output 不得新增無來源排名 / 百分比 / 事實；若 adapter 做不到自動驗證，至少在 metadata warnings 標記 `requires_human_review`。
- CLI behavior:

```bash
python scripts/generate_daily_brief.py --date 2026-06-04 --draft --from-raw /tmp/raw_signal_pack.yml --llm-provider mock
python scripts/generate_daily_brief.py --date 2026-06-04 --draft --from-raw /tmp/raw_signal_pack.yml --llm-provider manual
```

- `manual` provider：不呼叫 API，只把 prompt + raw signals 組成可複製的手動撰寫包。
- `mock` provider：測試用，回傳 deterministic brief，讓 CI 不依賴外部 LLM。
- 真實 provider：可先留 stub；若要實作 Claude / OpenAI API，需另開 PR 並由人類確認供應商策略與 key 管理。

**Acceptance checks**

```bash
python scripts/generate_daily_brief.py --date 2099-01-01 --draft --from-raw tests/fixtures/raw_signal_pack.yml --llm-provider mock
python scripts/generate_daily_brief.py --date 2099-01-01 --draft --from-raw tests/fixtures/raw_signal_pack.yml --llm-provider manual
python scripts/validate_repo.py
python -m unittest discover -s tests
```

---

## 3. 人類決策 Queue

這些不是 Claude Code 該自行決定的事，請人類 / Codex 先拍板。Codex 本輪已把建議方案、理由與待確認狀態整理到 [Decisions](decisions.md)：

1. **是否要把「韓潮」拉成獨立 monthly report**，或先只在 daily brief 裡追蹤。
2. **月報排序要不要固定 Top 5 / Top 10**，還是依訊號強弱浮動。
3. **是否要新增挑買 shortlist 目錄**，例如 `reports/buy_shortlist/` 或 `shortlist/`。
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

**工程 backlog（C1–C6）已全部完成；C7 已 DROPPED（見 D5）。目前無待辦工程 PR。**

下一步不是工程，而是**讓系統跑、累積真實資料**：Lyst Q2（7 月排程自動 ingest）、每月歐美速報（每月 1 號排程）。需要新工程時再依實際需求開卡，不預先堆 backlog。
