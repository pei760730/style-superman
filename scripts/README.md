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

可選 `--with-rss` 同時收集 RSS 來源成 raw_signal_pack（需網路；抓取失敗會優雅降級，brief 仍照產）：

```bash
python scripts/generate_daily_brief.py --date 2026-06-04 --with-rss --raw-signals-out /tmp/raw.yml
```

### `collect_raw_signals.py`
從 `data/sources.yml` 中有 RSS 的來源收集近期文章，轉成符合 `templates/raw_signal_pack_template.md` 的 raw_signal_pack（**事實層**：只收 source/title/url/date/summary；`signal_type`、`credibility` 留 `待查`，由寫 brief 的主編 agent 判讀）。純標準庫、抓取失敗自動跳過。
社群來源（`type: community`）有標題層 spam 過濾（盜播 / 導流模式；2026-06-10 reddit-techwear 灌版事件後加入），濾掉幾則會記 warning 不靜默；語意級離題判斷仍交 insight 層。

```bash
python scripts/collect_raw_signals.py                    # → stdout
python scripts/collect_raw_signals.py --out /tmp/raw.yml --limit 5
```

> raw_signal_pack 是中間產物，**不入長期版控**（見 `templates/raw_signal_pack_template.md`）。

### `generate_weekly_buy_picks.py`
產出「本週最值得買 Head-to-Toe」骨架，寫到 `reports/buy_shortlist/YYYY-Wnn.md`（ISO 週）。
自動帶入週期、本週 daily briefs 清單、各排行快照最新 period；5 區 × 3 樣的挑買內容由 AI（`prompts/weekly_buy_picks.md`）或人工補上。

```bash
python scripts/generate_weekly_buy_picks.py                  # 本週
python scripts/generate_weekly_buy_picks.py --date 2026-06-10
python scripts/generate_weekly_buy_picks.py --draft          # 產 *.draft.md（不入版控）
```

已存在的正式檔不覆寫（封存快照不回改）。

### `generate_monthly_heat_report.py`
產出當月「熱度速報」骨架（`--region us-eu|jp`，預設歐美），寫到 `reports/monthly/YYYY-MM-eu.md` / `YYYY-MM-jp.md`。自動帶入該地區量化基準（歐美：Lyst / StockX；日本：Mercari）的最新 period 與來源摘要，其餘判斷留 `待填`。

```bash
python scripts/generate_monthly_heat_report.py --month 2026-06
python scripts/generate_monthly_heat_report.py --month 2026-07 --region jp
python scripts/generate_monthly_heat_report.py --month 2026-06 --draft   # 產 *.draft.md
```

對照每月 1 號的遠端排程（全自動產全文），這支是「本地手動產骨架」的入口。內容判斷見 `prompts/monthly_heat_report.md`。

### `repo_health.py`
Repo 自我健康檢查（Self-Evolution Loop 的 Observe / Diagnose / Next Action 層）。
檢查**一致性**（每支腳本有沒有文件、文件提到的路徑存不存在、孤兒檔、workflow 引用、
**決策守衛** `data/decision_guards.yml`——已拍板決策的禁用識別字不得回到活文件 / 程式碼）與
**新鮮度 / 產線**（daily 斷更幾天、當月月報缺不缺、Lyst 快照是否落後、
重定位後產的 daily / monthly 是否符合現行契約——殭屍任務卡的產出層防線），並輸出 Next Actions。

```bash
python scripts/repo_health.py                # 人讀報告 + Next Actions
python scripts/repo_health.py --json         # 給 agent / 自動化吃
python scripts/repo_health.py --consistency  # 只跑一致性（CI 用；新鮮度不擋 PR）
python scripts/repo_health.py --strict       # WARN 也算失敗（手動巡檢）
```

一致性問題（ERROR）會讓 CI 紅；新鮮度（WARN）不擋 PR，但 `.github/workflows/health.yml`
每週一、四排程跑 `--strict` 巡檢，未通過會自動開 / 更新 `repo-health` issue。每次開工先跑這支。

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

支援來源：`lyst` / `stockx` / `mercari` / `kream` / `musinsa`。檢查項：period 必填且不可與既有重複；Lyst rank 不重複/為整數；StockX 不可壓成單一 `ranking`；Mercari / KREAM 必含 `brand_top` / `menswear_read`；MUSINSA 的 `brands` rank 不重複/為整數。輸入格式見 [templates/ranking_snapshot_template.md](../templates/ranking_snapshot_template.md)，範例見 `tests/fixtures/*_snapshot.yml`。

### `track_rankings.py`
讀取 `data/rankings/` 的排行快照（歐美 Lyst+StockX / 日本 Mercari / 韓國 KREAM+MUSINSA），顯示最新榜並比對名次演化。模組說明見 [docs/rankings.md](../docs/rankings.md)。

```bash
python scripts/track_rankings.py                    # 全部（歐美 + 日本 + 韓國）
python scripts/track_rankings.py --region jp         # 只看日本（Mercari）
python scripts/track_rankings.py --region us-eu      # 只看歐美（Lyst + StockX）
python scripts/track_rankings.py --region kr         # 只看韓國（KREAM + MUSINSA）
python scripts/track_rankings.py --source lyst       # 單一來源：lyst/stockx/mercari/kream/musinsa
python scripts/track_rankings.py --source lyst --compare   # 比對最新兩季名次（目前僅 Lyst）
python scripts/track_rankings.py --json              # 輸出 JSON
```

## 日常流程（手動版）

```bash
# 1. 產出今天的骨架
python scripts/generate_daily_brief.py

# 2. 收集訊號 → 用 prompts/ 讓 AI 整理 → 填進 brief（趨勢挑選由主編判斷，見 prompts/daily_trend_brief.md）
```

## 驗收 / 測試
PR 前（CI 也會自動跑）：

```bash
python scripts/validate_repo.py            # repo 契約（隨 data/templates/reports 數量增減）
python tests/test_smoke.py                 # 核心腳本最小驗收（無需 pytest）
python scripts/repo_health.py --consistency  # 文件↔程式碼一致性
```

`tests/test_smoke.py` 跑過所有核心指令並斷言結果；`tests/fixtures/*_snapshot.yml` 是 ingest 的合成測試範例。

## 後續規劃
- 接更多來源自動收集（非 RSS API；新增來源需人類拍板）
- 推送（Telegram / Notion / Sheets）——未拍板，先讓 daily 產線跑順
- AI 撰寫全文走對話 agent / 排程雲端 agent，**不接 repo 內 LLM API**（決策 D5）

詳見 [docs/operating_manual.md](../docs/operating_manual.md)。
