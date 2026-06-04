# AI Collaboration Playbook — Style Superman

這份文件把 **ChatGPT / Codex（以下稱「Codex」）** 與 **Claude Code** 在本 repo 的責任拆開，避免兩個 AI 都在做同一件事、或把「內容判斷」和「工程落地」混在一起。

核心原則：

- **Codex 做系統總編與 repo 變更整合**：看整體架構、定規格、拆任務、寫文件、整合 PR。
- **Claude Code 做長程工程執行與大範圍重構**：照規格實作腳本、測試、自動化與批次修改。
- **人類做最終品牌判斷**：決定哪些趨勢值得講、語氣是否符合 Style Superman、是否發布。

---

## 1. Repo 現況切分

| 區域 | 主要用途 | 目前成熟度 | 最適合主責 |
|------|----------|------------|------------|
| `README.md` | 專案入口、能力說明、目錄導覽 | 穩定 | Codex |
| `docs/` | 系統設計、營運手冊、評分規則、排行方法 | 穩定但會隨流程演進 | Codex |
| `prompts/` | 給 AI 的內容工作模板 | 已有基礎，需要持續調校 | Codex 主責，Claude Code 可批量整理 |
| `templates/` | Daily brief、trend card、ranking snapshot 等固定輸出契約 | 穩定 | Codex |
| `data/` | 來源、品牌、人物、taxonomy、ranking 快照 | 半人工維護 | 人類 + Codex 審核，Claude Code 可做格式清理 |
| `scripts/` | brief 生成、趨勢評分、排行追蹤 | 可執行 MVP | Claude Code 主責，Codex 定規格 / review |
| `reports/` | 每日、月度、主題分析產物 | 持續產出 | 人類 + Codex 內容判斷，Claude Code 可批次生成骨架 |

---

## 2. 角色定位

### 2.1 Codex：系統總編 / 架構整合者

Codex 負責讓這套 repo「方向正確、格式穩定、能被人用」。優先處理需要跨文件理解、資訊架構、內容判斷與 PR 整合的任務。

**Codex 應該主責：**

- 定義 Style Superman 的資訊架構與工作流。
- 修改 `README.md`、`docs/`、`templates/`、`prompts/` 的規格性內容。
- 將使用者的模糊需求拆成可執行 issue / task list。
- 設計 `scripts/` 的輸入輸出契約、錯誤處理規則與測試情境。
- 審核 `data/` 的 schema 是否一致、是否有沒有來源的推論。
- 整合 Claude Code 產出的 patch，確認沒有破壞內容策略與資料契約。
- 在 PR 中說清楚「為什麼這樣改」、跑過哪些檢查、還有哪些限制。

**Codex 不應該長時間主責：**

- 大量機械式檔案修改。
- 大型腳本重構的所有細節。
- 長時間追 dependency / lint / CI failure 的工程迭代。
- 未經人類確認就把流行判斷寫成既定事實。

### 2.2 Claude Code：工程執行者 / 批次修改者

Claude Code 負責把已經定義好的規格落地，尤其適合長時間、多檔案、可測試的工程任務。

**Claude Code 應該主責：**

- 擴充 `scripts/`：CLI 參數、資料驗證、輸出格式、錯誤訊息。
- 建立或補強測試：fixtures、sample input、snapshot output。
- 批量整理 YAML / Markdown 格式，但不改變未確認的內容事實。
- 實作 GitHub Actions、排程、n8n / Telegram / Notion 串接前的 adapter。
- 做大型 rename / refactor / typed schema migration。
- 追蹤 CI / lint / test failure，直到工程檢查穩定。

**Claude Code 不應該單獨決定：**

- 哪個趨勢是 Style Superman 的主打觀點。
- 哪些品牌 / 人物應該被列為「重要」。
- 內容語氣、價值判斷、爭議角度是否符合品牌。
- 在沒有來源的情況下補排名、百分比或市場結論。

### 2.3 人類：品牌主編 / 發布決策者

人類保留最後決策權，尤其是會影響品牌定位與外部發布的內容。

**人類應該拍板：**

- 今日 headline trend 是否值得採用。
- hot-take 是否太硬、太冒犯或不夠有梗。
- 內容是否要導購、是否要避開特定品牌或爭議。
- 任何需要付費工具、外部 API key、正式發布的動作。

---

## 3. RACI 分工表

RACI：**R = Responsible 執行**、**A = Accountable 最終負責**、**C = Consulted 諮詢**、**I = Informed 知會**。

| 任務 | Codex | Claude Code | 人類 |
|------|:-----:|:-----------:|:----:|
| 新增 / 修改系統設計文件 | R/A | C | C |
| 修改 prompt 與 template 契約 | R/A | C | C |
| 新增 CLI 功能 | C/A | R | I |
| 補測試與修 CI | C | R/A | I |
| 新增資料來源到 `data/sources.yml` | R | C | A |
| 新增品牌 / 人物追蹤 | C | I | A |
| 更新排行快照 | C | R | A |
| 產出每日 brief 骨架 | C | R | I |
| 判斷每日 headline trend | R | I | A |
| 生成短影音選題 | R | I | A |
| 大型格式遷移 | A | R | C |
| PR 最終整理與說明 | R/A | C | I |

---

## 4. 標準交接流程

### 4.1 從人類需求到可執行任務

1. **Codex 先讀 repo 現況**：確認需求影響 `docs/`、`data/`、`scripts/`、`reports/` 哪些區域。
2. **Codex 寫規格**：先定義輸入、輸出、檔案位置、不可做事項。
3. **需要長程工程時交給 Claude Code**：任務要包含明確檔案範圍與驗收命令。
4. **Claude Code 實作並回報**：列出改了哪些檔案、哪些測試通過 / 失敗。
5. **Codex 整合 review**：確認內容語氣、資料契約、README / docs 是否同步。
6. **人類 final review**：確認品牌判斷與發布策略。

### 4.2 Claude Code 任務卡模板

把任務交給 Claude Code 時，請盡量使用這個格式：

```md
## Goal
一句話說明要達成的使用者價值。

## Scope
- 可修改：`scripts/...`, `tests/...`
- 不要修改：`data/rankings/...` 的未驗證內容、`reports/` 的已發布分析

## Contract
- Input: ...
- Output: ...
- Error handling: ...

## Acceptance checks
- `python scripts/... --demo`
- `python scripts/... --json`

## Notes
不要補沒有來源的排名或百分比；遇到內容判斷請留 TODO 給 Codex / 人類。
```

### 4.3 Codex Review 清單

Claude Code 回來後，Codex review 時至少檢查：

- 是否遵守既有 Markdown / YAML 結構。
- 是否讓 `README.md`、`docs/operating_manual.md`、`scripts/README.md` 同步。
- 是否有把推論寫成事實。
- CLI 是否有清楚 help、錯誤訊息是否能讓非工程使用者看懂。
- 是否跑過與變更相關的最小檢查。

---

## 5. 依任務類型分派

### 5.1 文件 / 架構類

**預設交給 Codex。**

例：

- 新增一份「月報流程」文件。
- 重寫內容策略。
- 定義 trend card 的欄位。
- 決定 `reports/monthly/` 的命名規則。

原因：這些任務牽涉品牌語氣、資訊架構與長期維護成本，比單純改檔案更重要。

### 5.2 工程 / 自動化類

**Codex 定規格，Claude Code 實作。**

例：

- `generate_daily_brief.py` 接真實 RSS。
- `score_trends.py` 支援 CSV / YAML input。
- `track_rankings.py` 加上 schema validation。
- GitHub Actions 每天產 brief 並開 PR。

原因：工程任務需要大量細節迭代，Claude Code 適合長時間追測試；但輸入輸出契約仍要先由 Codex 與人類確認。

### 5.3 內容情報類

**人類 / Codex 主責，Claude Code 只做格式與批次輔助。**

例：

- 今天哪些趨勢值得寫進 daily brief。
- 某個品牌是否已經從 niche 變 mainstream。
- 某個 hot-take 會不會傷品牌。

原因：內容判斷不是純文字生成，必須保持來源意識、品牌意識與人工決策。

### 5.4 資料維護類

**按資料風險分派。**

| 資料動作 | 分派 |
|----------|------|
| 格式化 YAML、補缺漏欄位 | Claude Code |
| 新增已確認來源 URL / RSS | Codex 或 Claude Code，Codex review |
| 新增品牌 / 人物重要性描述 | 人類 + Codex |
| 更新榜單排名 / 百分比 | Claude Code 可貼來源資料，但人類 / Codex 要驗證 |

---

## 6. 防呆規則

1. **不虛構來源**：沒有來源就標 `待查`，不要補排名、百分比、銷量或「爆紅」結論。
2. **不讓工程改壞內容契約**：`templates/` 欄位變更時，要同步更新 `prompts/`、`docs/` 與相關腳本。
3. **不讓內容改壞自動化**：`data/` schema 變更後，要跑對應腳本確認仍能解析。
4. **不雙重主責**：同一個任務只能有一個 accountable owner；另一個 AI 只能輔助或 review。
5. **PR 要能被回看**：每次 PR 說清楚改動原因、驗收命令與未解限制。

---

## 7. 建議工作流範例

### 範例 A：新增「月度歐美熱度報告」自動化

1. Codex 定義月報欄位與資料來源信心規則。
2. Claude Code 實作 `scripts/generate_monthly_heat_report.py` 與測試 fixture。
3. Codex review 月報文字是否符合 `docs/content_strategy.md`。
4. 人類確認第一份月報是否可發布。

### 範例 B：新增 StockX 最新榜單

1. 人類或 Codex 提供來源連結 / 原始資料。
2. Claude Code 將資料整理進 `data/rankings/stockx.yml`，不自行補不存在欄位。
3. Claude Code 跑 `python scripts/track_rankings.py --source stockx --json`。
4. Codex 檢查 menswear focus 是否只是推論；必要時標成「觀察」。
5. 人類確認是否納入月報或 daily brief。

### 範例 C：調整趨勢評分權重

1. Codex 根據回測結果提出權重修改理由。
2. Claude Code 修改 `scripts/score_trends.py` 與相關測試。
3. Codex 同步更新 `docs/trend_scoring_rules.md`。
4. 人類確認新的排序是否符合內容策略。

---

## 8. 最短版口訣

- **Codex：定方向、寫規格、管內容契約、整合 PR。**
- **Claude Code：照規格寫程式、跑測試、做批量工程。**
- **人類：決定品牌觀點、資料可信度與是否發布。**
