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
