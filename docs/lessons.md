# Lessons — Style Superman 教訓簿（Self-Evolution Loop 的 Learn 層）

> 這裡記「犯過的錯、踩過的坑、與對策」。規則升級路徑：
> **soft note（記在這）→ 反覆出現 → 硬化成 `validate_repo.py` / `repo_health.py` 檢查或文件硬規則。**
> 不要一犯錯就直接加規則；也不要讓同一個坑踩第三次。
>
> 每條格式：日期 · 發生什麼 · 對策 · 硬化狀態。

---

## 已硬化（檢查已存在，記錄根因）

### 2026-06-10 · 殭屍任務卡：排程 agent 拿舊世界觀照做
- **發生什麼**：6/5 拍板「內容生產 → 個人挑買」重定位，但改動留在本機 5 天沒 push。期間排程 agent 讀到的 remote decisions.md 仍是舊方向（D3 = content_ideas 選題池），照舊任務卡把選題池落地成 PR 並 merge——對 agent 來說它完全照規矩辦事。根因有兩層：**(1) 未 push 的拍板等於不存在**（agent 的世界觀 = origin/master）；(2) 任務卡沒有時效 / 一致性檢查，方向變了沒人通知執行端。
- **對策**：拍板當天就 push（哪怕開 draft PR）；agent 執行任何既有任務卡前先比對 CLAUDE.md 定位與 decisions.md 最新拍板，矛盾就停（已寫入 CLAUDE.md 慣例）。
- **硬化**：`data/decision_guards.yml` + `repo_health.py` 決策守衛檢查（ERROR，CI 擋）——「不可回頭」的拍板留下禁用識別字（如 `content_ideas`、`short_video`），任何把它們寫回活文件 / 程式碼的 PR 直接紅燈，**殭屍任務卡的產物進不了 master**。守衛只防識別字層；任務卡本身的時效仍靠執行前比對（流程規則）。

### 2026-06-11 · 殭屍任務卡（第三例）：守衛只在 PR/CI 層生效，直推 master 的排程 agent 繞過全部防線
- **發生什麼**：擁有者要求深掃「拍攝殘留」，發現月度排程 routine（歐美熱度速報）的任務卡仍是重定位前版本——明寫「2–3 條可拍選題」，且收尾是 `git push origin master` **直推**。直推不經 PR，決策守衛與產出契約檢查（都掛在 CI）完全攔不到；7/1 下次執行就會把可拍選題直接寫進 master。同次深掃也抓到守衛 pattern 漏字：`content_angle` 標籤組（taxonomy 內整組內容生產視角標籤）從未在禁用清單裡。
- **對策**：repo 內的防線只護得住「走 PR 的變更」——**排程 agent 任務卡一律要求開分支 + PR，禁止直推 master**；拍板後要主動盤點 repo 外的任務指示（雲端 routine prompt），不能只改 repo。
- **硬化**：兩個 routine（月度速報、Lyst watcher）任務卡已改為分支 + PR 流程並植入定位鐵則；`decision_guards.yml` pattern 補上 `content_angle`。

### 2026-06-10 · 殭屍任務卡（第二例）：守衛擋活文件，舊世界觀產出從 reports/ 進來
- **發生什麼**：決策守衛上線當天，2026-06-10 的 daily brief 仍以舊世界觀產出（趨勢卡用「對創作者的意義」、結尾是「🎬 可拍選題 Content Hooks」，沒有「🛒 對我有用 For Me」）並進了 master。守衛沒抓到，因為 `reports/` 是封存快照、刻意不在守衛 scope（歷史快照本來就含舊識別字，掃全部會誤殺）——但「重定位之後才產的 brief」不是歷史，是產出端（排程 / 外部 agent 的任務指示）還沒換腦。
- **對策**：守衛的「活文件」邊界要照**產出日期**切，不是照目錄切：拍板日之後產的報告也算活的。產出端的任務指示（repo 外的排程 agent prompt）要跟著拍板一起更新。
- **硬化**：`repo_health.py` 新增報告產出契約檢查（WARN，health.yml 週期巡檢盯）——重定位拍板日（2026-06-05）之後產的 daily / monthly 必含現行契約段落（daily「🛒 對我有用 For Me」、monthly「🛒 本月挑買方向」）、不得含重定位前識別字；歷史快照不溯及、不回改（2026-06 月報產於 6/1，屬拍板前歷史）。smoke 反向探針保護該檢查本身。

### 2026-06-14 · brief 天天列同一個單品（去重只防同款、漏了下架與品牌疲勞）
- **發生什麼**：擁有者反映「nonnative×Timberland / Moonstar / NB 204L 連看 3 天」。查證：nonnative×Timberland 06-11（頭條）+ 06-12（增量）確實連 2 天、且 6/13 已發售（過了時刻我試跑還重列）；NB 204L 其實當天才首現，但 New Balance 這品牌近一週每天換型號上榜（1890 / 2010 / SI×NB / 1954R / 991 / 204L）→ 讀起來像跳針。既有「增量寫法」只防同一單品逐日重貼，漏了 (a) 過了發售 / 高峰時刻沒下架、(b) 同品牌天天換型號的疲勞。
- **對策（已落地，本次 PR）**：`prompts/daily_trend_brief.md` 任務 8 + `prompts/weekly_buy_picks.md` 連續性條，加：① 近 7 天已列過 + 無新事實 + 已過時刻 → **整個不列**（消失，非增量）；② 同品牌一天最多 1 則，只換型號要嘛跳過、要嘛明寫輪替。在紅＝現在在升 / 到頂，非已發生舊聞（接 D15）。
- **硬化狀態**：prompt 規則層（D7：先文件規則、不寫 code）。若再犯（寫手不遵守），候選硬化：`repo_health` 比對近 N 天 brief 的單品 / 品牌頻次，超標 WARN。

### 2026-06-10 · 警告無人看見：產線停擺時恰好沒人 push
- **發生什麼**：repo_health 的新鮮度檢查（daily 斷更等）只在有人跑它時才被看見；CI 又只在 push / PR 時觸發——**產線停擺的時候，正是最沒有 push 的時候**，警告形同不存在。lessons 原 soft note「工程全綠掩蓋產線停擺」的根因即此。
- **對策**：警告必須自己找上門，且要變成「持久物件」而不是一次性 log。
- **硬化**：`.github/workflows/health.yml`——每週一、四排程跑 `repo_health.py --strict`（WARN 也算失敗），失敗即自動開 / 更新 `repo-health` issue。頻率刻意不設每日（避免通知疲勞衰退成噪音）；daily 斷更 3 天內必被下一次巡檢抓到。它同時是 daily-brief.yml 的獨立看門狗（那邊排程若無聲死掉，斷更會在這裡現形）。「同類警告兩週沒人理 → 修產線或改宣告節奏」仍是人類決策，issue 模板內建提醒。

### 2026-06-10 · GitHub workflow 註冊會無聲消失
- **發生什麼**：`daily-brief.yml` 從 init 就在 origin/master 上，但 GitHub Actions 的 workflow 註冊表裡沒有它——連手動 dispatch 都按不了，且沒有任何錯誤訊息。期間帳號曾被 GitHub 風控 suspend 過，`ci.yml` 因每次 push 都觸發而自動重新註冊，`daily-brief.yml` 沒被改過就一直失聯。
- **對策**：對該檔做一次內容變更並 push，GitHub 會重新註冊。
- **硬化**：`repo_health.py` 管不到 GitHub 端；教訓是「**排程 / workflow 的存在 ≠ 在跑**」，要看實際 run 紀錄。daily 斷更由 `repo_health.py` 的新鮮度檢查捕捉（斷更即警告，不管原因是哪層）。

### 2026-06-10 · 文件比決策慢，會留下兩套世界觀
- **發生什麼**：D5 拍板「不接 LLM API」後，`system_design.md`、`operating_manual.md`、`scripts/README.md`、`CHANGELOG.md` Planned、`daily-brief.yml` 註解仍寫著「未來接 LLM API 自動撰寫」。後來的讀者（人或 agent）會不知道哪個是現實。
- **對策**：拍板一個決策時，同一個 PR 內 grep 全 repo 找與該決策矛盾的描述一併改掉。
- **硬化**：兩層。**識別字層已機器化**——`data/decision_guards.yml` 讓每個「不可回頭」的拍板留下禁用識別字（檔名 / 欄位名 / 目錄名），repo_health 掃到即 ERROR、CI 擋。**散文層（兩段文字語意互相打架）機器抓不到，誠實劃界給 review**：guard pattern 刻意不放會出現在否定句的自然語言詞（「不要做短影音」會誤殺），所以拍板後的「全 repo 矛盾掃描」這步仍是人 / agent 的 review 義務（CLAUDE.md 慣例）。

### 2026-06-04 · 反爬網站不要硬刮（ZOZO / Akamai）
- **發生什麼**：嘗試抓 ZOZOTOWN 男裝銷售榜，curl 403 / JS 動態 / 聚合站無逐位名次，全部失敗。
- **對策**：「不準確就拿掉」——不保留半準資料，不背 headless 反偵測的重量。詳細紀錄見 `docs/rankings.md` 的 ZOZOTOWN 一節。KREAM / MUSINSA 即時榜同理，改用官方稿公開數據手動建快照。
- **硬化**：已寫進 `docs/rankings.md` 鐵則；新來源評估時先確認「能不能穩定、合法、低成本地拿到」再加進 `sources.yml`。

## Soft notes（觀察中，尚未硬化）

### 2026-06-13 · 沒讀過原文就寫「為什麼推薦」：roundup 進來只有標題
- **發生什麼**：daily brief 把 Vogue Korea「一條牛仔褲指南」只寫成「夏季丹寧指南」，沒給任何品牌——擁有者問「你都給我這題目了，為什麼不給確切哪些品牌？要有確實讀完才能知道為什麼推薦」。根因在管線：`collect_raw_signals.py` 只抓 RSS 標題＋短摘要、不抓內文，listicle/roundup 到寫手手上本來就是空的，寫手卻照樣補了「對我的意義」＝沒讀就推薦。
- **對策（已落地，本次 PR）**：`prompts/daily_trend_brief.md` 立「推薦的證據門檻」——進推薦位（For Me 值得入手）或寫「對我的意義」前要讀過原文，簡介行必含至少一個原文事實（價格/型號/材質/發售日/具體主張）當「讀過的證明」；清單型報導要 fetch 原文挖出 top 4–6 品牌；讀不到具體事實的降到訊號層報標題＋待查，不准編「為什麼」。
- **硬化狀態**：未硬化（單例，依 D7 反熵先記 soft note）。若再犯，候選硬化兩條（都動管線/契約、需擁有者拍板）：**(a)** collect 對「要進推薦/headline」的項補抓內文塞進 `RAW_SIGNALS`（管線層，最接近真保證——寫手手上直接有全文）；**(b)** `validate_repo` 加 gate：`值得入手`/headline 必含一個可查證事實或 `待查＋去哪查`，否則紅燈（契約層強制）。

### 2026-06-11 · 排程 workflow 的「今天」是 UTC 的今天
- **發生什麼**：daily-brief 排程設 UTC 23:00（＝台灣 07:00）跑，但腳本不帶 `--date` 時用 runner 本地日期——UTC 23:00 的「今天」是台灣的**昨天**。昨日報告已存在 → 防覆寫跳過 → 排程每天綠燈但什麼都沒產（靜默空轉，比紅燈更難發現）。首跑前人工讀 workflow 攔到，未實際發生。
- **對策**：任何排程任務裡的日期都顯式計算時區（`TZ=Asia/Taipei date +%F`）再傳參，不讓腳本吃預設值；「跑了」與「產出了」是兩件事，驗證要看產物不是看綠燈。
- **硬化狀態**：未硬化（單例）。既有防線可兜住後果：daily 斷更 3 天會被 health.yml 巡檢抓到。
- **發生什麼**：repo 工程全綠（CI ✅、決策全拍板），但 daily brief 只產過一次。工程完成度掩蓋了「產線停擺」的事實。
- **對策**：`repo_health.py` 新鮮度檢查讓停擺可見；agent 每次開工先跑 health（見 `CLAUDE.md`）。
- **硬化進度（2026-06-10）**：「警告無人看見」的環節已硬化（health.yml 排程巡檢 + 自動 issue，見上方）。**仍在觀察**：daily 排程 6/10 才開、issue 機制是否真的讓警告被處理——若 repo-health issue 開著超過兩週沒動作，回到原判斷：修產線或承認 daily 改 weekly。

### Windows 終端機 cp950 編碼
- 所有腳本已加 `sys.stdout.reconfigure(encoding="utf-8")`；新腳本記得照抄，CI 端配 `PYTHONIOENCODING: utf-8`。PowerShell 5.1 的 `Get-Content` 讀 UTF-8 檔會亂碼，讀檔用支援 UTF-8 的工具。
