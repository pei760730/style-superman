# Changelog

本檔記錄 Style Superman 系統的演進。格式參考 [Keep a Changelog](https://keepachangelog.com/)。

## [Unreleased]

### Removed
- **3 張封存挑買卡 + `reports/buy_picks/` 目錄（2026-06-14，擁有者反轉 D9 封存決定）**：D9 當時把 cdg-postman-bag / nonnative-timberland-taupe / teva-nhoolywood-hurricane 三卡列為「封存保留」,擁有者後判定獨立挑買卡是設計錯誤,全數刪除、目錄收掉。同步:`reports/daily/2026-06-11.md` 移除連到卡的兩個 `→ 挑買卡` 尾連結（For Me 內容不動,只拿掉死指標——一次性破例改凍結 brief）;`README.md` 結構移除 buy_picks 列;`docs/decisions.md` D9 標註反轉;`data/decision_guards.yml` 守衛 pattern 保留續擋重開卡流程、reason 更新。
- **趨勢加權評分框架 score_trends（D14，2026-06-14）**：刪 `scripts/score_trends.py` + `docs/trend_scoring_rules.md`；
  趨勢卡移除 `## 評分（0–5）` 段（`trend_card_template.md` / `validate_repo.py` 必含字串 / `prompts/trend_analysis.md` 同步）；
  `prompts/daily_trend_brief.md` 移除 SCORED_TRENDS input；`system_design.md` 管線移除「評分」階、`operating_manual.md` 移除評分步驟、
  `flow_calendar.md` / `rankings.md` / `scripts/README.md` / `README.md` / `ci.yml` / `tests/test_smoke.py` 一併清除引用。
  根因：腳本只在 smoke 空跑、產線從不餵真資料、趨勢挑選實際全靠主編判斷（沒人用＝0，反熵）。排行快照仍保留為 L1 佐證。

### Changed
- **啟用 trend_history.yml 進判斷迴圈**（2026-06-14 第二輪殭屍盤點：trend_history 06-12 回填後成孤兒——只有 `flow_calendar` 文件嘴上說要查、`validate_repo` 驗格式，**沒有任何 prompt 實際讀它**）：
  `prompts/brand_radar.md` 把它列進 repo 存量輸入、風險欄的「炒作週期位置」改成先查 trend_history 對照 `status_2026` / `menswear_read`、新增規則 7「挖到已成形但未收錄的趨勢順手補一條」；
  `prompts/trend_analysis.md` 加 `HISTORY` 輸入、生命週期判斷改成先對照 trend_history（已收錄引用 `arc` 當基準、未收錄順手補）。讀＋寫回都進 prompt，從孤兒資產變防炒作誤判的錨。非定期維護（D7）。
- **月報自動帶入 Lyst 季對季名次變動**（2026-06-14 啟用既有但從未用過的 `track_rankings --compare`）：
  `compare_lyst` 抽出可回傳字串的 `lyst_comparison_text()`；`generate_monthly_heat_report.py` 在 us-eu 骨架的
  `## 🆚 對照量化基準` 段自動嵌入 Lyst 自有歷史的季對季變動（從 `data/rankings/lyst-index.yml` 算,非來源 move 欄）。
  月報 prompt 改為「升溫/退燒 + 對照基準優先引這塊 L1 客觀數據,別只憑體感」。template / 生成器 / prompt 同步（格式即契約）。
  jp 區因 Mercari 為歷史區間、無季變動可比,自動標註說明。

### Added
- **Drapers 來源 + 歐洲深度走每週深挖位（D13）**（2026-06-13 擁有者問「歐美能不能拆兩區」，評估＋2 週實測後拍板）：
  收 Drapers（英國時裝零售日報）進 `data/sources.yml`（us-eu / media / tier2，RSS 實測可解析），定位零售/通路 intel、餵 brief「值得買｜通路」軸、不當 headline 來源；
  **不開每日 EU 區**（實測 Numéro EN ≈0.2、Dazed ≈0.8 條男裝/天，多天為 0，肥料不足）——歐洲深度改由 `flow_calendar.md §5` 每週深挖位承載（優先男裝週/Pitti/歐洲品牌），Dazed / The Rake / nss / 032c 列人工參考源、不進每日自動源。詳見 `docs/decisions.md` D13

### Fixed
- **README 自動化全貌對齊實況**（2026-06-14）：API 查得實際只有 **1 支雲端 routine**（daily brief 填寫），但 README 列了 5 支（多出週挑 / 歐美月報 / 日本月報 / Lyst Q2 watcher——全不存在）。改為實況:週挑 / 月報 / Lyst 一律**對話觸發**（低頻不開常駐 routine,省額度 + 合 D7）。同步修:① daily Actions 時間 07:00→**05:00**（cron 提早後 README 漏改）;② RSS 收集歸屬更正——Actions 走 `--with-rss` 收 signals、routine 是**讀** signals（原寫「RSS 由 routine 收」與 workflow 實際相反）。
- **daily-brief 排程競態:Actions 提早至 UTC 21:00**（2026-06-14 早安巡檢發現,06-14 首次無人值守裸跑當場爆）：
  Actions（產 skeleton + 收 RSS signals）原 cron UTC 23:00（台北 07:00）,與 07:30 填寫 routine 只差 30 分;
  但 GitHub 排程慢性延遲 60–78 分（實測 06-11~14 皆 +63~78 分）,Actions 一延遲就跑在 routine 之後——
  routine 07:45 寫 brief 時 signals 08:03 才進 master,當天 267 條真訊號全沒用上、退回 WebSearch。
  cron 改 UTC 21:00（台北 05:00）把間距拉到 ~150 分,穩蓋過延遲;日期仍以 Asia/Taipei 算,不受影響。
  （routine 端配套延後 + footer 死連結修正屬 cloud routine 設定,另由擁有者處理。）
- **README 與現況同步**（2026-06-14）：拍板速覽從 D1–D9 補到 **D1–D14**（補 D10 可購性門檻 / D11 品牌雷達 / D12 看到就修 / D13 歐美不拆兩區+Drapers / D14 score_trends 停用），標題「九個拍板」改「十四個拍板」;目錄結構補上漏列的 `data/trend_history.yml`、來源「28 個可 RSS」更正為 **29**（D13 收 Drapers 後）、`decisions.md（D1–D9）` 標籤改 `D1–D14`。純文件同步。
- **daily-brief.yml push race**（2026-06-14 修;上輪巡檢記錄的已知洞）：23:00Z checkout 與 `git push`
  之間若 master 有他人 commit,原本單發 `git push` 會 non-fast-forward 失敗、需手動重跑。改成
  push 被拒就 `git pull --rebase origin master` 再試,最多 3 次（reports/daily 為唯一 per-date 檔,
  rebase 不會衝突）。屬產線可靠性修正,無行為面擴張。
- **清掉 D14 後殘留的「評分」文件漂移**（2026-06-14 sleep-mode 巡檢發現，補 #86 漏網）：score_trends 已於 D14 移除、趨勢挑選回歸主編判斷,但 8 個檔仍把「評分」寫成現行管線步驟/能力——
  `CLAUDE.md` + `README.md` 一句話使命的「分類→評分」改「分類→主編判斷」;README 時間軸「歸類、評分」改「主編判讀」、人機協作「骨架、評分」改「骨架、排行追蹤」、roadmap 去掉「評分規則」;
  `system_design.md` 設計原則「可解釋的評分／分數」改「可解釋的判斷／結論（不走自動評分,D14）」、輸出描述去掉「可評分」;`operating_manual.md` 刪掉指向不存在 `trends.json` 的「評分缺維度警告」疑難排解列;
  `flow_calendar.md` 回饋迴路去掉「評分規則／權重」;`style_strategy.md` 衣櫥回饋「校準評分」改「校準挑買判斷」;`trend_card_template.md` / `trend_analysis.md` 標頭「供評分」改「供簡報」（評分段已於 #86 移除）;`trend_taxonomy.yml` 兩處註解去掉評分字眼。純文件/註解,無邏輯改動。
- **清掉 insight 層殘留引用**（同輪巡檢,補 2026-06-11 移除漏網）：中間 insight 層 06-11 已移除(主編 agent 直接讀 pack),但 `scripts/collect_raw_signals.py` 兩處註解 + `scripts/README.md` 仍把「語意級離題判斷」寫成交給 insight 層——改為「交主編 agent（讀 pack 時判讀）」。純註解/文件,無邏輯改動。
- **health.yml 巡檢假成功**（2026-06-13 sleep-mode 巡檢發現）：`repo_health --strict | tee` 在
  Actions 預設 shell（`bash -e`、無 pipefail）下，失敗 exit code 被 tee 吃掉——看門狗永遠綠、
  issue 永遠不會開。補 `set -o pipefail`；同步修 issue 查詢 `--jq` 無開啟 issue 時印出
  字面 "null" 導致新 issue 開不出來（補 `// empty`）
- **repo_health 週挑落後週數跨年少算**：ISO 年有 52/53 週（2026 即 53 週），「×52」公式
  跨年會少算一週使 WARN 晚響；改用 ISO 週一日期相減
- **README 自動化描述錯置**：07:00 Actions 骨架不收 RSS（無 `--with-rss`），RSS 由 07:30
  內容填寫 routine 收——時間軸與自動化全貌表已更正

### Changed
- **validate_repo 補 data/ YAML 最低防線**：無專屬契約的 data 檔（trend_history /
  decision_guards 及未來新檔）自動納入「可解析 + 頂層 mapping」檢查——先前完全無人驗，
  壞 YAML 會沉默存在直到消費端炸掉（非新增檢查類別，是補 validate_repo docstring 既有承諾的洞）

### Changed
- **品牌雷達六欄化（D11 格式修正）**（2026-06-12 擁有者反饋「為了一句話去描述，沒辦法好好描述亮點」）：
  每牌「為什麼現在紅（一句）」拆成「是什麼（一句）＋為什麼現在紅（1–3 句亮點講滿）」，
  兩欄合計 80–150 字；雷達三行維持目錄職責；首發日潮雷達同日 v2 重發

### Added
- **品牌雷達 Brand Radar（D11）**（2026-06-12 擁有者需求「給關鍵字→當下 10 大最紅品牌（全品項從頭到腳＋配件）」，
  四設計點討論後拍板）：對話觸發「深挖 <關鍵字>」→ `prompts/brand_radar.md` →
  `reports/analysis/YYYY-MM-DD-brand-radar-<slug>.md`；分 tier 不排序、三層證據各牌至少兩層、
  lane 相容度對 brands.yml、入手點只給定番（D10 相容）、結尾留回測鉤；不排程、不新增 template

### Changed
- **可購性門檻（D10）**（2026-06-12 擁有者拍板「推薦的都是最紅的，根本短時間買不到」）：
  daily「值得入手」與週挑 15 樣只推現在買得到、且下個月還買得到的（定番／原版／GR 常販／穩定補貨款）；
  抽選／數量限定／完售前科的限定聯名降到訊號層、不進推薦位；推薦理由禁限時話術。
  同場否決兩個延伸提案不做：買後回填、watchlist 價格盯梢（頻率太低用不到）

### Added
- **📌 今日三行**（2026-06-12 擁有者從五提案中拍板 A）：daily brief 開頭固定 30 秒手機版——
  ①要做（死線+連結）②要知道（最大新聞）③要買嗎（挑買現狀）；只准引用不准重述；
  template / prompt / validate 契約同步，2026-06-13 起生效

### Added
- **每週挑買 Head-to-Toe routine**（2026-06-12 擁有者拍板「週一說早安就給當天＋當週報告」）：
  每週一台北 07:40 雲端 agent 產本週週挑（5 區 × 3 樣、收斂上週 briefs，CI 綠自 merge）——
  選週一的理由：完整收斂上週 7 天、日本發售日集中週五六、週一拿買單有整週行動時間。
  週挑自此脫離對話手動觸發（D7 反熵）；深挖卡仍為對話觸發

### Changed
- **三產物補「買的入口」**（2026-06-12 擁有者問「還能簡單加什麼、要不要延伸到週和月」）：
  daily For Me 固定「⏰ 行動日」子項（今明死線：開賣/截止/定尺寸，含通路連結）；
  週挑每樣加「價格 / 通路」行（挑買榜先前沒有買的入口——有預算帶與風險欄但不知去哪買）；
  月報單品 Top 5 加「價位」欄、挑買方向加「價位帶 / 通路」；連結必附（實測有效）規則延伸到週/月

### Changed
- **Daily brief 地區三區塊 + 密度配額**（2026-06-12 擁有者反饋「資料量太少、沒有歐美一區」）：
  ⚡ 快訊 + KR 三小項 → 🇯🇵 日潮 6–10 條／🇰🇷 韓潮 4–8 條（標三維度）／🌍 歐美 6–10 條（global 歸此），
  一行一則含日期/價格；總量目標頭條+三區 20–30 條/日（130 則上游篩到 15 條是過濾過兇）；
  template / prompt / validate 契約同步

### Added
- **每日 brief 內容填寫 routine**（2026-06-12 擁有者拍板）：每天台北 07:30 雲端 agent 自動把
  07:00 骨架填成完整 brief（收 RSS → 頭條/快訊/KR/For Me → 分支+PR → CI 綠自 merge；已填則跳過）。
  補上產線最後一塊人類手動勞動依賴（先前內容填寫靠擁有者每天開對話觸發，違反 D7 反熵原則）

### Changed
- **粉絲增長 / 內容生產殘留二次深掃**（2026-06-12 擁有者指示「整個深度再看過」）：
  `docs/content_strategy.md` → `style_strategy.md`、`docs/content_calendar.md` → `flow_calendar.md`
  （推翻 06-10「檔名沿用以維持連結」的便宜決定——檔名本身就是殘留識別字，連結已全鏈同步）；
  「Brand Voice」→「調性」、深挖卡「選題條件」→「入選條件」、daily prompt「品牌調性」→「調性」；
  守衛 positioning pattern 補 `content_strategy.md|content_calendar.md` 防回流；
  2026-06 歐美月報（重定位前產物、含可拍選題/粉絲/受眾段）由月報 routine 手動觸發重產覆蓋

### Changed
- **配件全週期覆蓋**（2026-06-12 擁有者拍板「週挑加配件；每週有了，每天每月也要有」）：
  週挑 Head-to-Toe 4 區 → **5 區**（新增 👜 配件：包 / 飾品 / 錶 / 皮帶 / 襪；帽與墨鏡照舊歸頭部），
  12 樣 → 15 樣；validate 契約 + smoke 探針 + 骨架提示同步。daily / monthly prompt 加
  「配件與服裝同等納入」規則（headline / 快訊 / For Me / 單品 Top 5 不漏配件訊號）

### Removed
- **D9 挑買卡停產**（2026-06-12 擁有者拍板「單純推薦就好，有不錯的我自己會去查、自己會去買」）：
  - `prompts/buy_picks.md`、`templates/buy_pick_template.md` 刪除；validate_repo 的 template 契約同步移除
  - daily brief「值得入手」不再同日開卡——For Me 行動帳第五件事改「一句為什麼 / 別買的條件」
  - 已產 3 張卡（reports/buy_picks/）原地封存不刪；週挑 / 月報挑買方向照舊
  - 守衛 `d9-no-buy-pick-cards`；連動：CLAUDE.md 定位、README、system_design、operating_manual、
    content_calendar、content_strategy、ai_collaboration（D8 清單去掉挑買卡）
- **D7 第一性原理瘦身**（2026-06-11 擁有者拍板「砍掉沒用的——什麼是我下個月就不用了」；
  依據：3 並行 agent 審計 + git 證據「7 天 110 commit 中 76% 是自我維護、僅 14% 是情報產出」。
  判準三問與完整理由見 docs/decisions.md D7）：
  - `prompts/article_to_insight.md` — 「待查交給它補」迴圈上線一週從未運轉；主編 agent 直接判讀 raw pack。
    連動更新：system_design 管線圖、operating_manual Step 2、raw_signal_pack_template、
    collect_raw_signals / generate_daily_brief 的註解字串、scripts/README、sources.yml 註解
  - `docs/codex_execution_plan.md`（315 行）— 已封存任務卡，git 歷史即檔案館；
    repo_health PATH_SCAN_EXCLUDE 與 decision_guards exclude 同步移除
  - `data/rankings/google-trends.yml` + 每月 20 分鐘手動拉取流程 — 人類定期手動勞動依賴、建立後零執行；
    推翻同日上午拍板（錯了快認）；rankings.md 留移除紀錄（同 ZOZO 前例）
  - `docs/ai_collaboration.md` 259 → ~30 行 — 多 AI 組織儀式（交接流程/任務卡模板/RACI 全表/範例）全砍，
    留帽子原則、自我審查偏誤控制、誰拍板三條
  - `docs/content_strategy.md` 去重 — 刪與 content_calendar 重複的轉換流程與節奏段

### Added
- **反熵原則**（D7，寫入 CLAUDE.md）：新流程不得依賴人類定期手動勞動；新檢查只能由重複教訓硬化而來；
  維護/產出比為系統健康終極指標（月度回看檢查，產出必須大於維護）
- **月報日本線**（2026-06-11 擁有者拍板「月報不只歐美，再多一個日本」）：
  - `generate_monthly_heat_report.py` 地區參數化（`--region us-eu|jp`）；template / prompt 同步改地區泛用
    （日本量化基準 = Mercari，明標「量化弱、信心保守」，ZOZO 等即時榜照舊不硬刮）
  - `repo_health.py`：月報產出契約 glob 涵蓋 `-jp.md`；新鮮度檢查改多地區（日本線 2026-07 起算，6 月不誤報）
  - smoke 加 `--region jp` 探針；scripts/README、CLAUDE.md 命名、operating_manual、content_calendar 同步
  - 雲端 routine「日本月度熱度速報」每月 1 號（分支 + PR 流程），來源：Fashionsnap / Hypebeast JP /
    Houyhnhnm / WWD Japan / 繊研 / POPEYE，首跑 2026-07-01

### Removed
- **重定位殘留總清**（2026-06-11 擁有者拍板「深挖把拍攝相關都刪掉」，明細見 decisions.md D3 / lessons.md 第三例）：
  - `data/trend_taxonomy.yml` 的 `content_angle` 標籤組（how-to-wear / explainer / hot-take / haul-review / listicle，
    「適合轉成什麼內容」視角）整組移除——挑買卡的 `buy_angle` 已取代其功能；守衛 pattern 同步補上此識別字
  - `reports/analysis/2026-us-jp-overlap.md` — 重定位前（6/4）產物，整份內容創作框架
    （「可直接當選題」「對內容的意義」）且無歷史豁免註記，依 D3 (b) 前例刪除
  - repo 外：「IG 漲粉週報」雲端 routine 經擁有者確認為錯置（純個人興趣、與漲粉無關），已停用

### Changed
- **README 全面重寫**（2026-06-11 擁有者要求「寫清楚」以利審視）：新增「自動化全貌」表
  （誰/何時/跑什麼/**怎麼提交**——明標 daily 骨架是唯一直推 master 的例外）與「防線」章
  （不虛構/守衛/產出契約/快照不溯及/教訓硬化）；目錄樹補漏（google-trends.yml、
  decision_guards.yml、buy_picks/、rankings.md）；移除已刪報告的引用；
  推送 roadmap 註明「傾向用既有據點，不加新平台」
- **排程 routine 任務卡去殭屍化**（2026-06-11）：月度歐美速報 routine 任務卡仍含「2–3 條可拍選題」
  且直推 master（繞過 CI 全部防線）——已改為「本月挑買方向」+ 植入定位鐵則 + 分支/PR 流程；
  Lyst Q2 watcher 同步改分支/PR。教訓記 lessons.md（殭屍任務卡第三例）
- `docs/ai_collaboration.md` 殘留的發布者框架改寫：2.3「品牌主編 / 發布決策者」→「擁有者 / 品味終審」、
  hot-take 審稿語言（太冒犯 / 不夠有梗 / 傷品牌）→ 趨勢判讀（炒作 vs 真趨勢）
- `data/sources.yml` Highsnobiety note「選題深度佳」→「文化脈絡深度佳」；
  `data/trend_taxonomy.yml` 註解兩處「選題」→「挑買判斷」

### Added
- `reports/analysis/2026-06-11-cross-market-scan.md` — 跨市場掃描（4 並行研究 agent：JP / KR / US-EU / contemporary lane）：
  與當日 brief 互補不重複；50+ 條訊號含發售日期/價格/來源，剔除年份混淆訊號並留查證註記；
  關鍵發現：A.PRESSE FW26 全 lane 最早開跑＋丹寧被 SNKRDUNK 型號化、washed denim 擴散成 lane 級語法
  （HERILL 為 CIOTA 現貨替代）、NB 1890 接棒 1906、轉售僅 47% 高於零售=買方市場確立
- **空轉殭屍防線**（2026-06-11 第二輪深審發現）：骨架有必有段落標題、新鮮度也綠、
  但內容從沒被填（殘留 `{{…}}` 佔位）時，健檢會誤報產線健康——「檔案在 ≠ 內容在」的下一層。
  產出契約檢查新增：報告**日期已過**仍殘留佔位 = WARN（當日的不吵，內容填寫中）；smoke 加空轉探針
- **「歐美趨勢＋值得買做到極致」的轉化面與量化面**（2026-06-11 Kai 拍板「都做」）：
  - **每週至少一張趨勢深挖卡（歐美優先）**：content_calendar §5 從「不定期」升格為每週節奏——
    挑本週最強跨源趨勢做「跨源查證→生命週期→全價位帶落地→挑買判斷」（範本：washed-denim 卡）；
    訊號弱可停一次但要在週挑註明，不硬寫。operating_manual 每週清單同步
  - **Google Trends 月度快照**（`data/rankings/google-trends.yml`）：補 Lyst 季度之間的歐美量化空窗。
    固定方法論（US / past 90 days / Shopping / 錨點詞 `sneakers` 正規化 anchor_ratio）+ 12 個追蹤詞
    （每個標注 repo 內出處）；每月人工拉取 ~20 分鐘（無公開 API，不接非官方套件）。
    流程見 docs/rankings.md；首期快照待首次拉取，不預填
- **歐美來源第二輪深挖：話語層 + 社群實況（RSS 25 → 28）**（2026-06-11，擁有者拍板「歐美趨勢+值得買做到極致」；
  us-eu 原為三區最薄）：收 `blackbird-spyplane`（美式男裝話語層指標 newsletter，tier 2）、
  `put-this-on`（經典男裝/二手挖寶視角，tier 3）、`reddit-sneakers`（發售落地驗證，tier 3 community）。
  另測 7 個不收：die-workwear（feed 空）、the-rake/robb-report/sole-retriever/mr-porter（擋 bot 或無 feed）、
  reddit-streetwear（置頂 megathread 噪訊）、british-gq（全站噪訊且 GQ US 已覆蓋）。
  全部走 repo 解析器端到端實測（28 源 56 則 / 0 警告）
- **Daily brief 密度與行動帳規則**（2026-06-11 Kai 拍板：一天一份、25+ 來源，重複要低、密度要高）：
  - For Me 改「行動帳」：禁止重述 headline（引用寫「見頭條 N」）；值得入手每項必含
    單品｜價格(或待查+去哪查)｜通路｜時點｜下一步，且**同日**依 prompts/buy_picks.md 開完整挑買卡
  - 挑買卡新增存放點 `reports/buy_picks/YYYY-MM-DD-<slug>.md`（封存快照，產出後不回改）
  - 連續訊號增量規則：同一趨勢連續入榜只寫新增事實，讀法一行回連前日 brief，不重述邏輯
  - 資料密度鐵則：同一事實全篇一次；headline 字數預算優先給價格/日期/規格/通路；快訊能附日期/價格就附
  - 同步 `templates/daily_brief_template.md` For Me 結構與 `prompts/buy_picks.md` 輸出段
- **來源深挖：RSS 自動收集覆蓋 17 → 25**（2026-06-11，擁有者拍板「日韓歐美潮流 + 國際時裝品牌來源深挖」）：
  - 國際產業：`bof`（The Business of Fashion，tier 1）、`wwd`（美版母刊，tier 2）
  - 歐美潮流：`sneakernews`（發售情報）、`fucking-young`（歐陸男裝設計師端）、
    `heddels`（丹寧 / workwear 工藝判斷）、`permanent-style`（tailoring 品質參照，tier 3）
  - 日潮：`senken`（繊研新聞，產業日報，與 Fashionsnap 互補）
  - 韓潮：`gq-korea`（KR 男裝編輯視角，補 KR 區男裝垂直缺口）
  - 全部 8 源以 repo 解析器三輪實測（fetch + parse + 端到端 collect 24 則 / 0 警告）後收錄；
    另 18 個候選確認不可自動收（無公開 feed / 擋 bot / feed 停更），明細見 PR #34，不硬刮（lessons 鐵則）

### Fixed
- **daily-brief 排程的日期時區 bug**（2026-06-11，首跑前攔到）：schedule 在 UTC 23:00 觸發時
  runner 的「今天」仍是台灣的昨天，腳本吃預設日期會永遠指向已存在的昨日報告 → 防覆寫跳過 →
  排程產線靜默空轉。workflow 改以 `TZ=Asia/Taipei` 計算日期並顯式傳 `--date`，
  commit 訊息同步用該日期（`.github/workflows/daily-brief.yml`；教訓記 docs/lessons.md）

### Planned
- 接入更多來源抓取（非 RSS API / 站點；新增來源需人類拍板）
- 推送管線（Telegram / Notion / Google Sheets）——未拍板，先讓 daily 產線跑順
- 挑買 shortlist 自動整理
- ~~AI 自動撰寫 daily brief 全文（接 Claude / OpenAI）~~ — 已由 D5 收掉（2026-06-04）：走排程雲端 agent，不接 repo 內 API

## [0.2.0] — 2026-06-11

> **重定位版**：內容生產 → 個人挑買決策（2026-06-05 拍板）＋ Self-Evolution Loop 落地
> （repo_health / 決策守衛 / 產出契約 / 週期巡檢）＋ 2026-06-10 全域審計收斂。

### Added
- **D6 拍板 + 守衛**（2026-06-11，Kai）：2026-06-10 全域審計的四項工程提案正式否決、不可回頭
  （scripts 層共用模組、平行契約定義檔、repo_health 設定驅動外部化、月報回補）。
  決策記 `docs/decisions.md` D6；新增守衛 `audit-rejected-over-engineering` 擋識別字復活
  （月報回補由快照鐵則 + 檔內 banner 防護，不入守衛）
- **RSS 自動收集覆蓋 16 → 17**（2026-06-10 盤點）：
  - `vogue-korea` 啟用 RSS（feed 實測可用，但出版方 XML 未宣告 `media:` namespace →
    `collect_raw_signals.parse_feed` 新增 unbound-prefix fallback：ParseError 時自動補宣告再重試，
    純標準庫、真壞 XML 仍降級回空；smoke 測試 +2）
  - `eyesmag`、`musinsa-newsroom` 實測無公開 feed（404 + 頁面無宣告），於 sources.yml 註記維持人工監看
  - 其餘 11 個無 RSS 來源屬結構性不可自動收：rankings ×4（季度/年度報告，走快照）、
    social ×2（IG/TikTok 無 RSS）、retailer ×5（無公開 feed，反爬教訓不硬刮）
- **報告產出契約檢查**（`repo_health.py`，WARN，health.yml 週期巡檢盯）——
  決策守衛只掃活文件、reports/ 是封存快照不在 scope，排程 agent 拿舊任務卡「產出」的報告
  會從這個缺口進 master（2026-06-10 daily 實際發生：趨勢卡用 `對創作者的意義`、結尾是
  `🎬 可拍選題 Content Hooks`）。新檢查只看重定位拍板日（2026-06-05）之後產的 daily / monthly
  （月報以當月 1 號計）：必含現行契約段落（daily `🛒 對我有用 For Me`、monthly `🛒 本月挑買方向`）、
  不得含重定位前識別字；歷史快照不溯及。smoke 新增反向探針
- **趨勢卡：washed / faded denim「舊味」丹寧**（`reports/analysis/2026-washed-denim.md`）——
  2026-06-10 watchlist 單源訊號跨源查證後升級：方向早於 KR 訊號半年已在歐美女裝確立（2025-12 美媒 + Margiela/Dior SS26 秀場）、
  JP 零售春季已主推；男裝大媒體仍未跟進＝挑買窗口。score_trends 85.0 → 主打
- **社群來源 spam 過濾**（`collect_raw_signals.py`）—— reddit-techwear 盜播灌版事件（2026-06-10 brief 警訊）的工程回應：
  community 來源標題層攔盜播/導流模式，濾掉必記 warning 不靜默；smoke 新增不誤殺測試
- **週挑「本週最值得買 Head-to-Toe」**（擁有者直接需求，D3 挑買池落地）—— 每週 4 區（頭/上身/下身/足）× 各 3 樣 + 為什麼是本週：
  `templates/weekly_buy_picks_template.md` + `prompts/weekly_buy_picks.md` + `scripts/generate_weekly_buy_picks.py`
  → `reports/buy_shortlist/YYYY-Wnn.md`；validate_repo 檢查命名與模板、repo_health 新增週挑斷更 WARN（≥2 週）；
  首期 `reports/buy_shortlist/2026-W24.md`（12 樣全數標注 repo 內可驗證來源）
- **決策守衛（decision guards）** — `data/decision_guards.yml` + `repo_health.py` 新檢查（ERROR，CI 擋）：
  已拍板決策留下禁用識別字（如 `content_ideas` / `short_video` / LLM SDK import），任何把它們寫回
  活文件 / 程式碼的 PR 直接紅燈。擋「殭屍任務卡」（排程 agent 拿重定位前的舊任務照做，2026-06-10 實際發生）。
  守衛只做識別字層（零誤殺）；散文層語意矛盾誠實劃界給 review（見 docs/lessons.md）
- **週期健康巡檢** — `.github/workflows/health.yml`：每週一、四排程跑 `repo_health.py --strict`，
  未通過自動開 / 更新 `repo-health` issue。修復「產線停擺時恰好沒人 push → CI 不跑 → 警告無人看見」
  的斷鏈；同時是 daily-brief 排程的獨立看門狗
- `CLAUDE.md` 慣例新增：執行既有任務卡 / 排程任務前先比對定位與最新拍板（殭屍任務卡防線的流程層）；
  拍板「不可回頭」的決策要同步建守衛
- **Self-Evolution Loop 落地**（repo 升級成可自我檢查的系統）
  - `scripts/repo_health.py` — Observe / Diagnose / Next Action：一致性檢查（腳本↔文件同步、孤兒檔、文件提到的路徑存在性、workflow 引用）為 ERROR 擋 CI；新鮮度檢查（daily 斷更、當月月報、Lyst 快照落後）為 WARN 提醒；輸出 Next Actions / `--json`
  - `docs/lessons.md` — Learn 層教訓簿：soft note → 反覆出現 → 硬化成檢查的升級路徑；種子教訓（workflow 註冊無聲消失、文件比決策慢、ZOZO 反爬）
  - `CLAUDE.md` 重寫為 AI Agent 作業入口：repo 目標、不可破壞假設、Observe→…→Next 工作迴圈、驗收命令、禁區
  - CI 新增 `repo_health.py --consistency` step；test_smoke 加 health 檢查項
- **Rankings 模組**（早期項，原誤置於 Removed 區，2026-06-10 歸位）：定期可量化排行（`data/rankings/`）
  - `lyst-index.yml` — Lyst Index 季度快照（已收錄 2026-Q1：Top 20 品牌 + Top 10 單品）
  - `stockx.yml` — StockX 年度/年中快照（已收錄 2025 全年熱銷）
  - `scripts/track_rankings.py` — 檢視最新榜 + 比對名次演化（已驗證可跑）
  - `templates/ranking_snapshot_template.md`、`prompts/ranking_ingest.md`、`docs/rankings.md`
  - `sources.yml` 新增 lyst-index / stockx 兩個 `type: ranking` 來源
- `reports/daily/2026-06-04.md` — SS2026 基準快照（歐美 × 日 × 韓）（早期項，同上歸位）

### Changed
- **審計殘餘修正（2026-06-11「全修」）**：
  - prompt↔template 契約補齊：`buy_picks.md` 欄位清單逐項對應 template（補「來源趨勢」「是什麼」，
    9 項一欄不漏）；`daily_trend_brief.md` KR 追蹤明定三小項逐項填寫
  - `codex_execution_plan.md` §0 加封存註（RSS=C6 已完成、adapter=C7 已 dropped），
    保留原文、消除與檔頭封存說明的表面矛盾
  - `content_calendar.md` 檔名沿用說明與 `content_strategy.md` 措辭統一
  - `generate_monthly_heat_report.build()` 移除已讀未用的 region 參數（檔名後綴仍由 CLI 層處理）
  - smoke：track_rankings `--json` 斷言從「開頭像 JSON」強化為「可解析 + lyst 榜結構完整」
  - 評估後不修：kream 2026-01 快照的六個月期間範圍（無法查證確切月份，硬補違反不虛構）
- **第一性原理全域審計（2026-06-10）的收斂修正**（3 個獨立 agent 分區深讀 + 逐項反向驗證後落地）：
  - 契約同步：`prompts/article_to_insight.md` 輸出鍵名 `category` → `signal_type`，對齊
    `templates/raw_signal_pack_template.md`（同值域、鍵名不一致是彙整時的靜默摩擦）
  - CI 去重：`ci.yml` 收斂為 py_compile + test_smoke 單一驗收入口——原本 validate_repo /
    repo_health / score_trends / track_rankings / generate_daily_brief 在 CI 與 smoke 各跑一遍
  - smoke 補計分公式已知答案測試（washed-denim 卡 4/4/4/5/4 = 85.0、分級門檻、權重總和=1）——
    原本只驗「跑得動」不驗「算得對」
  - 文件對齊現實：README 樹狀圖去掉「內容生產線」舊語、operating_manual 任務卡指引改指
    repo_health Next Actions（codex plan 已封存）、decisions.md 頭部改為自足描述
  - `docs/rankings.md` 補 snapshots 排序細則：「最新」以發布／入庫時間為準非 period 字面
    （消除 KREAM 年度結算 vs 月度快照的歧義）
  - 重定位前的兩份歷史快照（daily 2026-06-04、monthly 2026-06-eu）檔頭加「請勿改寫」banner，
    防未來 agent 把不溯及的舊格式誤當違規修掉
  - 審計中**評估後不做**（理由記錄於 PR）：yaml 載入抽共用模組（腳本獨立性 > 樣板去重）、
    repo_health 設定驅動重構（YAGNI）、field_contracts.yml 平行契約定義（template 即契約，
    兩套定義=兩套世界觀風險）、月報缺段落回補（快照不回改）
- repo_health RSS 覆蓋指標分母改為「結構上可自動收的來源」（media / community → 17/19）——
  原本拿全部 30 個來源當分母，但 ranking 走快照、social 無 RSS、retailer 不硬刮，
  覆蓋率永遠像「只做一半」，指標會衰退成沒人看的噪音
- README 對齊現實：smoke 項數改指向檔頭（硬編數字必漂移）；workflows 樹補 `health.yml`；
  串接列反映 RSS / AI 撰寫已接；codex_execution_plan 改標已封存（現役待辦由 repo_health 產生）；
  roadmap 反映 daily 排程已開啟（2026-06-10）
- repo_health 輸出品質：Next Actions 去重保序（多個 finding 指到同一條行動時不再重複列）；
  daily 斷更的建議文字不再說「開啟 schedule」（已於 2026-06-10 開啟）——改指向查 Actions run 紀錄
  （檔案在 ≠ 在跑）。`docs/system_design.md` 排程列同步反映現實
- **系統重新定位：內容生產 → 個人興趣 + 挑買決策。** 擁有者本人不拍片 / 不做內容創作；全 repo 從「服務內容創作者 / 產短影音選題」改為「服務我自己：追潮流、挑單品入手」。
  - daily brief 結尾 `🎬 可拍選題 Content Hooks` → `🛒 對我有用 For Me`（值得入手 / 想試的穿搭 / 想深入了解）；`對創作者的意義` → `對我的意義`。月報 `🎬 可拍選題` → `🛒 本月挑買方向`。
  - `prompts/short_video_ideas.md` → `prompts/buy_picks.md`、`templates/short_video_idea_template.md` → `templates/buy_pick_template.md`：從短影音腳本卡改造成「挑買卡」（該不該買 / 怎麼搭 / 在哪買 / 補哪個衣櫥缺口）。
  - 評分維度 `content_potential 內容潛力（好不好拍）` → `wearability 可駕馭度（好不好穿、能否融入衣櫥）`；同步 `score_trends.py`、`trend_card_template.md`、`trend_scoring_rules.md`、`validate_repo.py`。
  - 文件層全面改寫：`content_strategy.md`（受眾＝我自己、情報支柱、個人成功指標）、`content_calendar.md`（每週挑買取代每週拍攝）、`system_design.md` 第 5 階段「選題」→「挑買」、`operating_manual.md` Step 6、`ai_collaboration.md` / `decisions.md` / `codex_execution_plan.md` 的內容創作語言。`CLAUDE.md` 加上個人定位守則。
  - 契約檢查（`validate_repo.py`）與 smoke tests 全綠。
- **清除 D5 後殘留的兩套世界觀**：`docs/system_design.md`、`docs/operating_manual.md`、`scripts/README.md`、`.github/workflows/daily-brief.yml` 中「未來接 LLM API 自動撰寫」的描述全部改為現實（AI 撰寫走對話 agent / 排程雲端 agent，不接 repo 內 API）
- `docs/ai_collaboration.md` 角色改為 model-agnostic（主編 / 工程是「帽子」不是綁定產品），新增自我審查偏誤規則（同一個 agent 不終審自己的產出）
- `docs/codex_execution_plan.md` 頂部標註已封存（C1–C6 完成、C7 dropped；現役待辦改由 `repo_health.py` 產生）
- `.github/workflows/daily-brief.yml` 內容更新觸發 GitHub 重新註冊（帳號風控後 workflow 註冊消失，連 dispatch 都不可用；見 lessons）
- `.gitignore` 補 `reports/monthly/*.draft.md`
- 修正本檔下方 0.1.0 之前的分區錯置：「Rankings 模組」等新增項原誤放在 Removed 區

### Fixed
- CHANGELOG 分區錯置與 Planned 區和 D5 決策矛盾的項目

### Removed
- **選題池（content_ideas）整組移除** — 擁有者拍板：本 repo 純個人興趣（深挖趨勢、找出問題），沒有要拍片，不需要可拍選題池。`reports/content_ideas/`（含排程 agent 2026-06-10 依舊任務卡落地的 2026-06.md）、`validate_repo.py` 命名檢查、README / decisions 引用一併清除；挑買池仍依 D3 走 `reports/buy_shortlist/`（待需要時建立）
- **ZOZOTOWN 排行**（zozotown.yml + 腳本/來源 plumbing）—— 評估後移除。
  zozo.jp 由 Akamai 防護（curl 403、頁面 JS 動態、WebFetch 逾時、聚合站無逐位名次），
  無真實 headless 瀏覽器無法準確抓取，屬不該背的重量。依「不準確就拿掉」不保留半準觀察清單。
  紀錄與替代方案見 docs/rankings.md「ZOZOTOWN：評估後不採用」。

### Data
- **RSS 覆蓋 5/30 → 16/30**：對 `rss: null` 的 13 個來源逐一實測常見 feed 端點，11 個可解析即寫入
  （GQ、Esquire、Hypebeast JP/KR、WWD Japan/Korea、MEN'S NON-NO、POPEYE、Houyhnhnm、Dazed Korea、W Korea）；
  eyesmag / vogue-korea 無可用 feed 維持 null。GQ / Esquire 為全站 feed，男裝篩選交 insight 層

### Ops
- **開啟 daily-brief 每日排程**（UTC 23:00 = 台灣 07:00 自動產骨架，2026-06-10 Kai 拍板）；workflow 已確認在 GitHub 端重新註冊
- Actions 升級至 Node 24 相容版（`checkout@v5`、`setup-python@v6`；GitHub 2026-06-16 起強制 Node 24）
- `reports/analysis/2026-early-summer-jp-kr-eu.md` — 2026 初夏（5–6 月）歐美/日/韓 男裝從頭到腳趨勢 + 值得關注品牌；對照 repo 量化榜，**每節附英文原文來源連結**（報告交付一律附來源以便回原文深讀）
- **韓國 rankings（KREAM + MUSINSA）** — 把韓潮從「媒體訊號」升級成可長期比對的量化榜
  - `data/rankings/kream.yml` — KREAM 限量/轉售成交量（韓版 StockX）：2025 年度 Nike 成交 #1、平台去球鞋化 50%→37%；2026-01 中古精品 +203%、Rolex +363%
  - `data/rankings/musinsa.yml` — MUSINSA 平台銷售榜（最大男裝電商）：2026-02 무신사 스탠다드 連 5 月 #1、adidas #2；2025-12 #1 PB、#2 TNF
  - `track_rankings.py` 新增 `kream`/`musinsa` 來源 + `--region kr` 過濾與 KR 顯示
  - `validate_repo.py` 加 musinsa 品牌 rank 唯一性檢查
  - docs/rankings.md 補韓國生態（KREAM 看 flex/轉售、MUSINSA 看日常實買）與「逐位榜 JS 動態無法自動抓、採官方公開數據手動建立」紀錄
- **C6 — RSS 收集 → raw_signal_pack**
  - `scripts/collect_raw_signals.py`：從 `data/sources.yml` 有 RSS 的來源收集近期文章，轉成事實層 raw_signal_pack（純標準庫、抓取失敗優雅降級；`signal_type`/`credibility` 留待查交 article_to_insight）
  - `generate_daily_brief.py` 新增 `--with-rss` / `--raw-signals-out`
  - `tests/fixtures/sample_feed.xml` + test_smoke 加 2 項 RSS 離線測試（不依賴網路，共 9 項）
- **完成 Codex 執行計畫 C3–C5**
  - C3：`templates/raw_signal_pack_template.md` — RAW_SIGNALS 中間格式契約（接 RSS/LLM 前先固定形狀）；`prompts/article_to_insight.md`、`prompts/daily_trend_brief.md` 加引用
  - C4：`scripts/generate_monthly_heat_report.py` — 本地產月度歐美速報骨架（自動帶入 Lyst/StockX 季度基準），`--draft` 不入版控
  - C5：`tests/test_smoke.py` — 核心腳本最小驗收（7 項，無需 pytest）；接進 `ci.yml` 為 PR smoke 一步
- `scripts/ingest_ranking_snapshot.py`（C2）— 安全加入排行快照：預設 dry-run 檢查契約（period 不重複、rank 不重複、StockX 不壓成單一 ranking、Mercari 必含 brand_top/menswear_read），`--write` 才寫入且保留既有註解。附 `tests/fixtures/*_snapshot.yml` 合成範例。
- `scripts/validate_repo.py` + `.github/workflows/ci.yml` + `requirements.txt` — 補 PR smoke validation，讓 YAML / template / report 契約在 merge 前自動檢查。
- `CLAUDE.md` + `docs/codex_execution_plan.md` — 實際落地 Codex 第一輪 repo review，補 Claude Code 執行守則、工程任務卡與下一步驗收順序。
- `docs/ai_collaboration.md` — Codex / Claude Code / 人類分工手冊，補上 RACI、交接模板、review 清單與任務分派規則。
- **月度熱度速報（歐美）** — 補上「這個月什麼最紅」的月度粒度（Lyst 只有季度）
  - `templates/monthly_heat_report_template.md` + `prompts/monthly_heat_report.md`
  - `reports/monthly/` 產出區；由每月 1 號的遠端排程自動生成 `YYYY-MM-eu.md`
  - 綜合搜尋趨勢 + 電商 best-seller + 媒體/社群，對照 repo 內 Lyst/StockX 季榜，每條標信心、不編造
- `reports/analysis/2026-us-jp-overlap.md` — 歐美×日本 2026 潮流交集分析（運動鞋越界 / gorpcore / elevated basics 為共同核心；ASICS·Salomon·FOG·Uniqlo 跨市場）
- **日本 rankings + 媒體源**
  - `data/rankings/mercari-jp.yml` — Mercari 二手成交（成交 #1 Chanel→Uniqlo）
  - `track_rankings.py` 新增 `mercari` 來源 + `--region jp|us-eu` 過濾
  - `sources.yml` 新增日本 media（MEN'S NON-NO/POPEYE/Houyhnhnm）與 WEAR
  - docs/rankings.md 補日本生態與「量化榜+媒體街拍兩條腿」鐵則

## [0.1.0] — 2026-06-04

### Added
- 初始 repo 結構：`data/`、`reports/`、`prompts/`、`scripts/`、`templates/`、`docs/`、`.github/`
- 資料底層：`sources.yml`、`trend_taxonomy.yml`、`brands.yml`、`people.yml`
- 四套 AI 提示詞模板（daily brief / trend analysis / article to insight / short video）
- 兩支腳本：`generate_daily_brief.py`、`score_trends.py`
- 三套產出模板：daily brief / trend card / short video idea
- 系統文件：system design / content strategy / trend scoring rules / operating manual
- GitHub Actions 排程骨架 `daily-brief.yml`
