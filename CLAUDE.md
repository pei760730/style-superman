# Claude Code / AI Agent Instructions — Style Superman

> **定位**：這是擁有者的**個人**男裝潮流情報 + 挑買決策系統，**不是內容生產 / 拍片管線**。產出服務「我自己」（一個追潮流、會親手挑單品入手的玩家）：深挖趨勢、找出問題（炒作 vs 真趨勢、值不值得入手），不是產可拍選題。不要把產物導向短影音選題 / 社群貼文；daily brief 結尾是 `🛒 對我有用 For Me`，推薦直接寫在 brief / 週挑清單內——**不開獨立挑買卡**（D9，2026-06-12）：擁有者看到有興趣的會自己查、自己買。

本 repo 是一套**靠 AI Agent 長期維護的情報系統**。這份文件是 agent 的作業入口：
目標、不可破壞的假設、每次開工的迴圈、與不該做的事。
角色分工（主編 / 工程 / 人類）見 `docs/ai_collaboration.md`；歷史教訓見 `docs/lessons.md`。

## Repo 目標（一句話）

每天把全球男性潮流訊號 → 收集 → 分類 → 評分 → 變成「對我有用」的挑買判斷。
**產出有沒有持續發生，比工程漂不漂亮重要。**

## 不可破壞的核心假設

1. **不虛構**：沒來源就標 `待查`。不補排名、百分比、銷量、「爆紅」結論。
2. **資料與內容分離**：`data/` 是長期知識底層；`reports/` 是封存快照（產出後不回改）。
3. **格式即契約**：產出走 `templates/`；改 template 欄位必須同步改 `prompts/` + `docs/` + 相關腳本。
4. **不接 repo 內 LLM API**（決策 D5）：AI 撰寫由對話中的 agent 或排程雲端 agent 做，不在腳本裡呼叫 LLM、不管 API key。
5. **輕依賴**：標準庫 + pyyaml。新增依賴需人類同意。
6. **排行快照**：最新放 `snapshots:` 最上方；不同口徑分開記，不硬湊榜（細則見 `docs/rankings.md`）。

## Self-Evolution Loop（每次開工照這個迴圈）

```
Observe   → python scripts/repo_health.py        # 系統還活著嗎、文件↔程式碼有沒有漂移
Diagnose  → 看 ERROR（一致性壞了）/ WARN（產線停了）；判斷類型與優先級
Propose   → 中改以上先描述方案；涉及內容判斷 / 品牌觀點 / 費用 → 留給人類拍板
Patch     → 實際修改（branch + 單主題 PR）
Validate  → python scripts/validate_repo.py && python tests/test_smoke.py && python scripts/repo_health.py --consistency
Record    → 能力變更記 CHANGELOG.md；方向決策記 docs/decisions.md
Learn     → 踩到新坑記 docs/lessons.md（soft note；反覆出現才硬化成檢查）
Next      → repo_health.py 的 Next Actions 就是下一輪 TODO
```

## 修改前 / 修改後

- **修改前**：先跑 `repo_health.py` 知道現況；找該主題的既有檔案，**改既有的，不另起爐灶**。
- **修改後（驗收命令）**：
  ```bash
  python scripts/validate_repo.py          # 格式契約
  python tests/test_smoke.py               # 核心腳本行為
  python scripts/repo_health.py --consistency   # 文件↔程式碼一致性
  ```
  缺 `pyyaml` 時明確回報，不要為了通過檢查改掉 YAML 依賴。
- **寫程式前先自問**：能用既有檢查擋嗎？能用一條文件規則講清楚嗎？都不行才寫 code。

## 慣例

- **命名**：daily `reports/daily/YYYY-MM-DD.md`；monthly `reports/monthly/YYYY-MM-<region>.md`（region：eu / jp）；
  data id 用小寫 kebab；腳本用 snake_case 動詞開頭（generate_ / collect_ / track_ / validate_）。
- **文件同步**：加 / 改 / 刪腳本 → 同步 `scripts/README.md`（health check 會抓漏）；
  新檔案要被導覽引用，不留孤兒（health check 會抓）。
- **Changelog**：能力層面的變更（新腳本、新檢查、新資料源、移除模組）記入 `CHANGELOG.md` 對應分區（Added / Changed / Removed 別放錯區）。
- **執行既有任務卡 / 排程任務前**：先比對本檔定位與 `docs/decisions.md` 最新拍板——
  任務卡可能來自重定位前的舊世界觀（殭屍任務卡，2026-06-10 發生過）。矛盾就**停**，
  記入 decisions.md 待拍板，不執行。
- **決策過時時**：不要默默繞過；更新 `docs/decisions.md` 並在同 PR 清掉全 repo 矛盾描述、
  掃一遍排程 agent 的任務來源；「不可回頭」的拍板要在 `data/decision_guards.yml`
  留下禁用識別字（repo_health 會擋住任何把它們寫回來的 PR）。
- **Prompts**：`prompts/` 是給 AI 的內容工作模板，使用時嚴格遵守對應 template 欄位；
  工程 PR 不改 prompts 的內容判斷規則。

## 反熵原則（D7，2026-06-11）

- **新流程不得依賴人類定期手動勞動**——要嘛自動化、要嘛不做（google-trends 手動月拉的教訓）。
- **新檢查只能由重複出現的教訓硬化而來**；單次事故記 `docs/lessons.md` 即可，防止免疫系統自我增生。
- **維護/產出比是系統健康的終極指標**：月度回看時檢查 commit 比例，產出必須大於維護。

## 你不應該單獨做（留給人類 / 主編判斷）

- 判斷哪個趨勢是主打觀點；新增未驗證的榜單排名、銷量結論。
- 把月度綜合判斷寫成官方排名。
- 改 `templates/` 欄位契約（除非任務明確要求且同步全鏈）。
- 新增情報來源到 `data/sources.yml`（來源可信度是內容判斷）。
- 開啟自動排程、接外部推送、任何花錢或對外發布的動作。

## 常見坑（詳見 docs/lessons.md）

- Windows 終端 cp950：腳本都要 `sys.stdout.reconfigure(encoding="utf-8")`；CI 設 `PYTHONIOENCODING`。
- 擁有者的 Mac 沒有 `python` 只有 `python3`（3.9）：文件範例的 `python` 自行代換；新語法要相容 3.9（`X | Y` 型別註記靠 `from __future__ import annotations` 才活著）。
- workflow 檔在 GitHub 上的註冊可能無聲消失（帳號風控後遺症）：「檔案在 ≠ 在跑」，要看 run 紀錄。
- 反爬網站（ZOZO / KREAM / MUSINSA 即時榜）不硬刮；用官方公開數據手動建快照。
- `reports/daily/*.draft.md`、`reports/monthly/*.draft.md` 不入版控。
