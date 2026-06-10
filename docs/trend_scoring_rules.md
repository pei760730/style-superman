# Trend Scoring Rules — Style Superman

定義 `scripts/score_trends.py` 怎麼打分。目標：在一堆趨勢裡，挑出「還在升、我又駕馭得了、又買得到」的那幾個。

## 1. 五個維度（各 0–5）

| 維度 | 問的問題 | 0 分 | 5 分 |
|------|---------|------|------|
| **heat** 熱度 | 現在多熱？ | 沒人討論 | 全網都在講 |
| **growth** 成長性 | 升得多快？（看斜率不看絕對值） | 持平 / 下滑 | 一週內爆量 |
| **longevity** 持續性 | 能撐多久？ | 一週病毒 | 會沉澱成常態 |
| **wearability** 可駕馭度 | 我穿不穿得上身？ | 駕馭不了、塞不進現有衣櫥 | 一拿就會搭、融入現有衣櫥 |
| **accessibility** 落地度 | 買不買得到？門檻多高？ | 天價 / 絕版 / 極端 | 平價、好買、容易入手 |

### 打分指引
- 區分 **heat（現在多熱）** 與 **growth（升多快）**：一個已 mainstream 的趨勢可能 heat=5 但 growth=1，我們未必想壓注。
- `longevity` 參考 taxonomy 的 lifecycle：emerging/rising 通常較高，peak/declining 較低。
- 每個分數**必須附一句理由**（見 trend_card_template），不接受裸分。

## 2. 權重

```
heat          0.20
growth        0.30   ← 最重：我要的是「還在升」
longevity     0.15
wearability   0.25   ← 次重：我駕馭不了的趨勢，再紅也不關我的事
accessibility 0.10
              ────
              1.00
```

權重反映個人偏好：**寧可抓住一個還在升、我又穿得上身的中熱度趨勢，也不追一個已經到頂、或我根本駕馭不了的大眾品。** 若日後偏好轉向（例如願意花更多在 statement 單品），調權重即可，公式不變。

## 3. 計算

```
score = Σ (raw_i / 5) × weight_i × 100        # 0–100
```

每個維度先正規化到 0–1，乘權重，加總後 ×100。實作見 `score_trends.py` 的 `score_one()`。

## 4. 分級門檻（行動）

| 分數 | 分級 | 行動 |
|------|------|------|
| ≥ 75 | 🔥 主打 push | 優先列入挑買 / 認真追 |
| 55–74 | ✅ 採用 use | 進 brief，列入挑買候選 |
| 40–54 | 👀 觀察 watch | 放 watchlist，再盯幾天 |
| < 40 | 🧊 暫存 park | 存著，暫不動作 |

門檻對應 `score_trends.py` 的 `tier_of()`。

## 5. 範例

`barrel jeans`：heat 4 / growth 5 / longevity 3 / wearability 4 / accessibility 3

```
= (4/5×0.20 + 5/5×0.30 + 3/5×0.15 + 4/5×0.25 + 3/5×0.10) × 100
= (0.16 + 0.30 + 0.09 + 0.20 + 0.06) × 100
= 81.0  → 🔥 主打
```

用 `python scripts/score_trends.py --demo` 可看到一組對照。

## 6. 校準與回測

- 每月用 `reports/daily/` 的歷史，回看「當初給高分的趨勢，後來真的紅了嗎？」
- 若系統性高估某類（例如總是高估病毒型單品的 longevity），調整打分指引或權重。
- 評分是活的規則，不是石板。改動記到 `CHANGELOG.md`。
