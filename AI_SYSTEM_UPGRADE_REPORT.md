# AI System Upgrade Report

> Sleep-mode 巡檢的點時審計紀錄（每輪附加一個 Run 區段）。
> 本檔屬歷史紀錄，與 CHANGELOG 同列 repo_health 路徑掃描排除。

## Run 2026-06-13 (HEAD ab66fa1)

### Base
- Branch / HEAD / Repo root / Time: `master` / `ab66fa1` / `/Users/pei/style-superman` / 2026-06-13 00:09 CST
- Working tree before changes: clean（與 origin/master 同步）
- Working tree after changes: 6 個 modified（見 Files changed）+ 本報告（untracked）；無 commit / push / branch

### Project snapshot
- Project type: 個人男裝潮流情報 + 挑買決策系統（AI agent 長期維護；docs/config/automation 複合型）
- Primary language: Python（標準庫 + pyyaml）；77 個追蹤檔
- Entrypoints: `scripts/`（generate_ / collect_ / track_ / validate_ / repo_health）
- Automation: 3 個 GitHub workflows（ci / daily-brief 每日 23:00Z / health 巡檢一四 01:00Z）+ 雲端排程 routine（README 自動化全貌表）
- Validation: `validate_repo.py`、`tests/test_smoke.py`（20 cases，無 pytest 依賴）、`repo_health.py --consistency|--strict`
- AI instruction files: `CLAUDE.md`（含 Self-Evolution Loop、決策守衛機制）——成熟，本輪僅補一條環境坑
- High-risk areas: `daily-brief.yml` 直推 master；`data/decision_guards.yml` 拍板守衛；`reports/` 封存快照不回改

### What I inspected
全部 3 個 workflows、`repo_health.py` / `validate_repo.py` / `generate_daily_brief.py` 全文、
`test_smoke.py` 全文、`collect_raw_signals.py` 抓取層（timeout 確認 15s 存在）、
README 自動化描述 vs workflow 實際行為交叉比對、decision_guards / trend_history 消費端追查、
分支清單。未深讀：`prompts/`、`reports/` 內容層（內容判斷屬主編/人類）、
`score_trends.py` / `track_rankings.py` / `ingest_ranking_snapshot.py` 內部（已有 smoke 覆蓋）。

### System-level issues found
#### High risk
1. **health.yml 看門狗假成功**：`repo_health --strict | tee health-report.txt` 在 Actions 預設
   shell（`bash -e {0}`，**無 pipefail**）下，失敗碼被 tee 吃掉 → 巡檢 step 永遠綠 →
   `if: failure()` 永不觸發 → issue 永不會開。健檢警告體系的最後出口實際是斷的。
   本機 repro：`bash -ec 'sh -c "exit 1" | tee /dev/null'` → exit 0。
2. **health.yml 開 issue 路徑連帶失效**：`gh issue list --jq '.[0].number'` 無開啟 issue 時
   輸出字面 `null` → `[ -n "null" ]` 為真 → 對 issue "null" 留言而失敗，首次警告 issue 開不出來。

#### Medium risk
3. **README 自動化描述錯置**：時間軸與全貌表稱 07:00 Actions 骨架做「RSS 28 源收集」，
   實際 workflow 未帶 `--with-rss`（workflow 註解自己也說只填模板）；RSS 由 07:30 填寫 routine 收。
   誤導擁有者對「哪一層斷了該查誰」的判斷。
4. **data/ YAML 驗證覆蓋洞**：`trend_history.yml`、`decision_guards.yml` 不在 validate_repo
   任何檢查內（連可解析都沒驗）。decision_guards 壞掉會讓 repo_health 直接 traceback（紅但難讀）；
   trend_history 無腳本消費端，壞了會沉默存在。

#### Low risk
5. **repo_health 週挑落後週數跨年少算**：`(Δ年)×52+(Δ週)` 在 53 週 ISO 年（**2026 即是**）
   跨年少算一週，WARN 晚一週才響。repro：latest=2026-W53、now=2027-W01 → 舊式=0、正確=1。
6. **本機環境坑**：擁有者 Mac 無 `python`（僅 `python3`，3.9.6），全 repo 文件範例皆寫 `python`；
   agent 第一次跑就會撞 command not found。

### Changes made（每項附動機）
1. `.github/workflows/health.yml`：巡檢 step 補 `set -o pipefail` + 註解——讓看門狗失敗真的紅。
2. `.github/workflows/health.yml`：`--jq '.[0].number // empty'` + 註解——無 issue 時走 create 分支。
3. `README.md`（2 處）：RSS 收集歸屬更正為 07:30 routine——文件對齊事實。
4. `scripts/validate_repo.py`：新增 `check_yaml_parseable`，data/ 內無專屬契約的 YAML 自動納入
   「可解析 + 頂層 mapping」最低防線——補 docstring 既有承諾（catch broken YAML）的洞，
   非新檢查類別（D7 反熵相容）；未來新 data 檔免註冊即有防護。
5. `scripts/repo_health.py`：週挑落後改用 ISO 週一日期相減——修跨年少算。
6. `scripts/repo_health.py`：`PATH_SCAN_EXCLUDE` 加入本報告——點時審計紀錄與 CHANGELOG 同性質，
   允許提到歷史/已刪檔案。
7. `CLAUDE.md` 常見坑：補 python3-only 環境與 3.9 語法相容一條。
8. `CHANGELOG.md`：上述能力層變更記入 Fixed / Changed（repo 慣例）。

### Files changed
`.github/workflows/health.yml`、`README.md`、`scripts/validate_repo.py`、`scripts/repo_health.py`、
`CLAUDE.md`、`CHANGELOG.md`、`AI_SYSTEM_UPGRADE_REPORT.md`（新增，本檔）

### Verification run
| Check | Command | Result | Notes |
|---|---|---|---|
| 契約驗證 | `python3 scripts/validate_repo.py` | ✅ 全綠 | 新增 2 檔（decision_guards / trend_history）入列 |
| 煙霧測試 | `python3 tests/test_smoke.py` | ✅ 20 passed, 0 failed | 改動後重跑 |
| 健檢 strict | `python3 scripts/repo_health.py --strict` | ✅ exit 0，無 ERROR/WARN | 含本報告存在後重跑 |
| 編譯 | `python3 -m compileall scripts tests` | ✅ | 本機 3.9.6（CI 3.12） |
| workflow YAML | safe_load 3 檔 | ✅ 可解析 | |
| pipefail 修法 | `bash -ec 'set -o pipefail; …repo_health --strict --date 2026-09-01 \| tee …'` | ✅ exit 1（修正前同鏈 exit 0） | 端到端模擬 Actions run 內容 |
| 壞 YAML 探針 | data/ 放壞檔跑 `--data` | ✅ exit 1 並點名；移除後 exit 0 | 探針已刪 |
| W53 公式 | 邊界三組對照（53 週年跨年） | ✅ 新式與日期相減一致 | |

### Issues fixed (with evidence)
上表 1–8 全部對應 Verification run；唯一**未能實機驗證**的是 gh `--jq // empty`（需 GitHub API；
邏輯層驗證：`// empty` 為標準 jq 語法，null→空字串使 `-n` 判斷正確走 create 分支）。

### Existing issues not fixed
- `daily-brief.yml` push race：23:00Z checkout 與 push 之間若有他人 commit 會 push 失敗。
  低流量時段、發生率低、重跑即復原；加 rebase 屬行為變更，不在本輪低風險範圍。
- `generate_daily_brief.py --date` 不驗格式：壞日期會產出壞檔名，但 validate_repo 的
  reports 命名檢查會在 CI 抓到，下游有防線,不重複設防（D7）。
- gh `// empty` 修正未實機跑過（見上）。下次 health patrol 真的紅一次時觀察 issue 是否正常開出。

### Remaining risks
- health.yml 的修正要等下一次排程（週一/四 01:00Z）或手動 dispatch 才真正在 Actions 環境驗證。
- 「workflow 檔在 ≠ 在跑」（lessons 已記）：本輪只能改檔案,無法確認 GitHub 端排程註冊狀態。

### Branch cleanup candidates
#### Possibly safe to delete after human review
全部 10 條遠端 topic 分支皆已 merge 進 origin/master：
`brief/2026-06-10`、`brief/2026-06-11`、`chore/health-output-drift`、`docs/readme-reality-sync`、
`feat/daily-output-contract-guard`、`fix/daily-brief-tz`、`health/rss-coverage-denominator`、
`ops/remove-temp-cron`、`rss-coverage-vogue-korea`、`sources/deep-dig-2026-06-11`
（多數 PR 分支已被自動刪除,這 10 條是漏網;可在 GitHub 設定開啟 auto-delete merged branches）
#### Do not delete yet
無未 merge 分支。

### Recommended next actions
1. 手動 dispatch 一次 health.yml,確認巡檢在 Actions 環境綠燈、且故意紅時 issue 開得出來（驗 gh 修正）。
2. 開啟 GitHub「Automatically delete head branches」,清掉 10 條殘留分支並止住未來累積。
3. `trend_history.yml` 目前僅 flow_calendar 引用、無腳本消費端——若雷達/月報 prompts 確實引用它,
   維持現狀即可;若三個月無人引用,考慮併入趨勢卡體系（內容判斷,留給主編/人類）。

### Safe to commit?
- Yes
- Why: 全部改動為防禦性修正與文件對齊,驗收三件套 + smoke 20 case 全綠;無行為面擴張。
- Conditions before commit: 依 repo 慣例走 branch + 單主題 PR（建議拆兩個:workflows 假成功修正一個、
  validate/repo_health/docs 一個）;CI 綠後 merge。

### Correction (2026-06-13, 同日)
Branch cleanup candidates 一節有誤:所列 10 條「遠端 topic 分支」實為**本機過期的
remote-tracking refs**(遠端早已刪除,`git fetch --prune` 即清掉)。遠端實況只有 master。
已開啟 repo 設定 delete_branch_on_merge,之後 merge 即自動刪 head 分支。
紅路徑(issue 自動開出)已於同日實彈演習驗證(run 27430529539 → issue #76,演習後關閉)。

---

## Run 2026-06-14 (HEAD b8036c7)

### Base
- Branch / HEAD / Repo root / Time: `master` / `b8036c7` / `C:/Users/user/projects/style-superman` / 2026-06-14 01:52 CST
- Working tree before changes: clean（與 origin/master 同步）
- Working tree after changes: 12 個 modified（見 Change ledger）；無 commit / push / branch
- Pre-existing modified files: 無
- Pre-existing untracked files: 無

### Project snapshot
- Project type: 個人男裝潮流情報 + 挑買決策系統（AI agent 長期維護；docs/config/automation 複合型）
- Primary language: Python（標準庫 + pyyaml）
- Entrypoints: `scripts/`（generate_ / collect_ / track_ / validate_ / repo_health / ingest_）
- Automation: 3 個 workflows（ci / daily-brief / health）+ 雲端排程 routine
- Validation: `validate_repo.py`、`tests/test_smoke.py`（**18** cases，score_trends 砍後從 20 降）、`repo_health.py --consistency|--strict`
- AI instruction files: `CLAUDE.md`（成熟）；本輪修正其使命句殘留漂移
- High-risk areas: `daily-brief.yml` 直推 master；`data/decision_guards.yml` 守衛；`reports/` 封存快照不回改

### What I inspected
自上次巡檢（06-13）後新增 4 個 merge（#84 月報 compare、#85 people 10→3、#86 全砍 score_trends/D14、#87 啟用 trend_history）。
本輪聚焦「被移除元件是否仍被文件描述成現行」這類一致性檢查器抓不到的 prose 漂移：
全 repo grep `評分/加權/score`、`insight`、`trends.json`、people 數量宣稱；交叉比對 D14（score_trends 砍）
與 2026-06-11（insight 層砍）的實況。未深讀 reports/ 內容層（內容判斷屬主編/人類）。

### System-level issues found
#### High risk
無。working tree 乾淨、驗收三件套全綠、無 conflict residue、無 secrets 疑慮。

#### Medium risk
1. **D14 後「評分」文件漂移（補 #86 漏網）**：score_trends 已砍、趨勢挑選回歸主編判斷,但 9 處 prose
   仍把「評分」寫成現行管線步驟/能力（含 `CLAUDE.md` + `README.md` 的一句話使命）。一致性檢查器只抓
   dir-prefixed 路徑,抓不到這類概念性 prose → 下個 agent/人讀了會去找不存在的 score_trends 或誤以為有評分步驟。
2. **insight 層殘留引用（補 2026-06-11 漏網）**：中間 insight 層 06-11 已移除,但 3 處（2 個 code 註解 +
   scripts/README）仍把「語意級離題判斷」寫成交給 insight 層 → 同類「移除元件仍被描述成 live 下游」。

#### Low risk
3. `docs/operating_manual.md` 疑難排解列指向不存在的 `trends.json`（score_trends 配套,已不存在）→ dead reference。

### Change ledger
| File | Change | Reason | Risk | Verification |
|---|---|---|---|---|
| CLAUDE.md | 使命句「分類→評分」→「分類→主編判斷」 | D14:無自動評分 | low(文字) | grep clean + triad 綠 |
| README.md | 使命句/時間軸/人機協作/roadmap 4 處去評分 | 同上 | low(文字) | 同上 |
| docs/system_design.md | 設計原則「可解釋的評分」→「可解釋的判斷(不走自動評分,D14)」;輸出去「可評分」 | 同上 | low(文字) | 同上 |
| docs/operating_manual.md | 刪「評分缺維度警告/trends.json」疑難排解列 | dead ref | low(刪列) | 同上 |
| docs/flow_calendar.md | 回饋迴路去「評分規則/權重」 | 同上 | low(文字) | 同上 |
| docs/style_strategy.md | 「校準評分」→「校準挑買判斷」 | 同上 | low(文字) | 同上 |
| prompts/trend_analysis.md | 標頭「供評分」→「供簡報」 | 評分段#86已移除 | low(prose,非判斷規則) | 同上 |
| templates/trend_card_template.md | 標頭「供評分」→「供簡報」 | 同上 | low(prose,非欄位token) | validate 綠 |
| data/trend_taxonomy.yml | 2 處 YAML 註解去評分字眼 | 同上 | low(註解) | YAML 可解析 |
| scripts/collect_raw_signals.py | 2 處註解 insight 層→主編 agent | 06-11 移除 | low(註解) | smoke 18 綠 + compileall |
| scripts/README.md | insight 層→主編 agent | 同上 | low(文字) | 同上 |
| CHANGELOG.md | 記 2 條 Fixed | repo 慣例 | low | — |

### Files changed
`CLAUDE.md`、`README.md`、`docs/system_design.md`、`docs/operating_manual.md`、`docs/flow_calendar.md`、
`docs/style_strategy.md`、`prompts/trend_analysis.md`、`templates/trend_card_template.md`、
`data/trend_taxonomy.yml`、`scripts/collect_raw_signals.py`、`scripts/README.md`、`CHANGELOG.md`、
`AI_SYSTEM_UPGRADE_REPORT.md`（本檔）。共 12 檔 +21/-17（不含本報告）。

### Verification run
| Check | Command | Result | Notes |
|---|---|---|---|
| 契約驗證 | `python scripts/validate_repo.py` | ✅ 全綠 | 改動後 |
| 煙霧測試 | `python tests/test_smoke.py` | ✅ 18 passed, 0 failed | 含改過的 collect_raw_signals |
| 健檢一致性 | `python scripts/repo_health.py --consistency` | ✅ 一切健康,無待辦 | |
| 編譯 | `python -m compileall -q scripts tests` | ✅ | |
| YAML 可解析 | `yaml.safe_load(trend_taxonomy.yml)` | ✅ | 確認改註解未壞 YAML |
| 殘留 grep | `git grep 評分/加權/insight 層 live` | ✅ CLEAN（剩的全是「不走自動評分」/D14 移除註記） | |

### Issues fixed (with evidence)
1–3 全部對應 Verification run；最終 grep 確認 live prose 中已無把評分/insight 層當現行步驟的描述,
僅存正確的「已移除」歷史註記。所有改動皆為文字/註解,零邏輯。

### Existing issues not fixed
- `daily-brief.yml` push race（上輪已記,行為變更不在低風險範圍）。
- 上輪 gh `// empty` 修正仍待下次 health patrol 真紅一次時觀察（已於 06-13 實彈演習驗過紅路徑,見上一 Run）。

### Remaining risks
- 無新增風險。本輪純文件對齊,不影響任何產線行為;最壞情況是文字描述,不會讓能動的東西壞掉。

### Branch cleanup candidates
#### Possibly safe to delete after human review
- 本機分支（merged-by-ancestry,確認可刪）：`brief/2026-06-10`、`brief/2026-06-11-v2-action-ledger`、
  `buy-pick/2026-06-12-teva-nhoolywood`。
- 本機過期 remote-tracking refs：`git fetch --prune` 即清（repo 已開 delete_branch_on_merge,遠端實況僅 master）。
  注意 squash-merge 的分支不會被 `--merged` 認出,勿據此誤判未 merge。
#### Do not delete yet
- 無 ancestry 上真正未 merge 的分支。

### Recommended next actions
1. 走 branch + 單主題 PR 提交本輪（建議單一 PR：純文件漂移清理,主題一致）;CI 綠後 merge。
2. （選配）`git fetch --prune` + 刪 3 條本機 merged 分支,清掉 stale 視圖。

### Safe to commit?
- Yes
- Why: 12 檔全為文件/註解文字對齊,零邏輯;驗收三件套 + smoke 18 全綠;無行為擴張、無 secrets、可逆。
- Conditions before commit: 依 repo 慣例 branch + 單主題 PR（主題：清 D14/insight 移除後的殘留 prose 漂移）。

---

## Run 2026-06-21 (HEAD 56e8509)

### Base
- Branch / HEAD / Repo root / Time: `master` / `56e8509` / `C:/Users/user/projects/style-superman` / 2026-06-21 02:14 CST
- Target 選擇：啟動目錄 `C:/Users/user`（家目錄，非 git repo）。本階段唯一活躍 repo = `style-superman`，故以此為 target（家目錄做系統改善無意義）。
- Working tree before changes: clean 但有 1 個既存 untracked 檔（見下）
- Working tree after changes: 2 個 tracked modified（ci.yml、repo_health.py）+ 本報告；無 commit / push / branch
- Pre-existing modified files: 無
- Pre-existing untracked files: `reports/analysis/2026-06-19-brand-radar-japanese-vintage.md`（06-19 既存，封存深掘卡；依 dirty-tree 保護**全程未碰**）

### Project snapshot
- Project type: 個人男裝潮流情報 + 挑買決策系統（AI agent 長期維護；docs/config/automation 複合型）
- Primary language: Python（標準庫 + pyyaml）；81 個追蹤檔
- Entrypoints: `scripts/`（generate_ / collect_ / track_ / validate_ / repo_health）
- Automation: 4 個 workflows（ci / daily-brief[僅 dispatch] / flash-brief[僅 dispatch] / health[週一四 01:00Z]）。**自 06-14 巡檢後**：daily-brief schedule 已於 D16 移除（本輪確認無殘留）。新增 `.mcp.json`（Firecrawl keyless，對話端，D22）。
- Validation: `validate_repo.py`、`tests/test_smoke.py`（**23** cases）、`repo_health.py --consistency|--strict`；CI 跑 3.9+3.12 矩陣 + ruff
- AI instruction files: `CLAUDE.md`（成熟，本輪未改）
- High-risk areas: `daily-brief.yml` push（僅 dispatch，風險已降）；`data/decision_guards.yml` 守衛；`reports/` 封存快照不回改

### What I inspected
自 06-14 巡檢後新增大量活動（D15–D24、PR #133–#141：flash 層、D21 移除排行 CLI、D22 Firecrawl、D23/D24 重開韓/日量化榜、taste:anchor、日本 denim canon）。本輪聚焦「快速變動引入的漂移」：
全部 4 個 workflows 全文（schedule / concurrency / 假成功路徑）、`repo_health.py` Lyst 檢查段、
removed-component 全 repo grep（`ingest_ranking_snapshot` / `score_trends` / `track_rankings --compare|--json` / daily-brief schedule 宣稱）、`.gitignore` 對 Firecrawl 對話端 scratch 的覆蓋、健檢三件套現況。
未深讀：reports/ 內容層（封存不回改）、prompts/ 內容判斷（屬主編）。

### System-level issues found
#### High risk
無。健檢三件套全綠、working tree 乾淨、無 secrets 疑慮、無假成功。

#### Medium risk
1. **`repo_health.py:304` 活工具指向已刪腳本**：Lyst 落後 WARN 的修復提示叫使用者「跑 …→ `ingest_ranking_snapshot.py` 補快照」，但該腳本**已於 D21（06-20）刪除**。健檢儀表板（最常被下個 agent/人讀的出口）正在把人導向不存在的檔 → 誤判/重做風險。**已修**（見 Change ledger）。

#### Low risk
2. **Firecrawl 對話端 scratch 未被 gitignore 覆蓋**：D22/23/24 後「對話端 Firecrawl 抓 → 寫暫存 JSON」成為**重複工作流**（本輪 session 即 3 次：musinsa/kream/snkrdunk）。實作把暫存寫到 **repo root**（`_fc_*.json`，因 Windows git-bash `/tmp` 與 Python 路徑不通，見 memory），但 `.gitignore` 的 `scratch/` 只蓋目錄、**不蓋 root 的 `_fc_*.json`** → 忘了 `rm` 會被 `git add .` 帶進 commit。**未改 .gitignore**（理由見 Existing issues not fixed）→ 列入 Recommended next actions。
3. **封存卡引用已刪 `score_trends.py`**：`reports/analysis/2026-washed-denim.md` 的「評分（餵 score_trends.py）」段引用 D14 已刪腳本。但 `reports/` 是**封存快照、產出後不回改**（CLAUDE.md），此卡為 score_trends 仍存在時的歷史產物 → **正確地保持不動**，僅記錄；非 live 系統漂移。

### Change ledger
| File | Change | Reason | Risk | Verification |
|---|---|---|---|---|
| scripts/repo_health.py | Lyst WARN 修復提示：移除已刪的 `ingest_ranking_snapshot.py` 指向，改「對話請 AI 依 prompts/ranking_ingest.md 編進 lyst-index.yml（D21）」 | 活工具指向已刪腳本（medium #1） | low（提示字串，非邏輯；prompts/ranking_ingest.md 仍存且 clean） | py_compile OK + triad 綠 + grep 確認剩的只是「已移除」史註 |
| .github/workflows/ci.yml | 加 `concurrency: {group: ci-…ref, cancel-in-progress: true}` | 同分支連續 push 取消舊 run、省 Actions 額度（memory: AI 高頻 push 為額度主因；用戶跨 repo 偏好）| low（取消的只是被取代的舊 run；master 與 PR 不同 ref 互不取消，不影響正確性）| 4 workflows YAML 全部 safe_load OK |

> 兩檔本輪皆**首次**被本 session 修改（非 pre-existing dirty）。

### Files changed
`scripts/repo_health.py`、`.github/workflows/ci.yml`、`AI_SYSTEM_UPGRADE_REPORT.md`（本檔）。共 2 檔 +8/-1（不含本報告）。

### Verification run
| Check | Command | Result | Notes |
|---|---|---|---|
| 契約驗證 | `python scripts/validate_repo.py` | ✅ exit 0 | 改動後 |
| 煙霧測試 | `python tests/test_smoke.py` | ✅ 23 passed, 0 failed | |
| 健檢一致性 | `python scripts/repo_health.py --consistency` | ✅ 一切健康，沒有待辦 | 含改過的 repo_health 自身 |
| 編譯 | `python -m py_compile scripts/repo_health.py` | ✅ | |
| workflow YAML | safe_load × 4 | ✅ 全可解析 | 含新 concurrency 區塊 |
| 漂移消除 | `git grep ingest_ranking_snapshot -- scripts/*.py` | ✅ 僅剩「已移除」史註，無 live 指向 | |
| daily-brief schedule 漂移 | grep README/docs schedule 宣稱 | ✅ 全部正確標「D16 已移除」，無漂移 | 反向驗證：原假設有漂移 → 證偽 |

### Issues fixed (with evidence)
- medium #1（repo_health 指向已刪腳本）：對應上表 py_compile + grep + triad，已修且驗證。
- 其餘為記錄/建議，未做破壞性修改。

### Existing issues not fixed
- **Low #2（Firecrawl scratch gitignore）**：刻意不改 `.gitignore`。`_fc_` 是本 session 臨時前綴、非文件化慣例；gitignore 特定前綴會給**脆弱的假安全**（下個 agent 換個命名就漏），且為未文件化慣例加 ignore pattern 違反 repo 反熵紀律。durable 解法是「Firecrawl scratch 一律寫進已 ignore 的 `scratch/` 目錄」這個**慣例決策**（屬擁有者拍板）→ 列 Recommended next actions。
- **Low #3（封存卡引用 score_trends）**：reports/ 封存不回改，正確保持不動。
- `daily-brief.yml` push race（前兩輪已記，行為變更不在低風險範圍；現僅 dispatch 觸發，風險再降）。

### Remaining risks
- ci.yml concurrency 的真實效果要等下次有並發 PR push 才在 Actions 端可見；本機僅能驗 YAML 可解析（「workflow 檔在 ≠ 在跑」，lessons 已記）。
- 本輪純防禦性，無產線行為擴張；最壞情況是提示字串/CI 取消舊 run，不會讓能動的東西壞掉。

### Branch cleanup candidates
（read-only 檢查）
#### Possibly safe to delete after human review
- 遠端實況：repo 已開 `delete_branch_on_merge`，本 session PR #133–#141 分支應已自動刪。本機若有 stale remote-tracking refs，`git fetch --prune` 即清。
#### Do not delete yet
- 無 ancestry 上真正未 merge 的分支（master 為唯一長期分支）。

### Recommended next actions
1. **（選配，擁有者拍板）Firecrawl 對話端 scratch 慣例**：把臨時 JSON 一律寫進已 gitignore 的 `scratch/`（而非 repo root `_fc_*.json`），或在 `CLAUDE.md`/Firecrawl workflow 註記「抓完即刪」。比 gitignore 特定前綴更 durable。
2. 本輪 2 檔走 branch + 單主題 PR 提交（建議單一 PR：「sleep-mode: 修 repo_health 已刪腳本指向 + CI 加 concurrency」，兩者皆防禦性、主題一致）；CI 綠後 merge。
3. 下次有並發 PR 時順手確認 ci.yml concurrency 真的取消了被取代的舊 run。

### Safe to commit?
- Yes
- Why: 2 檔皆防禦性（修活工具指向已刪檔 + CI 省額度 guard），零產線行為擴張；驗收三件套 + smoke 23 + 4 workflow YAML 全綠；無 secrets、可逆。既存 untracked 檔全程未碰。
- Conditions before commit: 依 repo 慣例 branch + 單主題 PR；**不要** `git add .`（會把既存 untracked 的 brand-radar 卡一起帶進，那是獨立產物，應另行處理）。建議 `git add scripts/repo_health.py .github/workflows/ci.yml AI_SYSTEM_UPGRADE_REPORT.md`。
