# Operating Manual — Style Superman

每天怎麼操作這套系統。從零到一份可用的 brief + 挑買方向。

## 0. 一次性設定

```bash
git clone <repo-url> style-superman
cd style-superman
pip install pyyaml
```

## 1. 每日流程（約 20–30 分鐘）

### Step 1 — 產出今日骨架
```bash
python scripts/generate_daily_brief.py
```
會在 `reports/daily/YYYY-MM-DD.md` 產出待填草稿。

### Step 2 — 收集訊號
依 `data/sources.yml` 巡一遍核心來源（tier 1 必看）。把值得記的丟進處理：
- 有 RSS 的來源可半自動收集：`python scripts/collect_raw_signals.py --out /tmp/raw.yml`
  （或產 brief 時一併 `--with-rss --raw-signals-out /tmp/raw.yml`）。產出是**事實層** raw_signal_pack。
- 每篇用 `prompts/article_to_insight.md` 把 raw signal 補上 `signal_type` / `credibility` 並榨成 insight。
- 重點放在「新訊號」與「跨來源重複出現」的東西。

### Step 3 — 整理候選趨勢
把當天 insight 收斂成幾個候選趨勢，每個用 `prompts/trend_analysis.md` 做成 trend card，
並給五維度初步分。整理成 `trends.json`：

```json
[
  {"name": "...", "heat": 4, "growth": 5,
   "longevity": 3, "wearability": 4, "accessibility": 3}
]
```

### Step 4 — 評分排序
```bash
python scripts/score_trends.py --input trends.json
```
看哪些落在 🔥 主打 / ✅ 採用，決定今天 brief 的 headline。

### Step 5 — 寫 brief
用 `prompts/daily_trend_brief.md` 把排序結果寫成完整 brief，填回 `reports/daily/YYYY-MM-DD.md`。

### Step 6 — 出挑買方向
對 headline 趨勢用 `prompts/buy_picks.md` 生 2–3 張挑買卡（值不值得買 / 怎麼搭 / 在哪買 / 補哪個缺口），丟進挑買 shortlist。

### Step 7 — 封存
```bash
git add reports/daily/YYYY-MM-DD.md
git commit -m "brief: YYYY-MM-DD"
```

## 1.5 AI 分工（Codex / Claude Code）

日常操作可以把 AI 當成兩種角色使用：

- **Codex**：負責判斷今日趨勢、整理 prompt / template、維護文件與 PR 整合。
- **Claude Code**：負責較長程的工程任務，例如擴充 `scripts/`、補測試、批次整理 YAML / Markdown。
- **人類**：負責最後的品牌觀點、資料可信度與發布決策。

完整分工、RACI 與交接模板見 [AI Collaboration Playbook](ai_collaboration.md)。現役工程待辦由 `scripts/repo_health.py` 的 Next Actions 產生；[Codex Execution Plan](codex_execution_plan.md) 為第一輪任務卡的歷史紀錄（已封存，C1–C6 完成），只供回溯設計脈絡，不再從中複製任務卡。

## 2. 每週

- 從挑買 shortlist 收斂出 1–3 個真正想入手的方向。
- **產出一張趨勢深挖卡（歐美優先）**：挑本週最強跨源趨勢，依 `templates/trend_card_template.md`
  做「跨源查證 → 生命週期 → 全價位帶落地 → 挑買判斷」→ `reports/analysis/`（節奏規則見 Content Calendar §5）。
- 檢查 `data/` 是否要更新（新品牌、新人物、新來源）。
- 週挑買如何承接 daily brief，見 [Content Calendar](content_calendar.md)。

## 3. 每月

- **拉 Google Trends 月度快照**（約 20 分鐘）：依 `docs/rankings.md` 的固定方法論查追蹤關鍵字，
  記入 `data/rankings/google-trends.yml`——補 Lyst 季度之間的歐美量化空窗。
- 產出或回看 `reports/monthly/YYYY-MM-eu.md` 與 `YYYY-MM-jp.md`（日本線 2026-07 起），確認月報有標訊號來源分層、信心與抓取限制。
  （要手動產骨架：`python scripts/generate_monthly_heat_report.py --month YYYY-MM [--region jp]`；每月 1 號排程會自動產全文。）
- 回測評分命中率（見 `trend_scoring_rules.md` §6）。
- 視數據調整評分權重 / 情報支柱佔比，並記到 `CHANGELOG.md`。
- 若月報暴露固定弱點（例如電商即時 best-seller 訊號不足），回頭硬化相關 prompts / templates。

## 4. 維護 data/

| 檔案 | 何時更新 |
|------|---------|
| `sources.yml` | 發現新的好來源 / 舊來源失效 |
| `trend_taxonomy.yml` | 出現現有分類裝不下的新現象 |
| `brands.yml` | 新品牌冒頭 / 既有品牌動向重大改變 |
| `people.yml` | 新的帶風向人物 / 影響力升降 |

## 5. 自動化開關

- **GitHub Actions**：`.github/workflows/daily-brief.yml` 每天台灣時間 07:00 自動跑 Step 1（產骨架並 commit；2026-06-10 起開啟），也可 `workflow_dispatch` 手動觸發。
  AI 撰寫全文由對話中的 agent / 排程雲端 agent 做，**不接 repo 內 LLM API**（決策 D5，見 `docs/decisions.md`）。
- **推送（Telegram / Notion 等）**：未拍板。先手動跑順、確認有價值，再自動化；不要為了自動化而自動化。

## 5.5 系統自我檢查

每次開工（或懷疑系統停擺）先跑：

```bash
python scripts/repo_health.py
```

它會回報：daily 斷更幾天、當月月報缺不缺、Lyst 快照是否過期、文件與程式碼有沒有漂移，
並直接給出 Next Actions。agent 的完整工作迴圈見根目錄 `CLAUDE.md`。

## 6. 疑難排解

| 症狀 | 處理 |
|------|------|
| `ModuleNotFoundError: yaml` | `pip install pyyaml` |
| brief 已存在不覆蓋 | 故意的防呆；要重產先刪檔或用 `--draft` |
| 評分缺維度警告 | `trends.json` 補齊五個維度 |
| 中文在終端機亂碼 (Windows) | 設 `PYTHONIOENCODING=utf-8` |
