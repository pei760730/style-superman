# Lessons — Style Superman 教訓簿（Self-Evolution Loop 的 Learn 層）

> 這裡記「犯過的錯、踩過的坑、與對策」。規則升級路徑：
> **soft note（記在這）→ 反覆出現 → 硬化成 `validate_repo.py` / `repo_health.py` 檢查或文件硬規則。**
> 不要一犯錯就直接加規則；也不要讓同一個坑踩第三次。
>
> 每條格式：日期 · 發生什麼 · 對策 · 硬化狀態。

---

## 已硬化（檢查已存在，記錄根因）

### 2026-06-10 · GitHub workflow 註冊會無聲消失
- **發生什麼**：`daily-brief.yml` 從 init 就在 origin/master 上，但 GitHub Actions 的 workflow 註冊表裡沒有它——連手動 dispatch 都按不了，且沒有任何錯誤訊息。期間帳號曾被 GitHub 風控 suspend 過，`ci.yml` 因每次 push 都觸發而自動重新註冊，`daily-brief.yml` 沒被改過就一直失聯。
- **對策**：對該檔做一次內容變更並 push，GitHub 會重新註冊。
- **硬化**：`repo_health.py` 管不到 GitHub 端；教訓是「**排程 / workflow 的存在 ≠ 在跑**」，要看實際 run 紀錄。daily 斷更由 `repo_health.py` 的新鮮度檢查捕捉（斷更即警告，不管原因是哪層）。

### 2026-06-10 · 文件比決策慢，會留下兩套世界觀
- **發生什麼**：D5 拍板「不接 LLM API」後，`system_design.md`、`operating_manual.md`、`scripts/README.md`、`CHANGELOG.md` Planned、`daily-brief.yml` 註解仍寫著「未來接 LLM API 自動撰寫」。後來的讀者（人或 agent）會不知道哪個是現實。
- **對策**：拍板一個決策時，同一個 PR 內 grep 全 repo 找與該決策矛盾的描述一併改掉。
- **硬化**：`repo_health.py` 的路徑掃描能抓「提到不存在的檔案」這類漂移；**語意矛盾（兩段文字互相打架）仍要靠 review** —— decisions.md 拍板後加一步「全 repo 矛盾掃描」。

### 2026-06-04 · 反爬網站不要硬刮（ZOZO / Akamai）
- **發生什麼**：嘗試抓 ZOZOTOWN 男裝銷售榜，curl 403 / JS 動態 / 聚合站無逐位名次，全部失敗。
- **對策**：「不準確就拿掉」——不保留半準資料，不背 headless 反偵測的重量。詳細紀錄見 `docs/rankings.md` 的 ZOZOTOWN 一節。KREAM / MUSINSA 即時榜同理，改用官方稿公開數據手動建快照。
- **硬化**：已寫進 `docs/rankings.md` 鐵則；新來源評估時先確認「能不能穩定、合法、低成本地拿到」再加進 `sources.yml`。

## Soft notes（觀察中，尚未硬化）

### 2026-06-10 · 「每日」系統的最大風險是根本沒在跑
- **發生什麼**：repo 工程全綠（CI ✅、決策全拍板），但 daily brief 只產過一次。工程完成度掩蓋了「產線停擺」的事實。
- **對策**：`repo_health.py` 新鮮度檢查讓停擺可見；agent 每次開工先跑 health（見 `CLAUDE.md`）。
- **觀察點**：若警告連續出現超過兩週都沒人理，代表「警告→修復」斷鏈，要嘛開自動排程、要嘛承認 daily 改成 weekly，不要讓警告衰退成噪音。

### Windows 終端機 cp950 編碼
- 所有腳本已加 `sys.stdout.reconfigure(encoding="utf-8")`；新腳本記得照抄，CI 端配 `PYTHONIOENCODING: utf-8`。PowerShell 5.1 的 `Get-Content` 讀 UTF-8 檔會亂碼，讀檔用支援 UTF-8 的工具。
