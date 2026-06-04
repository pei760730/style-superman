# Operating Manual — Style Superman

每天怎麼操作這套系統。從零到一份可用的 brief + 選題。

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
- 每篇用 `prompts/article_to_insight.md` 的格式榨乾成 insight。
- 重點放在「新訊號」與「跨來源重複出現」的東西。

### Step 3 — 整理候選趨勢
把當天 insight 收斂成幾個候選趨勢，每個用 `prompts/trend_analysis.md` 做成 trend card，
並給五維度初步分。整理成 `trends.json`：

```json
[
  {"name": "...", "heat": 4, "growth": 5,
   "longevity": 3, "content_potential": 4, "accessibility": 3}
]
```

### Step 4 — 評分排序
```bash
python scripts/score_trends.py --input trends.json
```
看哪些落在 🔥 主打 / ✅ 採用，決定今天 brief 的 headline。

### Step 5 — 寫 brief
用 `prompts/daily_trend_brief.md` 把排序結果寫成完整 brief，填回 `reports/daily/YYYY-MM-DD.md`。

### Step 6 — 出選題
對 headline 趨勢用 `prompts/short_video_ideas.md` 生 2–3 個選題卡，丟進選題池。

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

完整分工、RACI 與交接模板見 [AI Collaboration Playbook](ai_collaboration.md)。

## 2. 每週

- 從選題池排 3–5 支拍攝。
- 檢查 `data/` 是否要更新（新品牌、新人物、新來源）。

## 3. 每月

- 回測評分命中率（見 `trend_scoring_rules.md` §6）。
- 視數據調整評分權重 / 內容支柱佔比，並記到 `CHANGELOG.md`。

## 4. 維護 data/

| 檔案 | 何時更新 |
|------|---------|
| `sources.yml` | 發現新的好來源 / 舊來源失效 |
| `trend_taxonomy.yml` | 出現現有分類裝不下的新現象 |
| `brands.yml` | 新品牌冒頭 / 既有品牌動向重大改變 |
| `people.yml` | 新的帶風向人物 / 影響力升降 |

## 5. 自動化開關（未來）

- **GitHub Actions**：`.github/workflows/daily-brief.yml` 可定時自動跑 Step 1（產骨架）。
  接上 LLM 後可擴到自動寫 brief。預設 `workflow_dispatch` 手動觸發，排程那行需要時再開。
- **n8n / Telegram / Notion**：把 brief 推到你每天會看的地方。
- 原則：**先手動跑順、確認有價值，再自動化。** 不要為了自動化而自動化。

## 6. 疑難排解

| 症狀 | 處理 |
|------|------|
| `ModuleNotFoundError: yaml` | `pip install pyyaml` |
| brief 已存在不覆蓋 | 故意的防呆；要重產先刪檔或用 `--draft` |
| 評分缺維度警告 | `trends.json` 補齊五個維度 |
| 中文在終端機亂碼 (Windows) | 設 `PYTHONIOENCODING=utf-8` |
