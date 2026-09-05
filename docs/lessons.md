# Lessons — Style Superman 教訓簿（Self-Evolution Loop 的 Learn 層）

> 這裡記「犯過的錯、踩過的坑、與對策」。規則升級路徑：
> **soft note（記在這）→ 反覆出現 → 硬化成 `validate_repo.py` / `repo_health.py` 檢查或文件硬規則。**
> 不要一犯錯就直接加規則；也不要讓同一個坑踩第三次。
>
> 每條格式：日期 · 發生什麼 · 對策 · 硬化狀態。
> soft note 可標 `- **重演**：N｜已硬化：<檢查或文件規則>` 或 `｜未硬化`；`repo_health` 對 Soft notes 裡 N ≥ 3 且未標已硬化的印「該硬化了」（D40，2026-09-03）。只認顯式標籤、沒標＝0、不溯及。

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

### 2026-06-14 · 把「管線桶子有什麼」當成「世界上什麼紅」（頭部交白卷）
- **發生什麼**：擁有者在對話問「6 月 head-to-toe 什麼最紅」，我只把 RSS 收到的 420 則訊號按關鍵字分桶，回報「🧢 頭部最薄、基本沒源」當交差——還拿「沒帽源」當理由。但這是 ad-hoc 對話、手上有 WebSearch / WebFetch，查男帽 / 男士眼鏡 6 月趨勢 30 秒就有（事後補做證明每格都填得滿）。本質錯誤：**把工具（RSS 管線）的覆蓋當成答案的天花板**，把基礎建設（找來源）做很多、產品（情報本身）卻交白卷。擁有者直接質疑「這是世界前三名 AI 的成果?」。
- **對策**：回答「什麼最紅 / head-to-toe / 月度回看」是分析師工作，用盡所有工具；管線某格薄是「主動去查」的訊號，不是「回報空白」的藉口。
- **硬化（即時，擁有者「寫進去」）**：`CLAUDE.md` 立「管線是底盤，不是答案邊界」節（治理對話 ad-hoc 行為，這條才擋得到沒走 prompt 的場景）；`prompts/weekly_buy_picks.md` + `prompts/monthly_heat_report.md` 加「某格可信訊號 < 3 條必須主動 WebSearch/WebFetch 補滿才出稿，禁止回報該區無源交差」。

### 2026-08-21 · 下游查得很細、上游沒查（同一窗三犯 → 升級為 E5）
- **發生什麼**：三則結論的下游都驗得很紮實，前提卻沒驗。① CONVERSE ALL STAR POINTEDTOE ¥10,450 的價格／發售日／完售狀態全用資料層驗過，沒開尺碼表——商品 tag 是 `WOMENS`、上限 26.0cm，擁有者穿不上，整條情報歸零。② Polo Ralph Lauren 트윌 재킷 被寫成「量化背書最硬」，三天後名次 #1→#14 而累計銷量 1.9 천개 一件未增；同期 North Face 벤투스 온 折扣一收（226,100→238,000 원）立刻掉出 TOP100、商品未下架未完售——名次是折扣租來的。同窗另把 패딩팬츠 當外套算進「一條線吃三個名次」。③ YOKE 被判「官方站密碼牆、讀不到」，實際 `yoke-tokyo.com` 是舊網域，現行官方站 `yoketokyo.com` HTTP 200 正常——假的不可讀。
- **對策**：下結論前先問「這條訊號要成立，有什麼前提我還沒驗？」具體三問：**尺碼／性別分類涵蓋得到嗎**、**名次有沒有配銷量增量與折扣率**、**這個網址是不是該品牌現在在用的**。
- **硬化**：已寫入 `prompts/region_reader.md` 的 **E5**（文件硬規則，非機器檢查）。**破例即時硬化的理由**：CLAUDE.md 要求「先 soft note、反覆出現才硬化」，而這三則是**同一個形狀在同一窗內三犯**，遞迴條件當場滿足，故直接立法而非等下次。**未寫成 code 的理由**：過三層自問——lint／test 擋不到（要判斷的是「該問而沒問」）、schema 也約束不了（尺碼與折扣不在 reader 契約內），只有文件規則做得到。E1–E4 防「把渲染當資料」，E5 防「問題問得不夠上游」，兩者不重疊。

## Soft notes（觀察中，尚未硬化）

### 2026-06-23 · scan reader 用 Explore 派工會查不了網（dogfood D28 抓到）
- **發生什麼**：D28 為了「工具層擋掉 reader 寫檔」把多區 scan reader 指定用 **Explore** subagent。實跑當天 daily 時，4 個 reader 裡 **US-EU 的 Explore 直接拒做**：自稱「我是 code 搜尋工具、沒 web、唯讀、fashion 超出範圍」，回 0 資料；JP/lane 勉強回了但品質參差。對照組——同日改用 **general-purpose** 補跑 US-EU/KR，兩個都正常 WebSearch/WebFetch、回滿可查證 JSON。根因：**Explore 自我定位是 codebase 搜尋，不可靠地做外部 web research**；用它換 no-Write 保證 = 換來「讀不了網的 reader」，違背 reader 本職。
- **對策**：scan reader 改用 **general-purpose**（能查網）；**no-Write 改由 reader prompt 規範**（`prompts/region_reader.md` 明寫「不可寫檔、不呼叫寫檔工具」）而非靠 agent type 工具層強制。其餘 cookbook 紀律（output_schema、防注入、單一 writer、auditor）不變。已改 `prompts/region_reader.md` / `prompts/daily_scan_orchestration.md` / `data/scan_units.yml` 的 roles。
- **硬化狀態**：未硬化（單次、prompt 層修正即可）。教訓通則：**選 subagent type 要看它「肯不肯做這類任務」，不是只看工具權限**——工具層保證再漂亮，agent 拒做就是 0。

### 2026-06-18 · 新時尚源評估：權威 ✓ 不是門檻，cadence + RSS 可解析才是
- **發生什麼**：擁有者問「能用的好源是不是找完了」。評估兩個對其品味（日系 elevated/古著）最對的候選——**Die Workwear**（Derek Guy）與 **Sabukaru**。兩個權威都滿（D18 gate ②），但都退：Die Workwear 部落格最新文 2025-11-28（7 個月前、約季度更一次，即時產出全在 X）→ 敗 gate ①（近 30 天持續產出），`/feed/` 實測用 `parse_feed` 解析 0 則；Sabukaru 內容週級新鮮但**全無可用 RSS**（`/feed`、`/rss`、`?format=rss` 全 404，只有 10MB sitemap）→ 進不了只吃 RSS 的管線。
- **對策**：評估新源**先過「實用門檻」再談權威**——① 近 30 天 cadence（用 repo 自己的 `parse_feed` 抓 feed 看實際 pubDate，**不只信 WebFetch「looks active」**）② RSS 能被 `parse_feed` 解析出 ≥N 則。好源常敗在這兩關（stale / no-RSS），這正是它們不在 repo 的原因。**結論：RSS 源層已成熟**；剩缺口（X-only 權威、無 RSS 新站、IG、古著店/拍賣）屬非管線 territory，走臨場 WebSearch/WebFetch（合 D20、反熵 D7），不擴常設源。
- **硬化狀態**：未硬化（評估方法 soft note）。若「該不該加源」反覆被重議或評估再現同模式，候選硬化：把「D18 候選自動跑 `parse_feed` cadence + 可解析」做成小驗證腳本。

### 2026-06-16 · liveness 跑在 Actions 美國 egress，韓源偽死（本機台灣可達）
- **發生什麼**：把 `--liveness` 死源偵測塞進 `health.yml` 週期巡檢後首次跑（`workflow_dispatch` 驗證），報 3 死源 `gq-korea` / `w-korea` / `vogue-korea`（全 `unreachable`）並開了 `repo-health` issue #122。但這 3 個韓站對擁有者本機（台灣）是**可達的**——同日 06-16 的深度日報就收到它們的訊號（gq-korea 微品牌錶、w-korea 西裝穿搭、vogue-korea 白裙）。根因：liveness 跑在 **GitHub Actions（美國 egress）**，真實產線卻是**本機（台灣）**，韓國站對美國 runner 連不到、對台灣可達＝**Actions 視角的偽陽性**。`reddit-techwear` 的 429 則是真限速（已正確歸「非死源」、不觸發 issue）。
- **對策**：liveness-in-health.yml 報的死源是「Actions 美國視角」，**韓/日源報 `unreachable` ≠ 本機產線收不到**——撤源前一定先在本機 `python scripts/repo_health.py --liveness` 複核（本機台灣才是真實產線視角）才算數；撤源/換域名仍是內容判斷（D17 式），別照 Actions issue 直接撤。
- **硬化狀態**：未硬化（單例觀察）。若反覆誤判，候選硬化：① liveness 對 `region: kr/jp` 的源標「Actions 視角，需本機複核」註記；② 或改 liveness 不在 health.yml 自動開 issue（降 run summary），避免地理偽陽性噪音。先觀察 issue #122 這次怎麼收。

### 2026-06-13 · 沒讀過原文就寫「為什麼推薦」：roundup 進來只有標題
- **發生什麼**：daily brief 把 Vogue Korea「一條牛仔褲指南」只寫成「夏季丹寧指南」，沒給任何品牌——擁有者問「你都給我這題目了，為什麼不給確切哪些品牌？要有確實讀完才能知道為什麼推薦」。根因在管線：`collect_raw_signals.py` 只抓 RSS 標題＋短摘要、不抓內文，listicle/roundup 到寫手手上本來就是空的，寫手卻照樣補了「對我的意義」＝沒讀就推薦。
- **對策（已落地，本次 PR）**：`prompts/daily_trend_brief.md` 立「推薦的證據門檻」——進推薦位（For Me 值得入手）或寫「對我的意義」前要讀過原文，簡介行必含至少一個原文事實（價格/型號/材質/發售日/具體主張）當「讀過的證明」；清單型報導要 fetch 原文挖出 top 4–6 品牌；讀不到具體事實的降到訊號層報標題＋待查，不准編「為什麼」。
- **硬化狀態（2026-06-14 更新：再犯一次 → 已硬化）**：2026-06-14 試跑時 roundup 又留「待挖」空殼,擁有者二度反映「roundup 一定要挖出 picks」。依「反覆出現才硬化」原則,**已硬化（prompt 規則層）**：roundup 一律 WebFetch 挖 picks 才能列、挖不到整條不列;並實測 26 源 crawler 可讀性,7 個封鎖源（gq/esquire/bof/sneakernews/drapers/wwd-japan/put-this-on，多 403）在 `data/sources.yml` 標 `body_fetchable: false`,prompt 看旗標直接不列其 roundup（確定性,不靠寫手自覺）。原候選 (a) collect 抓內文：封鎖源連 collect 也抓不到,故改走「標記 + 不列」;(b) validate gate 暫不加（roundup 在 reports/、不在 validate scope）。
  - **追記（2026-09-05）**：上面那份「7 個封鎖源」清單**已於 D36／#202（2026-07-28）作廢六個** —— 本機複驗 gq / esquire / bof / drapers / put-this-on / wwd-japan **全部 200、正文與價格齊全**（詳見本檔 2026-07-28「同一個『視角』錯誤修好一條軸、卻留在另一條軸上 44 天」）。2026-09-05 實測 `data/sources.yml` 全庫 `body_fetchable: false` **只剩 1 個：`sneakernews`**。⚠️ **不要從這一段抄那六個名字** —— 跳過清單只能從 `sources.yml` 推導、不得手打（D40，orchestration Step 1）。
  - **2026-06-20 更新（D22）：「封鎖源直接不列」改為「先試 Firecrawl」**。Firecrawl keyless（免 key、1000 credits/月）平行試用勝出——實測 GQ「20 Best New Menswear」WebFetch 硬失敗、Firecrawl scrape 200+結構化抽 17 picks（價格對得上原始 markdown、grounded）;wwd-japan 同樣 200。落地走**對話端 MCP**（`.mcp.json` keyless,不進 Python 腳本 → 不破輕依賴/D5/D16/D21）。封鎖源 roundup 不再無腦丟,先 Firecrawl scrape（schema 結構化抽取,plain 1 credit / json extract 5 credits）,真挖不到才不列。Akamai 級即時榜（ZOZO/KREAM/MUSINSA 逐位）未測、不宣稱解決。production 自動化量級要自帶 key。

### 2026-06-11 · 排程 workflow 的「今天」是 UTC 的今天
- **發生什麼**：daily-brief 排程設 UTC 23:00（＝台灣 07:00）跑，但腳本不帶 `--date` 時用 runner 本地日期——UTC 23:00 的「今天」是台灣的**昨天**。昨日報告已存在 → 防覆寫跳過 → 排程每天綠燈但什麼都沒產（靜默空轉，比紅燈更難發現）。首跑前人工讀 workflow 攔到，未實際發生。
- **對策**：任何排程任務裡的日期都顯式計算時區（`TZ=Asia/Taipei date +%F`）再傳參，不讓腳本吃預設值；「跑了」與「產出了」是兩件事，驗證要看產物不是看綠燈。
- **硬化狀態**：未硬化（單例）。既有防線可兜住後果：daily 斷更 3 天會被 health.yml 巡檢抓到。
- **發生什麼**：repo 工程全綠（CI ✅、決策全拍板），但 daily brief 只產過一次。工程完成度掩蓋了「產線停擺」的事實。
- **對策**：`repo_health.py` 新鮮度檢查讓停擺可見；agent 每次開工先跑 health（見 `CLAUDE.md`）。
- **硬化進度（2026-06-10）**：「警告無人看見」的環節已硬化（health.yml 排程巡檢 + 自動 issue，見上方）。**仍在觀察**：daily 排程 6/10 才開、issue 機制是否真的讓警告被處理——若 repo-health issue 開著超過兩週沒動作，回到原判斷：修產線或承認 daily 改 weekly。
- **結案（2026-06-14，D16/D17）**：「daily 改 weekly」的觀察有結論了，但走的是**第三條路**——daily brief 改**對話觸發、不入 `reports/daily/`**（D16）。既然產出不存檔、無檔可監控，`repo_health` 的 daily 斷更檢查（`check_daily_freshness`）與 `DAILY_STALE_DAYS` 一併移除；health.yml 巡檢改只盯週挑/月報/一致性/守衛/產出契約，**不再是 daily 的看門狗**。⚠ 上方 2026-06-10 條描述的「daily 斷更看門狗 / daily-brief.yml 排程」機制**已不適用**（保留原文為歷史記錄）。
- **硬化（2026-06-26，D16/D7）：純文件規則擋不住，daily 被 commit 進 master 連四犯 → 加 gate**。D16「daily 不入 `reports/daily/`」只寫在文件、沒有機制執法 → 平行 session 走舊存檔習慣把整份 brief commit 進去：**06-23（rogue routine，已刪）+ 06-24/06-25/06-26（平行 session 開 PR、擁有者每次手動 merge）連四犯**，每次都要人手動發現+移除。反向驗證收穫：第一反應喊「rogue routine 復活」，查 `RemoteTrigger list` → 零 routine，**真因是規則沒長牙齒、不是有人惡意**。達「反覆出現才硬化」門檻後，`validate_repo.py` 加 `DAILY_FREEZE_CUTOFF=2026-06-16`：之後的 `reports/daily/*.md` 一律 CI 紅（歷史 ≤06-16 grandfathered；flash 不在此列）。擁有者定調：**「我要的就是單純看，喜歡的自己記」**——daily 是用來讀的、不是用來存的（要存喜歡的單品走候選池/週挑，不存整份 brief）。教訓：**「文件寫了」≠「擋得住」；反覆違規且對策穩定，就該從散文升級成 gate（警告必配修復）**。

### Windows 終端機 cp950 編碼
- 所有腳本已加 `sys.stdout.reconfigure(encoding="utf-8")` **及 `sys.stderr.reconfigure(encoding="utf-8")`**（2026-06-24：原本只設 stdout，argparse 的中文錯誤訊息與 `print(file=sys.stderr)` 警告走 stderr，在本機 cp950 仍亂碼／smoke 測試 capture 時 UnicodeDecodeError）；新腳本記得兩個都照抄，CI 端配 `PYTHONIOENCODING: utf-8`。PowerShell 5.1 的 `Get-Content` 讀 UTF-8 檔會亂碼，讀檔用支援 UTF-8 的工具。

### 2026-06-15 · 設定在的 RSS 源默默 403、躲在「N 個 RSS」數字裡沒人發現
- **發生什麼**：擁有者要我跑沒用過的功能找問題，dogfood `collect_raw_signals` 進料口（這 session 從沒真連網跑過），發現 3 個 reddit 源（malefashion / techwear / Sneakers）的 `rss:` 指向 `www.reddit.com/*.rss`——reddit 2023 API 封鎖後該域一律 403。collect 對抓取失敗「優雅降級」（跳過 + 印 warning），所以這些源**每次跑都默默回 0**，卻照樣被算進 README/repo_health 宣稱的「31 個 RSS」。實際能收的是 28，宣稱 31。同 Mercari（D17 陳貨）一個本質：**宣稱覆蓋 ≠ 實際覆蓋**，而降級設計讓它永遠無聲。
- **對策**：① `rss:` 改 `old.reddit.com`（該域仍開放，實測各收 25 則；`url:` 人點連結維持 www）；② reddit 對 bot 連續請求限速兇 → `fetch_feed` 加 429 退避重試一次（reddit 自己要求的禮貌）；③ **403（永久死）≠ 429（活著被限速）**——除錯時一定要分清：我自己一天狂測把 reddit 打到 429，差點把「活源被我限速」誤判成「死源該撤」，靠長 cooldown + 間隔的 ground-truth 測試（各收 25 則）才確認是限速不是死。
- **硬化（擁有者選「修好 + 加死活檢查」）**：`repo_health.py --liveness` 連網打每個 `rss:`、回報實際收得到料的比例 + 點名死源，且**把 429 單獨標「限速（非死源）」不混進死源**（這個分類就是被上面的誤判教出來的）。刻意 opt-in、不入 CI `--strict`（需外網、外站抖動會讓 CI flaky）。這檢查上線當下就立刻抓到我漏改的第 3 個源（reddit-sneakers），證明值得留。
- **注意**：`--liveness` 自己會連打 reddit → 跑完它再馬上跑會看到 reddit 顯示 429（限速），那是檢查工具自身的副作用、不是源死了；要判死活看「長 cooldown 後單發」而非「剛跑完 liveness 的結果」。

### 2026-06-15 · 工具吃單一趨勢、使用者給一整季（trend_analysis 範圍落差）
- **發生什麼**：擁有者下「男性秋冬穿搭趨勢」跑 `trend_analysis`，但該工具產的是**一張**單一趨勢卡（「定義」要一句話說清楚是什麼），一整季有 7–8 個趨勢、塞不進一張卡。本次靠「先研究 AW26 → 收斂成最定義性的單一趨勢（廓形收窄）→ 給選項讓擁有者挑」臨場補上，沒交白卷也沒硬塞。
- **對策**：收到「一季 / 品類大盤 / 廣主題」時，先收斂成最定義性的單一趨勢並回報理由（理解錯比挖錯更糟）、或建議改用月報（多趨勢全貌工具），不硬塞一張卡。同精神於 brand_radar 是「先複述對關鍵字的理解」。
- **硬化狀態（擁有者選硬化）**：已寫進 `prompts/trend_analysis.md` 開頭「範圍門檻」。屬首次發生即硬化（擁有者拍板），非反覆出現——若此規則上線後沒再撞到同類落差即視為足夠，不再加碼。

### 2026-07-03 · KR 月榜搜尋反覆吃到「去年同月」舊報告（連 5 次）
- **發生什麼**：每日 KR reader 搜 MUSINSA / KREAM「6월 월간 랭킹」時，WebSearch 反覆回傳 **2025 年 6 月**的舊月報當成當期（`제로 스웨트팬츠 3개월 연속 1위`／`아디다스 삼바 OG`／`필루미네이트 데님`＝2025-06 內容；URL `musinsa.com/content/1388075929845500921` 也是 2025）。若照單全收會把去年榜寫成「今年在紅」。06-24～07-03 連 5 天每天靠 orchestrator **臨場在 reader 派工指令裡提醒「驗年份」**擋下——但那條規則**只活在每天的 ad-hoc prompt、沒進持久檔**，換個 session／我忘了提就會破。
- **對策**：採用任何 MUSINSA/KREAM 月榜前，必先 WebFetch 原文確認「집계 기간」年份＝當年；不是當年就當缺口、明寫「當期未發行」，不把舊年度當當期。
- **硬化（2026-07-03，D7）**：反覆 5 次 + 對策穩定，達門檻 → 從「每天臨場提醒」寫進持久檔 `prompts/region_reader.md`（KR 骨幹源那條下方）。教訓：**一條「每天都要交代一次」的臨場規則＝還沒優化的漏；反覆用到就該搬進持久 prompt，別靠記性續命。**

### 2026-07-03 · `--liveness` 死源清單反覆偽陽性——真因是「探測視角」，不是對面死了
- **發生什麼**：patrol（每週一・四排程）的死源清單三次三組、互不重疊：06-16=KR 三源（unreachable）、07-02=bof(403)/heddels/permanent-style(empty 200)。每組都被當死源開出／追評 issue #122，「死源」清單分不出真死 vs 誤報、失去可信度（liveness 帶 `|| true`、死源不弄紅 job——7/2 job 紅是 strict/Lyst，見 D31；死源的破壞是**污染 issue 清單**、下一步就是被 D17 誤撤源）。
- **病因（兩組事後都查明、都不是瞬斷）**：① 6/16 KR 三源＝Actions 美國 egress 地理不可達（本頁 2026-06-16 節）；② **7/2 三源＝自報身分的 bot UA（StyleSupermanBot/0.1）被 WAF 擋**——#177 實彈驗證同 URL 換瀏覽器 UA 即回滿 RSS（120KB/18KB/394KB）。且封鎖是**間歇的**：7/3 同在本機、同 bot UA，早上探測全過、稍後實測被擋（同視角不同結果）——症狀因此長得像瞬斷，一度誤讀成「瞬斷已自己恢復」。
- **對策 / 硬化（兩層，2026-07-03）**：① **UA 改 reader-grade 瀏覽器 UA**（#177，改 `collect_raw_signals.UA`，probe 同源引用）——公開 syndication feed 用閱讀器級 UA 屬正常使用；② `check_source_liveness` 對 dead/empty/unreachable 隔 2s 重打一次、二次仍非活才定讞（D32）——防真瞬斷（DNS 抖、暫時 5xx），**治不了 UA/地理這類探測視角問題**（間歇 WAF 時擋時放，重試偶爾矇過反而讓死源清單時紅時綠、更像抽風——對症解是換 UA，不是重試）。
- **教訓**：**連網探測報死，第一嫌疑人是自己的探測視角（egress 地理、UA、IP 信譽），第二才是對面真死**；撤源（D17）前必本機複核＋換 UA 複核。與「跑了≠產出了」同族系：探測器說死 ≠ 源死了。（本節 2026-07-03 深審訂正：初版把兩組誤診成「瞬斷、下次自己恢復」，D32 決策的背景段有同步追記。）

### 2026-07-28 · 同一個「視角」錯誤修好一條軸、卻留在另一條軸上 44 天（body_fetchable 六源假陰性）
- **發生什麼**：daily brief 交付時把 PS 棉西裝評測、GQ 亞麻襯衫 13 選、drapers 收購案三條**整條不列**，理由「WebFetch 403 + Firecrawl 沒掛上」。本機複驗七源：gq / esquire / bof / drapers / put-this-on / wwd-japan **全部 200、正文與價格齊全**（PS $3,800、GQ $120/$90/$50…），只有 sneakernews 真 403。**七個裡六個是假陰性**，且旗標是 2026-06-14 標的、錯了 44 天。
- **病因**：`body_fetchable` 把「(源 × 探測視角) 的量測結果」寫成「源的永久屬性」。而 **repo 早就在 RSS 死活軸修好同一條**（#186 四次誤殺 → #193 視角感知分類：`403＝blocked＝活著但拒收本視角，永不判死`）——正文抓取軸沒跟上。更早的 #177（2026-07-03）換 UA 時只改了 collect 的 UA，**沒回頭複驗依賴舊視角量出來的旗標**。
- **對策 / 硬化（D36，2026-07-28）**：① 新增本機 `scripts/fetch_article.py`（純機械、零 LLM），取內文順序改「本機 → WebFetch → Firecrawl → 才不列」；② `body_fetchable` 判定視角正名為**本機**，標 false 必須附 `body_fetch_note`（本機實測日期＋現象），`validate_repo.check_sources` 擋、`test_smoke` 9i-2 反向鎖。
- **教訓（兩條）**：**①「量出來的旗標」要連同量測視角與日期一起存**，否則它會以「事實」的身分活下去，沒人知道何時該複驗。**② 修好一個概念性錯誤時，要橫向掃還有哪幾條路徑犯同一個錯**——#193 修 liveness 那次沒問「還有誰把 403 當永久事實」，代價是六個源被封 44 天、三條有價情報當天被丟掉。第三個附帶教訓：**寫在文件裡的備援（Firecrawl MCP）不等於執行環境有**，宣告備援時要標「不保證掛得上」。

### 2026-08-04 / 08-06 · CIOTA lazy-load 佔位圖被判成停更
- 官網商品圖全呈現 `dummy.jpg` 就被判「站掛了／品牌停更」；對照 2019AW 與 2026SS 同樣渲染 `dummy.jpg`，才確認是 Shopify lazy-load 佔位圖。
- 教訓：渲染結果不是資料本身；負面結論先用已知有料的同型頁跑對照組。

### 2026-08-11 · KR「讀不到」被靜默升級成「已死」
- 回報六個釘選來源死三個，實際僅 isplus.co.kr 可驗證為死；l'officiel Korea 是 HTTP 200 但無法解析日期，gqkorea 與 whatsonthestar 根本沒驗。
- 教訓：無法讀取只代表不下結論；未讀目標與原因必須進 reader JSON，不能讓 orchestrator 看不見。

### 2026-08-15 · A.PRESSE hidden 完售標記被文字化成全頁完售
- 每張商品卡都渲染 Sold out 元素，文字擷取洗掉 `hidden`；原始 HTML 16 個元素中 6 個帶 `hidden`，實際 8/8 那波 17 型中 10 型完售，非該頁九型全數售罄。
- 教訓：判讀完售看原始 HTML 與可見性屬性；「全部完售」前先跑同版型對照組。
- **重演**：3｜已硬化：`prompts/region_reader.md` E1/E3 操作註記＋「逐 variant 抓法」段（08-15 A.PRESSE → W35 Graphpaper → 08-29 AURALEE；文件硬規則——機器驗不到 reader 怎麼讀頁）

### 2026-08-29 · `curl -L` 的重導把「站可讀」量成「站不可讀」（AURALEE，E2 的新變形）
- **發生什麼**：上一窗把 auralee.jp 判成「自建 SPA、`products.json` 404、`sitemap.xml` 404，**所有路徑（含不存在的）都回同一個 95,663 bytes 殼**，HTTP 層分不出真頁與 404，只能靠會渲染 JS 的工具」，並據此把該品牌所有數字降級為「證據等級低於其他日系項」。本窗**關掉 `-L` 重測**：不存在的路徑回 **404 / 77,127 bytes**、`/item` 回 **200 / 170,003 bytes**——HTTP 層分得一清二楚。那個「同一個殼」是 `curl -L` 跟著 3xx 走回首頁的產物。
- **而且站根本不是 SPA**：jQuery + `assets/front/js/`，頁內直接內嵌 `var item_stock = {...}`（逐色逐碼含 `stock` 整數）與 JSON-LD `schema.org/Offer`（`priceCurrency` / `price` / `availability`）。整站可純 curl 逐 variant 複核，不需要任何會渲染 JS 的工具。
- **教訓**：**探測參數是量測視角的一部分**。`-L` / UA / cookie / Accept-Language 任一個都能製造出「站壞了」的假象，跟 #186（UA）、#193（403）、E5（找錯網址）是同一族錯誤的第四個變形。判 `unreadable` 前，**至少要有一次不跟隨重導、且比對過「已知不存在路徑」的對照組**——兩者回傳大小相同才是真的分不出。
- **附帶**：本窗同時確認 sold-out 樣板元素陷阱在 AURALEE 重演（第三站）——`SOLD OUT` 全帶 `style="display:none"` / `class="hide"`，文字化必誤報完售。E1/E3 操作註記已補。
- **重演**：5｜已硬化：E2 操作註記「不跟隨重導＋不存在路徑對照組」＋ `docs/rankings.md` 逐檔實測狀態（#186 UA → #193 403 → D36 body_fetchable → 08-29 `-L` → 09-03「Firecrawl MCP 未接＝補不動」）
- **第 5 變形（09-03，硬化後又犯，因為上一輪硬化太窄）**：08-29 把規則寫進 `prompts/region_reader.md`（reader 怎麼讀網頁），但**沒覆蓋「文件裡的能力宣稱」**——`docs/rankings.md` 差點寫進「KREAM/MUSINSA/SNKRDUNK 只有接得到 Firecrawl 的環境才補得動」。兩層錯：① **`Firecrawl MCP 未接` ≠ `Firecrawl 不可用`**，keyless REST 從 bash 直接 curl 即可（免 key/免 MCP/免重啟，memory `firecrawl-keyless-blocked-sites` 早有記載）；② **MUSINSA 連 Firecrawl 都不需要**，官方 JSON 榜純 curl 回 200/588KB、101 筆帶 rank/價/折扣/完售。逐檔實測後只有 KREAM 真的打不到（HTTP 500）。→ **教訓:「某某補不動」是能力宣稱,和「某站讀不到」同一個東西;寫進任何文件前都要附實測日期與指令,否則它會以事實的身分活下去。**

### 2026-08-29 · 電商站的顯示幣別跟著訪客走，不是站的屬性（第三站重演）
- **發生什麼**：auralee.jp 商品卡顯示 `$1,287.00` / `$737.00`，頁內 `<input id="currency_input" value="USD">`，即使帶 `?lang=ja` 仍是 USD；真價要從同頁 JSON-LD 取（`priceCurrency: JPY, price: 99000 / 55000`）。這與 8/15 A.PRESSE（無 cookie 時 `110000` 是 **$1,100 USD** 不是 ¥110,000）、以及 OUR LEGACY（Centra 各市場獨立定價，€230／€190 對應 ¥52,800／¥42,900）是同一件事。
- **教訓**：**看到價格先問「這是哪個市場的價」**。三個站三種後台（自建 / Shopify markets / Centra）都是各市場獨立定價、非匯率換算，所以「換算回來對不上」不代表數字錯。反向也成立：**同一個乘數在同批兩個品項上都成立，就是該站的市場定價，不是誰換算錯**（本窗 €230→¥52,800、€190→¥42,900 皆 226–230，據此判定日圓價可信）。
- **重演**：3｜已硬化：`region_reader.md`「逐 variant 抓法」各後台的幣別註記（08-15 A.PRESSE → 08-29 AURALEE → OUR LEGACY）

### 2026-08-29 · 有了框架卻沒拿它驗自己的清單（OUR LEGACY × Dickies 被放錯格）
- **發生什麼**：W35 週挑的「本週最該記住」寫的是 **「原型 × 限量投放 才會動；只有其一都不動」**，反例明寫 LVC 1947 501（原型純度最高卻零缺碼，因為常在架、非一次性投放）。同一份報告卻把 OUR LEGACY WORK SHOP × Dickies 放進上身推薦位，理由是「Eisenhower 與 874 都是有名字的原型——這正是本週在動的那一類」，並自承「未逐 variant 驗庫存」。本窗補驗（Centra `__NEXT_DATA__` 逐碼）：Eisenhower 三色 868 件、874 三色 937 件，**合計 1,805 件 web 倉在架**，擁有者的 L 與 W34 每個色都是數十件起跳，只有 XXL 與 khaki 31 缺。**它是那條規則的反例，不是例證。**
- **教訓**：**規則寫出來不等於套用過**。當一份產出同時包含「判準」與「清單」，收尾時要拿判準回頭掃一遍自己的清單——尤其是那些被標「未驗」而仍然進了推薦位的項目。**「未逐 variant 驗庫存」＋「因為在動所以推薦」同時出現，本身就是矛盾**：沒驗庫存就不會知道有沒有在動。

### 2026-08-29 · 已硬化的教訓沒被套進「我自己臨場寫的派工清單」
- **發生什麼**：W35 窗內把 SoleRetriever 與 Permanent Style 寫進 reader 派工 prompt 的「已知讀不到」清單，理由是 WebFetch 403。實測瀏覽器 UA curl 兩站皆 HTTP 200 全文可讀——**403 是單一視角造成的**，正是 repo 早在 #186 / #193 / D36 就硬化過的那條。防線擋得住 `data/sources.yml` 的 `body_fetchable` 欄位，擋不住我在對話裡臨時打出來的一句「這兩個讀不到，別派」。
- **教訓**：**硬化只保護有 schema 的欄位，保護不到臨場產生的指令**。派工 prompt 裡每寫一句「某某來源讀不到／跳過」，都等於在建立一個沒有日期、沒有視角標註、不會被任何檢查複驗的旗標——與 D36 明令要根除的東西完全同型。**要嘛當場實測後才寫，要嘛不要寫。**

### 2026-08-29 · 「星期幾＋日期」的發售情報要回推年份
- 搜尋引擎會浮出 ATON「July 18(Fri) / August 8(Fri)」這類發售資訊，但那兩個星期幾對應的是 **2025 年**、不是 2026。同族案例：MUSINSA `content/mz/30014`「8월 5주차 주간 랭킹 TOP 10」實為 **2019.09.03** 舊文；月榜 `/ranking/archive` 在當月未結算時顯示「판매중인 상품이 없습니다」，讀了就會掉回上一個已結算年度。
- **教訓**：看到「星期幾＋日期」先用日曆回推年份對得上才採用；讀排行榜前先確認**該期已結算**，未結算的期間會靜默給你去年的資料。

### 2026-08-29 · 四個「零測試區」的突變掃描結果（勿重掃）
- **掃了什麼**：20 個探針打 `repo_health` 的 Lyst 季度數學與週差、`generate_flash` 的去重與截斷、`collect_raw_signals` 的 Atom 分支、`fetch_article` 的 `MIN_BODY_CHARS` 邊界。**掃前殺率 30%（殺 6 / 存活 14）。**
- **最嚴重的兩個存活**：`behind` 正負反轉會讓 repo_health 印出「Lyst 快照落後 **-1** 季」、當季 index 少一個 `+ 1` 會印「落後 **0** 季」——兩者都是使用者直接看到的數字，且整個測試網沒有一條會變紅。既有 lyst 測試只斷言 level 與字串、從不看那個數字。
- **補了 6 條測試後殺率 85%（殺 17 / 存活 3）**，且**存活的 3 個全是「門檻值釘」探針**（`LYST_PUBLISH_LAG_DAYS` 45→46、週挑落後 2→3、`MIN_BODY_CHARS` 200→201）。這是**刻意留的**：新測試把邊界語意從常數**推導**出來釘（「邊界當天仍在寬限內、隔天才警」），而不是把 45 這個數字寫進斷言——調參是調參，不該讓測試變紅；會漂掉的季末算法才該釘死。
- **教訓**：**殺率低的區塊，洞通常不在「有沒有跑到那行」而在「有沒有斷言那個值」。** Lyst 那段每次 `repo_health` 都會執行、coverage 是滿的，但沒有任何一條斷言碰過 `behind`——所以整段算術等於裸奔。挑探針時，**先問「這個函式輸出的哪個數字會被人讀到」，再去看有沒有測試釘住它**。

### 2026-09-03 · 迴圈量的是流程、不是判斷（三例同根，升級為 D40）
- **發生什麼**：08-29 一天抓到三個錯——SoleRetriever 被寫成死源、AURALEE 被判成 SPA、OL×Dickies 在同一份週挑裡先立規則三段後違反它——三條教訓**全早已在本檔**，卻在該用的那一刻沒出現。同時 Observe 層（`repo_health`）量的全是「機器活著沒」，沒有一個數字回答「上週說在紅的、還在嗎」；而那個數字每週都被手寫在候選池 ⚠️ 區塊，從沒被讀成指標。
- **對策 / 硬化（D40）**：① 週挑 header 帶「上週複驗：推薦／複驗／須更正」，health 印出；② 派工 prompt 的「跳過清單」只能從 `sources.yml` 推導、禁止手打；③ soft note 標 `重演：N`，≥3 未硬化 health 提醒；④ 雷達快照滿 90 天無 `-backtest.md` 提醒（D11 的扳機）。
- **教訓**：「有 Self-Evolution Loop」跟「迴圈在優化對的目標」是兩件事。硬化只保護有 schema 的欄位，保護不到對話裡臨時打的一句話——所以第二刀不是再加檢查，是**把那句話變成推導**。

### 2026-09-03 · 彙整站的價格欄可能整欄失真——用一個你已經知道的價去校準它
- **發生什麼**：寫 2026-09 歐美月報時，House of Heat 的九月發售月曆把 **Air Jordan 4 標成 `$84.60`、Air Max 90 標成 `$87.40`**（AJ4 公認零售約 $215–225）。日期欄與 WWD 月曆對得上、頁面結構正常、沒有 403 也沒有付費牆——**只有價格欄整欄是壞的**，成因未查明（疑似折扣／匯率欄誤取）。
- **教訓**：**發現一個來源某一欄不可信，不是修那一格，是整欄棄用。** 該站日期經第二路對上後仍可用，價格則一條都不採，寧可讓單品榜 3/5 格 `待查`。這跟 08-29「先問這是哪個市場的價」是同一族但不同刀：那條是**幣別**要問，這條是**欄位可信度**要驗——**引用彙整站的數值前，先拿一個你本來就知道正確答案的品項當校準器**（AJ4 零售價是常識級的錨），一格對不上就整欄不用。
- **重演**：1｜未硬化

### 2026-09-05 · E5 叫我「確認尺碼」，但沒防「手上那張對照表本身是錯的」
- **發生什麼**：W35 週挑（2026-08-29 封存）的 🎯 推薦位寫「AURALEE 上 5 下 4／上 5 下 5 兩種組合都買得到」，依據是候選池記的「size 4＝腰 86cm≈W34、5＝90cm」。2026-09-05 第一手抓官方尺寸表：**3=80cm(31.2in)／4=84cm(32.7in)／5=88cm(34.3in)／6=92cm(35.8in)**，且 SIZE CONVERSION 是 `3/4/5/6 = Japan Men S/M/L/XL`。→ **兩個數字都錯**（4 是 84 不是 86、5 是 88 不是 90），而且**擁有者的 W34 對到的是 size 5 不是 4**——「下 4」是 32.7 吋，他穿不下。那條推薦從發出去就是錯的。
- **為什麼 E5 擋不住**：E5（2026-08-21）立的是「引用單品前先確認尺碼／性別分類涵蓋得到擁有者」，防的是**沒去查**（CONVERSE POINTEDTOE 女鞋 26.0cm 上限）。這次**查了**，只是查的是候選池裡一句沒有出處、沒有實測日期的散文，而那句話本身是錯的。**「有查」與「查對」之間還有一層。**
- **對策 / 硬化**：`prompts/region_reader.md` 新增「已驗品牌尺碼對照」表（AURALEE／CIOTA／A.PRESSE／marka），逐碼腰圍＋擁有者對應＋**實測日期**，並註明 AURALEE 同一張表有日規與國際規兩列（看錯一列差一整號）、marka 官方未公開尺寸表故標 `待查`。同時立通則：**尺碼表是每個品牌各自的，不可跨品牌外推**（AURALEE 的 5 是 88cm、CIOTA 的 5 是 83cm）。
- **教訓**：**規則要求「確認 X」時，要一併指定「X 的權威來源在哪」**，否則執行者會拿手邊最近的一句話當權威——而那句話很可能是上一輪某個人憑印象寫的。散文裡的數字沒有實測日期就等於沒有出處。
- **重演**：2｜已硬化：`prompts/region_reader.md`「已驗品牌尺碼對照」表（08-21 CONVERSE 女鞋 → 09-05 AURALEE 尺碼制）

### 2026-09-05 · 把 A 榜的口徑坑貼到 B 榜上（MUSINSA 兩個榜被我合成一個）
- **發生什麼**：2026-09-03 我把 MUSINSA 商品榜端點（`api2/hm/web/v5/pans/ranking/sections/199`）寫進 `docs/rankings.md` 時，順手把候選池記的三個口徑特性——「판매액(營收)非件數／浮動七日窗／每週五 11:00 KST 刊」——掛在它身上。09-05 實測：那三條是**주간 랭킹 리포트**那條線的，section 199 是**另一個榜**：頁內 tooltip 自報 `매출, 조회수, 후기수를 반영한 상품 랭킹`＝**銷售額＋瀏覽數＋評論數混合**，`information.updatedAt` 顯示**每日 ~04:47 KST 更新**、且**不揭露日期範圍型的「집계 기간」，只給更新時刻**。
- **後果**：如果照原文寫月報，會把一個混合指標當成純營收引用，「名次高」被讀成「賣得多」——而這正是 E5 立法時要防的（Polo 트윌 재킷 #1→#14 但銷量零增）。
- **教訓**：**同一個平台可以有好幾個榜，口徑坑不會自動繼承。** 記端點時要連「這是哪一個榜」一起記；把舊筆記的注意事項搬到新端點上之前，先確認那些注意事項當初講的是不是同一個東西。

### 2026-09-05 · 拍板改了資料層卻沒接進程式，而測試把錯誤狀態釘死當契約
- **發生什麼**：D24（2026-06-21）用 SNKRDUNK 重建日本球鞋轉售量化板、`data/rankings/snkrdunk.yml` 也建好了，但 `generate_monthly_heat_report.REGIONS["jp"]["baselines"]` 一直是 `()`，而且它的註解引用的是 **D24 前一週（06-14）**的狀態。**後果不是骨架難看，是產出說謊**：`2026-08-jp.md` 與 `2026-09-jp.md` 兩份月報都白紙黑字寫「本區無可自動收的量化基準榜」「日本無量化基準榜是結構性限制」，而那個榜就躺在同一個 repo 裡、76 天沒人用。同一句話另外散在 `prompts/monthly_heat_report.md`（×2）、`prompts/brand_radar.md`、`docs/flow_calendar.md`、`scripts/README.md` 五處。
- **最惡的一層：測試站在錯誤那一邊**。`test_baseline_labels_and_movements_cover_regional_contracts` 硬斷言 `baseline_label(REGIONS["jp"]) == "無"` 與「jp 的 movement 含『無可自動收的量化基準』」。**任何人把 D24 接上去，這支測試就會紅、看起來像迴歸** —— 它不是沒擋住這個 bug，它是這個 bug 的保鑣。
- **對策 / 硬化**：① 接上 `snkrdunk.yml`，並在註解裡寫明它只覆蓋球鞋轉售、服飾／精品仍空；② 該測試改成測**函式契約**（用合成 region 測空/非空兩條分支），不再拿某地區當下的資料當斷言；③ 新增推導式守衛 `test_every_region_scoped_ranking_file_is_claimed_as_a_baseline` —— **從 `data/rankings/*.yml` 自己的 `region` 欄位推導**，凡是 region 對得上月報地區的檔都必須被那個地區認領，新增排行檔或改 region 忘了接就紅（不維護第二份手工清單，那正是會漂開的東西）。
- **教訓（兩條）**：**① 拍板要同時盤點「資料層／程式層／文件層／測試層」四邊**，D24 只做了資料層與 `docs/rankings.md`，其餘三層原地不動了 76 天。**② 斷言「某地區現在沒有 X」是把資料狀態寫進契約** —— 測試該釘的是函式在給定輸入下的行為，不是世界現在長什麼樣；否則修正世界的人會先被自己的測試擋下來。
- **重演**：2｜已硬化：`test_every_region_scoped_ranking_file_is_claimed_as_a_baseline`（2026-08-18 CI 寫死單檔導致新增測試永不執行的假綠 → 09-05 baselines 未接上的假限制）

### 2026-09-05 · 「四格」的結論先成立，價格才被找來填格（Graphpaper 兩套面料被合成一套）
- **發生什麼**：Graphpaper 8/22 那批**同時**鋪了 `Scale Off Wool` 與 `Wool Doeskin` 兩套面料，**各自都走完頭到腳**。W35 寫「同一塊 Scale Off Wool 走完頭到腳四格」時，把 **Wool Doeskin Jacket ¥92,400** 塞進 Scale Off Wool 的敘事——Scale Off Wool 的外套其實是 **¥77,000**（Double Jacket ¥81,400）。2026-09-05 實測 `products.json` 全站 218 型，價格 92400 的只有一支、tag 明寫 `Wool Doeskin`。錯誤汙染 W35 一則 + 9 月 jp 月報三處，含一整條挑買方向的價位帶。
- **根因**：報告在同一個 bullet 裡先正確地把 Doeskin 領帶標成獨立面料，隔兩句就把 Doeskin 外套的價格算進 Scale Off Wool 那條線。**「四格」這個敘事先成立了，價格才被找來填格**——填錯了也沒有任何東西會說話，因為沒人回去對 tag。
- **對策 / 硬化**：`prompts/region_reader.md` 新增「同一批貨 ≠ 同一塊布」段——Shopify 的 `products.json` 每個商品都帶 `tags`、**面料名就在 tags 裡**；要講「同一塊布走完幾格」就用 tag 篩、把該 tag 的全部型號列出來，不要憑價格湊。
- **教訓**：**敘事一旦成形，證據就會被挑來配合它。** 凡是「同一個 X 走完 N 格」這種形狀的結論，都要能列出那 N 格**共同的機器可讀欄位**（tag / 品番前綴 / 同一批 published_at）；列不出來就不是同一個 X。
- **重演**：2｜已硬化：`prompts/region_reader.md`「同一批貨 ≠ 同一塊布」段（08-21 BLACKYAK 把 패딩팬츠當外套算進「一條產品線吃三個名次」→ 09-05 Graphpaper 兩套面料合一）

### 2026-09-05 · 「我查不到」被寫成「查不到」——單一來源失敗被當成資訊不存在
- **發生什麼**：9 月 eu 月報判定 House of Heat 的價格欄整欄失真（AJ4 標 $84.60、Air Max 90 標 $87.40，與零售價差一個量級），**這個判斷是對的**。但接著推導出「唯一查得到價的來源已失真」，於是主動把單品榜 3/5 格留成 `待查`。實測：AM95「Greedy」**$200**、AJ4「Tour Yellow」**$220**、Pokémon×adidas **$110–180**、Mowalola AJ14 SP **$255**、Pharrell Jellyfish **$300** —— 全在 Complex / SneakerBarDetroit / SoleRetriever / SneakerFiles 等標準球鞋媒體上。同份報告還留下自證矛盾：某項寫「唯一在**兩路來源**都標到具體價…但該價來自已判失真的價格欄」。
- **教訓**：**「棄用某個來源」與「這個資訊不存在」之間沒有蘊含關係。** 判一個來源失真之後，正確的下一步是**換來源再查一次**，不是把留白當成誠實。這正是 `CLAUDE.md` 那條「管線收到什麼不是答案上限」在講的事——而它被寫成留白，看起來還很像紀律。
- **檢查點**：任何「查不到 → 標 `待查`」之前問一句：**我查了幾個來源？** 只查了一個就不是「查不到」。

### 2026-09-05 · 對封存快照做事後稽核，「現在不一樣」預設是時間差不是錯誤
- **發生什麼**：稽核 W35「YOKE Coverall 0/4、同料褲 6/6」時，今日實測是 **0/5 與 5/7**，看起來報告數錯了。追 `created_at` 才發現那兩個 `Black / 4` variant 是 **2026-09-04T15:33 / 15:36 才被建立的**——8/29 採樣時根本不存在。**報告當時是對的。**
- **教訓**：**稽核封存快照時，差異的預設解釋是「時間過了」，不是「當時算錯」。** 要把差異升級成錯誤，必須找到一個**不可竄改的時間欄位**（Shopify 的 `created_at` / `published_at`、Centra 的 `createdAt`）證明那筆資料在採樣當下就存在。沒有這種欄位的差異一律停在 ⚠️、不寫成 ❌ —— 否則稽核本身會製造一批乾淨的假陽性，比原本的錯更難清。
