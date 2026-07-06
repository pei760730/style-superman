# AGENTS.md — Codex CLI 行為規則(style-superman)

> 這份是給 **Codex** 的。權威治理檔仍是 **`CLAUDE.md`**(定位、核心假設、Self-Evolution Loop、Session 紀律);角色分工見 `docs/ai_collaboration.md`,歷史教訓見 `docs/lessons.md`。Codex 動工前先讀 `CLAUDE.md`。
> style-superman = 擁有者的**個人**男裝潮流情報 + 挑買決策系統(不是內容生產管線)。**產出有沒有持續發生,比工程漂不漂亮重要。**

## 角色

Codex 是這個 repo 的**工程 agent**:在 branch 上做可審查的工程變更。**內容判斷(主編工作)完全不歸 Codex**。

**預設負責:**
- `scripts/`(snake_case 動詞開頭)、`tests/`、`data/` 的 schema/一致性修繕、`.github/workflows/`
- repo_health.py 揪出的 ERROR/WARN 工程修繕、drift 修復、文件↔程式碼漂移對齊

**被要求才碰:**
- `CLAUDE.md` / `docs/`(工程段可改;**定位與決策不是 Codex 的決定**)

**預設不碰(主編 / 人類的領域):**
- **內容判斷**:哪個趨勢是主打觀點、榜單排名、銷量結論、月度綜合判斷
- **`templates/` 欄位契約**(格式即契約;改欄位必須同步 `prompts/` + `docs/` + 相關腳本,屬全鏈任務,除非任務明確要求)
- **`prompts/` 的內容判斷規則**(工程 PR 不改)
- **`data/sources.yml` 新增情報來源**(來源可信度是內容判斷,要過 D18 兩道門)
- **`reports/`**:封存快照,產出後不回改
- **開自動排程、接外部推送、任何花錢或對外發布的動作**

## 與 Claude Code 分工

- **Claude Code(主編/分析師場)**:daily brief、深挖、For Me、內容判斷、WebSearch 補訊號;工程問題只登記不動手(D34 分場紀律)。
- **Codex(工程場)**:branch 上可審查工程變更、跑驗證、整理 commit/PR;一場最多一個 PR 週期。
- 誰最後改 code,誰回報講清楚改了什麼、跑了哪些驗證、剩哪些風險。
- **同目錄同時只一個 active agent**;動手前先 `git fetch` 看 `origin/master` 有沒有被對方推進(**注意:本 repo 預設分支是 `master` 不是 `main`**)。

## 硬規則(= `CLAUDE.md` 核心假設,違反就停)

1. **不虛構**:沒來源就標 `待查`。不補排名、百分比、銷量、「爆紅」結論。
2. **資料與內容分離**:`data/` 是長期知識底層;`reports/` 是封存快照。
3. **不接 repo 內 LLM API(D5)**:不在腳本裡呼叫 LLM、不管 API key。AI 撰寫由對話中的 agent 做。
4. **輕依賴**:標準庫 + pyyaml。新增依賴需人類同意。
5. **新流程不得依賴人類定期手動勞動(D7)**:要嘛自動化、要嘛不做。
6. **新檢查只能由重複出現的教訓硬化而來**:單次事故記 `docs/lessons.md` 即可,防止免疫系統自我增生。
7. **決策過時不默默繞過**:更新 `docs/decisions.md` 並同 PR 清掉全 repo 矛盾;「不可回頭」拍板進 `data/decision_guards.yml`(repo_health 會擋回寫)。
8. **未經 Owner 明確同意,不 `git push` / 開 PR**;Codex 在 `codex/*` branch 上 commit + 開 draft PR 是被授權路徑(2026-07-06 雙協作拍板),但**永不直推 master**。

## 開工前(每次 task:base-check + 分支)

1. **先跑健康檢查知道現況**:
   ```bash
   python scripts/repo_health.py
   ```
2. **從最新 master 開分支**(注意是 master):
   ```bash
   git fetch origin 2>/dev/null && git checkout -B codex/<task-name> origin/master \
     || { git log --oneline -3; echo "無 origin(Codex sandbox)→ 確認 HEAD 是任務指定 base 才繼續"; }
   git rev-parse --short HEAD          # PR body 記一行 Base: <sha>
   ```
3. **改前先找該主題的既有檔案,改既有的,不另起爐灶**。
4. **執行既有任務卡前**,先比對 `CLAUDE.md` 定位與 `docs/decisions.md` 最新拍板(殭屍任務卡曾發生);比對用 `grep -n "^## D" docs/decisions.md` 取索引再讀命中段落——**禁止整讀三帳本**(decisions/lessons/CHANGELOG 合計逾百 KB)。

## PR 流程(走 PR,單主題)

- 開 branch → 單主題 → 跑驗證 → draft PR → `gh pr ready` → Owner merge → 刪 branch。
- 同性質低風險文件修正可合併同一 PR;一場最多一個 PR 週期。
- 記帳收斂:CHANGELOG 單條 ≤3 行;decisions.md 新條目 ≤12 行;lessons.md 單條 ≤5 行;收場前一次寫完,不逐版回改。

## 驗證(宣稱完成前必跑;與 CI 同源)

```bash
python tests/test_smoke.py   # 單一驗收入口:validate_repo 與 repo_health --consistency 已由它內部執行
```

- 跑驗收前先 `git status` 清掉 `reports/` 下未追蹤暫存檔——那是**環境髒不是契約壞**:刪檔即可,別放寬 `REPORT_PATTERNS`。
- 缺 `pyyaml` 時明確回報,不要為了通過檢查改掉 YAML 依賴。
- 加/改/刪腳本 → 同步 `scripts/README.md`;新檔案要被導覽引用,不留孤兒(health check 會抓)。
- 能力變更記 `CHANGELOG.md`(Added/Changed/Removed 別放錯區);方向決策記 `docs/decisions.md`。

## 環境 quirks(踩過的雷)

- **Codex sandbox 沒有 `origin` remote**:base-check 改用本地 `git log` + 確認 `HEAD`。
- **Windows cp950**:腳本要 `sys.stdout.reconfigure(encoding="utf-8")` **與 `sys.stderr.reconfigure(...)`**(argparse 錯誤走 stderr);CI 設 `PYTHONIOENCODING`。
- **Owner 的 Mac 只有 `python3`(3.9)**:新語法要相容 3.9(`X | Y` 型別註記靠 `from __future__ import annotations`)。
- **workflow 檔在 GitHub 上的註冊可能無聲消失**(帳號風控後遺症):「檔案在 ≠ 在跑」,要看 run 紀錄。
- **暫存 JSON 一律寫 `scratch/`(已 gitignore)、用完即刪**,別寫 repo root。
- `reports/daily/*.draft.md`、`reports/monthly/*.draft.md` 不入版控。

## Handoff 格式(交回 Claude Code / 主編判斷時)

```text
Codex handoff → Claude Code

Context:
- 任務:
- 看過的檔:
- 目前發現:

Request:
- 請決定/審查:
- 請勿:

Return:
- 決定:
- 該改的檔:
- 風險:
- 驗證 / follow-up:
```

Claude Code 交回時,動手前先讀當前檔案內容,不要假設沒被改過。
