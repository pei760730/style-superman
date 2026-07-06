# Claude Code / AI Agent Instructions — Style Superman

> **定位**：這是擁有者的**個人**男裝潮流情報 + 挑買決策系統，**不是內容生產 / 拍片管線**。產出服務「我自己」（一個追潮流、會親手挑單品入手的玩家）：深挖趨勢、找出問題（炒作 vs 真趨勢、值不值得入手），不是產可拍選題。不要把產物導向短影音選題 / 社群貼文；daily brief 結尾是 `🎯 對我最相關 For Me`（**在紅單品情報層**,非買清單,D15，2026-06-14）——讓擁有者知道現在歐美日韓在紅什麼,不催買;真要入手是隨選的另一條（**不開獨立挑買卡**,D9）。

本 repo 是一套**靠 AI Agent 長期維護的情報系統**。這份文件是 agent 的作業入口：
目標、不可破壞的假設、每次開工的迴圈、與不該做的事。
角色分工（主編 / 工程 / 人類）見 `docs/ai_collaboration.md`；歷史教訓見 `docs/lessons.md`。

## Repo 目標（一句話）

每天把全球男性潮流訊號 → 收集 → 分類 → 主編判斷 → 變成「對我有用」的挑買判斷。
**產出有沒有持續發生，比工程漂不漂亮重要。**

## 不可破壞的核心假設

1. **不虛構**：沒來源就標 `待查`。不補排名、百分比、銷量、「爆紅」結論。
2. **資料與內容分離**：`data/` 是長期知識底層；`reports/` 是封存快照（產出後不回改）。
3. **格式即契約**：產出走 `templates/`；改 template 欄位必須同步改 `prompts/` + `docs/` + 相關腳本。
4. **不接 repo 內 LLM API**（決策 D5）：AI 撰寫由對話中的 agent 做（D16 後 0 排程 routine），不在腳本裡呼叫 LLM、不管 API key。
5. **輕依賴**：標準庫 + pyyaml。新增依賴需人類同意。
6. **排行快照**：最新放 `snapshots:` 最上方；不同口徑分開記，不硬湊榜（細則見 `docs/rankings.md`）。

## Self-Evolution Loop（每次開工照這個迴圈）

```
Observe   → python scripts/repo_health.py        # 系統還活著嗎、文件↔程式碼有沒有漂移
Diagnose  → 看 ERROR（一致性壞了）/ WARN（產線停了）；判斷類型與優先級
Propose   → 工程問題看到就修、修的人負責到底（D12）；涉及內容判斷 / 品牌觀點 / 費用 → 留給人類拍板
Patch     → 實際修改（branch + 單主題 PR）
Validate  → python tests/test_smoke.py   # 單一驗收入口：validate_repo 與 repo_health --consistency
            # 已由 test_smoke 內部執行（L55、L355），與 CI 同源；每輪 patch 收尾跑一次，
            # 連續 micro-edit 期間不重跑，失敗時只重跑失敗那支
Record    → 能力變更記 CHANGELOG.md；方向決策記 docs/decisions.md
Learn     → 踩到新坑記 docs/lessons.md（soft note；反覆出現才硬化成檢查）
            # 記帳收斂：decisions.md 新條目 ≤12 行（背景 2-3、拍板 3-5、可逆/guards 1-2）；
            # 事後訂正用一行「追記」，不重寫既有段落；lessons.md 單條 ≤5 行；
            # 每個 patch 的記帳（CHANGELOG + decisions/lessons + memory）在收場前一輪
            # 一次寫完，不逐版回改帳本
Next      → repo_health.py 的 Next Actions 就是下一輪 TODO
```

## Session 紀律（token 成本，2026-07-06）

> 成本模型：token 按**每次呼叫 × 當下全量 context** 計費——尾端 300K 時每條小 Bash 都是
> 一次 30 萬 token 的 cache read（實測 2026-07-05 場後半 58 個呼叫燒掉全日 60%）。

1. **一場一事**：STYLE 場照 `prompts/daily_scan_orchestration.md` 出 brief、交付 For Me 後即收場；
   途中看到的工程問題記一行到收場摘要（memory next-actions）留給下個 REPO 場——
   這是 D12「看到就修」的**分場執行**（批次修，不是回到請示制）。
2. **REPO 場一場最多一個 PR 週期**；同性質低風險文件修正合併同一 PR。
3. **跨日不續場**：隔天「接著做」一律開新對話；續作靠 memory + git log / gh api 接軌，不靠舊 context。
4. **換模型重審 / 深審已完成工作＝開新場或派 repo-auditor subagent**，輸入只帶 PR 編號讓它自抓 diff。
5. **收場儀式**：每完成一個 PR 週期或 daily 交付，agent 主動總結
   「本場已完成 X、剩餘已記 memory，建議收場、下個任務開新對話」。

## 修改前 / 修改後

- **修改前**：先跑 `repo_health.py` 知道現況；找該主題的既有檔案，**改既有的，不另起爐灶**。
- **修改後（驗收命令）**：
  ```bash
  python tests/test_smoke.py   # 單一驗收入口：validate_repo 與 repo_health --consistency 已由它內部執行，與 CI 同源
  ```
  缺 `pyyaml` 時明確回報，不要為了通過檢查改掉 YAML 依賴。
  跑驗收前先 `git status` 清掉 `reports/` 下的未追蹤暫存檔——scratch 檔會讓 `validate_repo` 紅燈，
  那是**環境髒、不是契約壞**：刪檔即可，別去放寬 `REPORT_PATTERNS`（會把契約弄鬆、改錯方向）。
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
  比對拍板用 `grep -n "^## D" docs/decisions.md` 先取索引、再只讀命中的目標段落——
  **主迴圈禁止整讀三帳本**（decisions / lessons / CHANGELOG 已達 75KB / 27KB / 85KB，
  整讀一次 ≈25-35K tokens 且永久滯留 context）。
- **決策過時時**：不要默默繞過；更新 `docs/decisions.md` 並在同 PR 清掉全 repo 矛盾描述、
  掃一遍排程 agent 的任務來源；「不可回頭」的拍板要在 `data/decision_guards.yml`
  留下禁用識別字（repo_health 會擋住任何把它們寫回來的 PR）。
- **Prompts**：`prompts/` 是給 AI 的內容工作模板，使用時嚴格遵守對應 template 欄位；
  工程 PR 不改 prompts 的內容判斷規則。

## 反熵原則（D7，2026-06-11）

- **新流程不得依賴人類定期手動勞動**——要嘛自動化、要嘛不做（google-trends 手動月拉的教訓）。
- **新檢查只能由重複出現的教訓硬化而來**；單次事故記 `docs/lessons.md` 即可，防止免疫系統自我增生。
- **終極指標是「產出有沒有持續發生」，不是 commit 比例**（2026-06-19 修正）：D16 後 daily / 週挑 對話即焚、不進 commit，「維護/產出 commit 比例」結構性量不到（永遠像維護壓倒產出，實測近 40 commit 治理:產品 = 84:3）→ **不可當健康訊號**。真健康訊號 = ① brief / 深挖**持續被產出**（有人問、agent 有跑）② 封存產物（`reports/analysis` 深挖卡 / 月報 / 週挑）有新鮮度。工程治理 commit 多 ≠ 不健康；**產線斷掉（沒人問、沒人跑）才是**。

## 管線是底盤，不是答案邊界（2026-06-14）

回答「什麼最紅 / head-to-toe / 月度回看」是**分析師工作**，要用盡所有工具：RSS 管線 + WebSearch + WebFetch + 判斷。
- **管線某部位 / 地區訊號薄 ≠ 該區沒料**——那是「主動去查」的訊號，不是「回報該區空白」的藉口。
- 任何 head-to-toe（5 部位 × 地區）或月度回看，**每格可信訊號 < 3 條（或關鍵字命中多為雜訊）時，必須主動 WebSearch / WebFetch 把該格補到有可信品項才出稿**。禁止拿「沒源 / 管線沒收到」當交差理由。
- 這條對**對話 ad-hoc 回答同樣生效**（不只走 prompt 的產出）——根因就是對話裡回 head-to-toe 時把「RSS 桶子有什麼」當成「世界上什麼紅」、頭部交白卷（見 `docs/lessons.md`）。

## 你不應該單獨做（留給人類 / 主編判斷）

- 判斷哪個趨勢是主打觀點；新增未驗證的榜單排名、銷量結論。
- 把月度綜合判斷寫成官方排名。
- 改 `templates/` 欄位契約（除非任務明確要求且同步全鏈）。
- 新增情報來源到 `data/sources.yml`（來源可信度是內容判斷；**加之前先過 D18 兩道門：① 近 30 天會持續產出新內容 ② 夠權威（非聚合/SEO 農場）**，並 WebFetch 實測可讀）。
- 開啟自動排程、接外部推送、任何花錢或對外發布的動作。

## Bash 衛生（2026-07-06）

- **能合併的指令用 `&&` 合成一發**——不把 `cd` / `export` / `git status` / `git diff` 拆成多次呼叫
  （2026-07-05 實測：`cd`×52、`export`×33 全是固定前綴稅，每發都揹全量 context）。
- **gh 一律用絕對路徑 `~/.local/bin/gh`**（不再每次 export PATH）；**git 用 `git -C ~/style-superman`**（不再 cd 前綴）。
- **等 CI 一律單呼叫**：`~/.local/bin/gh run watch <run-id>`，或同一 Bash 內 `until`+`sleep` loop（設逾時）；
  禁止逐次輪詢各發一呼叫。
- **merge 授權**：要 merge 前一句話問、使用者回「MERGE」即明確授權（2026-07-05 實證分類器放行此措辭）；
  被權限分類器擋兩次直接請使用者 GitHub UI 按 merge，不進 settings.json 攻防。

## 常見坑（詳見 docs/lessons.md）

- Windows 終端 cp950：腳本都要 `sys.stdout.reconfigure(encoding="utf-8")` **與 `sys.stderr.reconfigure(encoding="utf-8")`**（argparse 錯誤訊息 / `print(file=sys.stderr)` 走 stderr，只設 stdout 仍會在本機 cp950 吐亂碼/炸 UnicodeError）；CI 設 `PYTHONIOENCODING`。
- 擁有者的 Mac 沒有 `python` 只有 `python3`（3.9）：文件範例的 `python` 自行代換；新語法要相容 3.9（`X | Y` 型別註記靠 `from __future__ import annotations` 才活著）。
- workflow 檔在 GitHub 上的註冊可能無聲消失（帳號風控後遺症）：「檔案在 ≠ 在跑」，要看 run 紀錄。
- 反爬網站（ZOZO 永久死；KREAM / MUSINSA / SNKRDUNK 即時榜）：對話端用 Firecrawl keyless 抓、反向驗證後寫 dated 快照（D22–D24），不進腳本。
- **Firecrawl 對話端暫存 JSON 一律寫進 `scratch/`（已 gitignore）、抓完即刪**——別寫 repo root（`_fc_*.json` 沒被 gitignore、會漏進 commit）。Windows git-bash `/tmp` 與 Python 路徑不通時，scratch 子目錄是正解。
- `reports/daily/*.draft.md`、`reports/monthly/*.draft.md` 不入版控。
