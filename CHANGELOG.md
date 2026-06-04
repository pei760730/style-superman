# Changelog

本檔記錄 Style Superman 系統的演進。格式參考 [Keep a Changelog](https://keepachangelog.com/)。

## [Unreleased]

### Added
- **C6 — RSS 收集 → raw_signal_pack**
  - `scripts/collect_raw_signals.py`：從 `data/sources.yml` 有 RSS 的來源收集近期文章，轉成事實層 raw_signal_pack（純標準庫、抓取失敗優雅降級；`signal_type`/`credibility` 留待查交 article_to_insight）
  - `generate_daily_brief.py` 新增 `--with-rss` / `--raw-signals-out`
  - `tests/fixtures/sample_feed.xml` + test_smoke 加 2 項 RSS 離線測試（不依賴網路，共 9 項）
- **完成 Codex 執行計畫 C3–C5**
  - C3：`templates/raw_signal_pack_template.md` — RAW_SIGNALS 中間格式契約（接 RSS/LLM 前先固定形狀）；`prompts/article_to_insight.md`、`prompts/daily_trend_brief.md` 加引用
  - C4：`scripts/generate_monthly_heat_report.py` — 本地產月度歐美速報骨架（自動帶入 Lyst/StockX 季度基準），`--draft` 不入版控
  - C5：`tests/test_smoke.py` — 核心腳本最小驗收（7 項，無需 pytest）；接進 `ci.yml` 為 PR smoke 一步
- `scripts/ingest_ranking_snapshot.py`（C2）— 安全加入排行快照：預設 dry-run 檢查契約（period 不重複、rank 不重複、StockX 不壓成單一 ranking、Mercari 必含 brand_top/menswear_read），`--write` 才寫入且保留既有註解。附 `tests/fixtures/*_snapshot.yml` 合成範例。
- `scripts/validate_repo.py` + `.github/workflows/ci.yml` + `requirements.txt` — 補 PR smoke validation，讓 YAML / template / report 契約在 merge 前自動檢查。
- `CLAUDE.md` + `docs/codex_execution_plan.md` — 實際落地 Codex 第一輪 repo review，補 Claude Code 執行守則、工程任務卡與下一步驗收順序。
- `docs/ai_collaboration.md` — Codex / Claude Code / 人類分工手冊，補上 RACI、交接模板、review 清單與任務分派規則。
- **月度熱度速報（歐美）** — 補上「這個月什麼最紅」的月度粒度（Lyst 只有季度）
  - `templates/monthly_heat_report_template.md` + `prompts/monthly_heat_report.md`
  - `reports/monthly/` 產出區；由每月 1 號的遠端排程自動生成 `YYYY-MM-eu.md`
  - 綜合搜尋趨勢 + 電商 best-seller + 媒體/社群，對照 repo 內 Lyst/StockX 季榜，每條標信心、不編造
- `reports/analysis/2026-us-jp-overlap.md` — 歐美×日本 2026 潮流交集分析（運動鞋越界 / gorpcore / elevated basics 為共同核心；ASICS·Salomon·FOG·Uniqlo 跨市場）
- **日本 rankings + 媒體源**
  - `data/rankings/mercari-jp.yml` — Mercari 二手成交（成交 #1 Chanel→Uniqlo）
  - `track_rankings.py` 新增 `mercari` 來源 + `--region jp|us-eu` 過濾
  - `sources.yml` 新增日本 media（MEN'S NON-NO/POPEYE/Houyhnhnm）與 WEAR
  - docs/rankings.md 補日本生態與「量化榜+媒體街拍兩條腿」鐵則

### Removed
- **ZOZOTOWN 排行**（zozotown.yml + 腳本/來源 plumbing）—— 評估後移除。
  zozo.jp 由 Akamai 防護（curl 403、頁面 JS 動態、WebFetch 逾時、聚合站無逐位名次），
  無真實 headless 瀏覽器無法準確抓取，屬不該背的重量。依「不準確就拿掉」不保留半準觀察清單。
  紀錄與替代方案見 docs/rankings.md「ZOZOTOWN：評估後不採用」。
- **Rankings 模組**：定期可量化排行（`data/rankings/`）
  - `lyst-index.yml` — Lyst Index 季度快照（已收錄 2026-Q1：Top 20 品牌 + Top 10 單品）
  - `stockx.yml` — StockX 年度/年中快照（已收錄 2025 全年熱銷）
  - `scripts/track_rankings.py` — 檢視最新榜 + 比對名次演化（已驗證可跑）
  - `templates/ranking_snapshot_template.md`、`prompts/ranking_ingest.md`、`docs/rankings.md`
  - `sources.yml` 新增 lyst-index / stockx 兩個 `type: ranking` 來源
- `reports/daily/2026-06-04.md` — SS2026 基準快照（歐美 × 日 × 韓）

### Planned
- 接入真實來源抓取（RSS / Instagram / 站點）
- AI 自動撰寫 daily brief 全文（接 Claude / OpenAI）
- 推送管線（Telegram / Notion / Google Sheets）
- 短影音選題自動排程

## [0.1.0] — 2026-06-04

### Added
- 初始 repo 結構：`data/`、`reports/`、`prompts/`、`scripts/`、`templates/`、`docs/`、`.github/`
- 資料底層：`sources.yml`、`trend_taxonomy.yml`、`brands.yml`、`people.yml`
- 四套 AI 提示詞模板（daily brief / trend analysis / article to insight / short video）
- 兩支腳本：`generate_daily_brief.py`、`score_trends.py`
- 三套產出模板：daily brief / trend card / short video idea
- 系統文件：system design / content strategy / trend scoring rules / operating manual
- GitHub Actions 排程骨架 `daily-brief.yml`
