# Claude Code Instructions — Style Superman

Claude Code 在本 repo 的定位是 **工程執行者 / 批次修改者**。請先讀：

1. `docs/ai_collaboration.md` — AI / 人類分工總規則
2. `docs/codex_execution_plan.md` — Codex 已拆好的工程任務卡與驗收標準
3. `docs/operating_manual.md` — 日常流程
4. `scripts/README.md` — 腳本用法

## 你應該做

- 實作已定義好的 CLI / automation / validation / test 任務。
- 修改 `scripts/`、測試 fixtures、自動化設定、批量格式清理。
- 依任務卡同步更新相關文件，例如 `scripts/README.md`、`docs/operating_manual.md`。
- 回報改了哪些檔案、跑了哪些命令、哪些檢查受環境限制。

## 你不應該單獨做

- 不要自行判斷哪個趨勢要成為 Style Superman 的主打觀點。
- 不要新增未驗證的榜單排名、百分比、銷量或「爆紅」結論。
- 不要把月度綜合判斷寫成官方排名。
- 不要改變 `templates/` 欄位契約，除非任務卡明確要求，且同步更新 prompts / docs / scripts。

## 資料與內容鐵則

- 沒來源就標 `待查`，不要補數字。
- 區分「原始來源事實」與「男裝視角推論」；推論要標成觀察或解讀。
- 排行資料最新快照放在 `snapshots:` 最上方。
- StockX 報告有不同口徑，照原欄位分開記，不要硬湊 Top 10。

## 建議驗收命令

```bash
python scripts/score_trends.py --demo
python scripts/generate_daily_brief.py --date 2099-01-01 --draft
python scripts/track_rankings.py --json
python scripts/track_rankings.py --source lyst --compare
python scripts/validate_repo.py
```

若環境缺 `pyyaml`，請明確回報；不要為了通過檢查而改掉 YAML 依賴。
