# Changelog

本檔記錄 Style Superman 系統的演進。格式參考 [Keep a Changelog](https://keepachangelog.com/)。

## [Unreleased]

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

### Changed
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

### Added
- **Self-Evolution Loop 落地**（repo 升級成可自我檢查的系統）
  - `scripts/repo_health.py` — Observe / Diagnose / Next Action：一致性檢查（腳本↔文件同步、孤兒檔、文件提到的路徑存在性、workflow 引用）為 ERROR 擋 CI；新鮮度檢查（daily 斷更、當月月報、Lyst 快照落後）為 WARN 提醒；輸出 Next Actions / `--json`
  - `docs/lessons.md` — Learn 層教訓簿：soft note → 反覆出現 → 硬化成檢查的升級路徑；種子教訓（workflow 註冊無聲消失、文件比決策慢、ZOZO 反爬）
  - `CLAUDE.md` 重寫為 AI Agent 作業入口：repo 目標、不可破壞假設、Observe→…→Next 工作迴圈、驗收命令、禁區
  - CI 新增 `repo_health.py --consistency` step；test_smoke 加 health 檢查項

### Changed
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

### Removed
- **ZOZOTOWN 排行**（zozotown.yml + 腳本/來源 plumbing）—— 評估後移除。
  zozo.jp 由 Akamai 防護（curl 403、頁面 JS 動態、WebFetch 逾時、聚合站無逐位名次），
  無真實 headless 瀏覽器無法準確抓取，屬不該背的重量。依「不準確就拿掉」不保留半準觀察清單。
  紀錄與替代方案見 docs/rankings.md「ZOZOTOWN：評估後不採用」。

### Added（早期，原誤置於 Removed 區，2026-06-10 歸位）
- **Rankings 模組**：定期可量化排行（`data/rankings/`）
  - `lyst-index.yml` — Lyst Index 季度快照（已收錄 2026-Q1：Top 20 品牌 + Top 10 單品）
  - `stockx.yml` — StockX 年度/年中快照（已收錄 2025 全年熱銷）
  - `scripts/track_rankings.py` — 檢視最新榜 + 比對名次演化（已驗證可跑）
  - `templates/ranking_snapshot_template.md`、`prompts/ranking_ingest.md`、`docs/rankings.md`
  - `sources.yml` 新增 lyst-index / stockx 兩個 `type: ranking` 來源
- `reports/daily/2026-06-04.md` — SS2026 基準快照（歐美 × 日 × 韓）

### Planned
- 接入更多來源抓取（非 RSS API / 站點；新增來源需人類拍板）
- 推送管線（Telegram / Notion / Google Sheets）——未拍板，先讓 daily 產線跑順
- 挑買 shortlist 自動整理
- ~~AI 自動撰寫 daily brief 全文（接 Claude / OpenAI）~~ — 已由 D5 收掉（2026-06-04）：走排程雲端 agent，不接 repo 內 API

## [0.1.0] — 2026-06-04

### Added
- 初始 repo 結構：`data/`、`reports/`、`prompts/`、`scripts/`、`templates/`、`docs/`、`.github/`
- 資料底層：`sources.yml`、`trend_taxonomy.yml`、`brands.yml`、`people.yml`
- 四套 AI 提示詞模板（daily brief / trend analysis / article to insight / short video）
- 兩支腳本：`generate_daily_brief.py`、`score_trends.py`
- 三套產出模板：daily brief / trend card / short video idea
- 系統文件：system design / content strategy / trend scoring rules / operating manual
- GitHub Actions 排程骨架 `daily-brief.yml`
