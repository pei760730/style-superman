# Brand Radar 回測 — 日本古著 · 2026-06-19 · 2026-10-25

> 原快照：reports/analysis/2026-06-19-brand-radar-japanese-vintage.md（不回改）

## 📌 回測三行
1. **最準的一句：A.PRESSE 續領跑，而且比當時更紅（⬆️）。** 官方 EC 6/19 後上架的 124 型中 89 型全碼歸零；9/10 推出 Supreme 聯名，皮衣 10/25 二手最低要價比原價高 $2,986（約 +79%）。Taiga Takahashi 從 👀 升到實質 🔥（⬆️），回測鉤 1、2 都應驗。
2. **最大的錯不在品牌，在 tier 的用法：**
   - The Real McCoy's 被放進 🔥「現在就紅」，三個月後看是一家「隨時買得到」的長青牌（❌，判錯的是 tier）。
   - Porter、Hender Scheme 是十幾、幾十年的老牌，卻被放進 👀「剛冒頭」。
   - 這三個 tier 的證據都是長青型清單文，分不出「現在紅」和「一直都在」。
3. **雷達第 1 行「越熱越往質感不炒作走」被部分推翻：** 這條 lane 最熱的那一點（A.PRESSE）正好走進了 Supreme 聯名＋二級溢價，也就是炒作那一層。

## 計分
- 逐品牌 10 列（大阪五大丹寧算 1 列）：⬆️ 2｜✅ 5｜↘️ 0｜❌ 1｜❓ 2
- **應驗率 =（⬆️+✅）/ 可判定數 = 7 / 8 = 88%**；可判定 8，❓ 2（Kapital、Kaptain Sunshine）
- ⚠️ **這 88% 有很大的水分。** 5 個 ✅ 裡有 4 個（Visvim、大阪五大丹寧、Hender Scheme、Porter）原本主張的就是「穩定／常青」，這種預測幾乎不可能錯，資訊量低。
- **只看有方向的熱度主張**，也就是 🔥 三家加上「Taiga 升 📈」這個回測鉤：可判定 3（A.PRESSE ⬆️、Taiga ⬆️、McCoy's ❌），**2/3 = 67%**，Kapital 是 ❓。
- **雷達三行：**
  - ① lane 一句話：部分 ❌（見上）。
  - ② 🔥 點名 Kapital／A.PRESSE／McCoy's：1 中、1 錯、1 無法判定。
  - ③ OrSlow 最對味：這是 lane 相容度主張，不是熱度主張，不計分。不過它的「低調定番」形狀與實測一致（見逐品牌）。
- **回測鉤：**
  - 鉤 1（A.PRESSE 續領跑）：✅ 應驗。
  - 鉤 2（Taiga 走出 cult）：✅ 應驗。
  - 鉤 3（OrSlow／大阪五大低調長青、無泡沫）：✅ 弱應驗，因為二手溢價沒讀，只能證明「零售價買得到、沒打折」。

## 逐品牌

所有「親測」都是 2026-10-25 用 curl 抓取。Shopify 的 `products.json` 用 Firefox UA 抓，逐 variant 看 `available`；「新品」＝ `published_at` 或 `created_at` ≥ 2026-06-19。**可選率只代表「還買得到的比例」，不等於銷量**，各家庫存深度不同。

| 品牌 | 原 tier | 當時主張 | 現況事實（連結） | 判定 |
|---|---|---|---|---|
| **A.PRESSE** | 🔥 | 升勢最猛的古著美學牌；鉤 1：秋冬「原價難買＋二級溢價擴大」即應驗，鋪貨變容易則降溫 | ① [官方 EC](https://ec.apresse.jp/) `products.json`：6/19 後 124 型，**89 型全碼 0**，variant 可選 112/1092（10%）；9/5 第 7 回那批（Royal Navy Cold Weather JK、Motorcycle Trousers、Leather Coach JK 等）全部 0［親測；價格欄沒帶 cookie 時是 USD，不引用］② **Supreme × A.PRESSE 9/10 發售、亞洲 9/12**（[Complex 2026-09-09](https://www.complex.com/style/a/mike-destefano/apresse-japanese-brand-everything-to-know)、[Pause 2026-09-09](https://pausemag.co.uk/2026/09/supreme-collaborates-with-a-presse-for-fall-2026/)）③ 聯名皮衣原價 $3,798／¥660,000，[SupremeCommunity](https://www.supremecommunity.com/season/fall-winter2026/supreme-a-presse-leather-jacket-7253/) 顯示「Resale $6784 +$2986 lowest ask · size XL · Oct 25」［親測 curl］④ repo：8/8 第 5 回 48 小時內 Wool M-65 ¥231,000 全碼歸零，同日同價的 HERILL 全部還有貨（`reports/buy_shortlist/2026-W33.md`） | ⬆️ |
| **Taiga Takahashi** | 👀 | cult 在長但聲量窄、單源；鉤 2：3 個月內出現第 2、第 3 家權威媒體／buyer 點名就算走出 cult | ① [官方 `products.json`](https://www.taigatakahashi.com/products.json)：26AW（9/18 後上架）61 型中 **30 型全碼 0**，variant 可選 56/254（22%）；LOT.224 M-43 Field Trousers 兩色、LOT.111 Work Shirt 兩色、Mackinaw Coat 都是 0［親測］② 6/19 推出女裝線（[官方 collection-women](https://taigatakahashi.com/en/pages/collection-women)；StyleZeitgeist 有報導，但原網址 10/25 回 404，標轉述未複核）③ OK-RM 展 8/1–8/9 在東京日本橋（[官方 blog](https://taigatakahashi.com/en/blogs/craftsmanship/in-the-beginning-woman-was-truly-the-sun-ok-rm-for-t-t)）④ [Highsnobiety 布料專文](https://www.highsnobiety.com/p/taiga-takahahi-fabrics/)：頁面只顯示「3 months ago」（推估 2026-07），寫到「Taiga Takahashi's Fall/Winter 2026 lookbook is reason to consider this.」⑤ repo 10-18 雷達已把它升到 🔥 ⑥ 對照：SSENSE 的「最高 7 折」只是 SS26 季末折扣（搜尋摘要），不是 26AW 的反證 | ⬆️ |
| **Kapital** | 🔥 | 全球 cult、L Catterton 入主、資本與聲量雙升；loud 款是時效熱 | ① 官網 `kapital.jp` 真實路徑與**不存在路徑都回 403**（試過無 UA 和 Firefox UA）＝WAF 擋，**讀不到，不下結論**（E2）② 搜尋摘要轉述官方 news：7/17「POPEYE VS KAPITAL」FW26 PORT ROCKS! 劇照、8/5 短片［轉述未複核］③ 美國選店 [Canoe Club](https://shopcanoeclub.com/collections/kapital) `products.json`：6/19 後 48 型 **0 型全碼完售**，可選 79/127（62%），也沒有任何折扣［親測］④ [H.Lorenzo](https://www.hlorenzo.com/collections/kapital) 正常鋪 FW26 ⑤ L Catterton 入主屬實，但那是 2025-01 的舊聞（[FashionUnited](https://fashionunited.uk/news/business/lvmh-backed-l-catterton-snaps-up-majority-stake-in-japans-kapital/2025010679429)） | ❓ 缺：日本官方庫存（讀不到）、媒體量（搜尋額度用完）、二手行情。單一美國選店「沒秒殺也沒打折」只能看出持平，6 月沒有基準，不判降溫 |
| **The Real McCoy's** | 🔥 | 地表最龜毛復刻牌，愛着趨勢下的標竿；風險是價格不是熱度 | ① [美國官方店 `products.json`](https://therealmccoys.com/products.json)：6/19 後 37 型只有 5 型全碼 0，**variant 可選 100/155（65%）**；10/16 上新的 MA-1 2/6、10/20 上新的 A-2 Deck 5/5［親測］② 6/19 後找不到聯名、新店、媒體專文（搜尋只回 Year Book 2026、舊店訪），repo 10-18 雷達也因「無當期證據」把它剔除 ③ E3 對照：用同一路徑量 A.PRESSE 是 10%、Taiga 是 22%，可見這個方法量得到秒殺，McCoy's 的 65% 不是方法造成的 | ❌ tier 判錯。它是「一直都在」的長青牌，不是「現在就紅」的領跑者。不能叫降溫，因為當時本來就沒有熱度證據，只有一篇長青清單文 |
| **OrSlow** | 📈 | 安靜定番、零浮誇、隨時買得到、不溢價；鉤 3：低調長青、緩升、無泡沫 | ① 選店 [Dant](https://www.dant.us/collections/orslow) `products.json`：6/19 後 42 型，可選 138/206（67%），只有 4 型全碼 0；但定番 Fatigue Pants 多色已在零售價 $235–285 賣空（例如 Summer Fatigue 7/3 上架 Olive 0/5、Reverse Sateen Deep Black 0/6）；126 型裡 9 型打折，屬季末正常［親測］② [Stuf-f](https://stuf-f.com/en/collections/orslow)：6/19 後 14 型可選 34/56［親測］③ FW26 第 3 波照常出貨（Meadow 影片，搜尋摘要） | ✅（形狀跟預期一致：定番在零售價被穩定買走，沒看到炒作。二手溢價未讀） |
| **Visvim** | 📈 | apex、常青而非新紅、connoisseur 層恆熱 | [官方 topics](https://www.visvim.tv/topics/information/)：8/31 Indigo Camping Trailer 膠囊、9/14 WMV Clothing and Harmony、9/15「VISVIM MOTORS CLUB for MR PORTER」（9/21 發售）、9/17 BIOTOP 四店 HARMONIOUS PROCESS 展［親測 WebFetch］；7/14 官方 PR：POPEYE 8 月號搶先刊出 WMV FW26，8/8 發售（[PR](https://www.visvim.tv/pr/media/pr_26071401.html)，搜尋摘要） | ✅（節奏常青。⚠️ 放在 📈「升溫」和它自己寫的「常青」是矛盾的） |
| **Kaptain Sunshine** | 📈 | 精煉日常服，jp 話語層＋us-eu specialty；產量小、好款季中易售罄 | ① [Hypebeast 2026-08-10](https://hypebeast.com/2026/8/kaptain-sunshine-fall-winter-2026-collection-lookbook) FW26 lookbook，HBX 香港店上架，文中沒提需求或完售 ② repo 10-18 雷達剔除，理由是「FW26 只有近似新聞稿的報導、亮點款是 cashmere-linen／sheepskin」③ 官網本次回 200（E 規則記載它曾連續 503），但 NEW ARRIVALS 清單頁回「商品が見つかりませんでした」，疑似是 JS 或參數問題，**不當成沒有新品** | ❓ 缺：消化或完售數據（官網清單讀不到、非 Shopify），以及例行 lookbook 以外的熱度訊號 |
| **大阪五大丹寧**（Warehouse／Full Count／Studio D'Artisan／Sugar Cane／Denime） | 📈 | selvedge 復刻長青底盤，非快熱；鉤 3：緩升、無泡沫 | ① [Heddels 2026-07-16](https://www.heddels.com/2026/07/studio-dartisan-adds-new-wide-leg-sd-104-cut-to-its-core-collection/)：SDA 新增最寬版型 SD-104，$280，文中說「Japanese brands keep releasing wider versions of their jeans」② [Heddels 2026-07-08](https://www.heddels.com/2026/07/sugar-canes-cornerstone-1947-jean-comes-pre-faded-too/)：Sugar Cane 1947 Aged Model，$275 ③ repo 2026-08-jp 月報：Fullcount×GDC 8/4（L4 單源）④ Warehouse／Denime 6/19 後沒找到新聞；官方 `ware-house.co.jp` 不是 Shopify，fullcount.co.jp 連線失敗（000） | ✅（照常推新版型、零售價、沒有泡沫訊號；信心低，二手市場沒讀） |
| **Hender Scheme**（配件位） | 👀 | 工藝＋愛着、jp/us-eu craft 圈穩定 | [Artek 官方 2026-09-01](https://www.artek.fi/en/news/artek-and-hender-scheme-coming-soon)：與 Artek 的皮革家具系列在倫敦設計節（9/15–19）預展，「The collection will then go on global sale on 10 October.」［親測 WebFetch］；Wallpaper 有專訪（[連結](https://www.wallpaper.com/design-interiors/artek-hender-scheme-collection-ryo-kashiwazaki-interview)，搜尋結果） | ✅（穩定，還跨進設計圈。⚠️ 2010 年創立的牌放 👀「剛冒頭」是 tier 誤用） |
| **Porter（吉田カバン）**（配件位） | 👀 | jp 國民級＋全球穩定 | [FASHIONSNAP 2026-09-30](https://www.fashionsnap.com/article/2026-09-30/pas-normal-studios-porter/)：PORTER × Pas Normal Studios 10/2 發售 6 型 ¥22,000–99,000［親測 WebFetch］；POTR × doublet 首次聯名 10/10（[WWDJAPAN](https://www.wwdjapan.com/articles/2520696)，搜尋結果）；官網 `yoshidakaban.com` curl 回 403 | ✅（聯名節奏照常。⚠️ 同樣是 tier 誤用：👀 被拿來當「配件位」的空格用） |

**同一抓法的橫向對照（10-25 親測，6/19 後新品的 variant 可選率）：**
- A.PRESSE 10%
- Taiga 22%（只算 26AW）
- Canoe Club 的 Kapital 62%
- McCoy's 美國店 65%
- Dant 的 orSlow 67%
- CIOTA 67%

這張表只能用來分辨「秒殺型」和「常備型」，不能當銷量排名。

## 漏網
06-19 之後，在日本古著／repro 類別裡真正冒起來、但快照沒列的品牌：**能用證據撐住的只有 1 個**。其餘候選因為搜尋額度用完驗不了，不硬湊。

1. **CIOTA**
   - 定位：用スビンコットン忠實重做軍裝／工裝原型，M-65、M-35、Baker Pants 這類。
   - 證據 ①：[shop.ciota.jp `products.json`](https://shop.ciota.jp/products.json)（10-25 親測）。
     - M-1965 Field Jacket ¥79,200：10/8 上架，**0/8**。
     - Moleskin French Work Jacket ¥69,300：1/9。
     - Fine-Wale Corduroy Baggy：2/12。
   - 證據 ②：repo 2026-10-jp 月報主榜 #1，而且有自家的衰減基準線可以對照。
   - ⚠️ 熱度是選擇性的：全店 6/19 後新品可選率仍有 67%，¥99,000 以上的 MA-1／M-65 幾乎沒動，而且只有市場這一層證據。它在 06-12 jp contemporary 雷達裡有出現，算這份古著快照分類上的漏網，不是整個系統的漏網。
- **類別訊號（不是品牌）**：日本復刻丹寧集體轉向超寬版型。Heddels 7/16 點名 The Flat Head D111、TCB Baggy 50s、ONI 222 Super Wide，以及 SDA SD-104。這是品類訊號，沒有消化數據撐住任何一家，所以不列成漏網品牌。
- **repo 自己的盲點**：Supreme × A.PRESSE（9/10）是這條 lane 三個月來最大的事件，但 repo 裡沒有任何一份報告記到它。原因是 09-jp 月報寫於 9/3，在事件之前；10-jp 月報又沒回頭補。

## 方法檢討
- **事後看預測力好的證據：**
  - 官方 EC 的逐 variant 消化（`products.json`），加上「稀缺型發售」的結構觀察。A.PRESSE 6 月時已經有「到貨即罄」的形狀，三個月後放大成 Supreme 聯名＋二級溢價。
  - 話語層先行、媒體跟進的路徑。A.PRESSE 有 Hypebeast100 2025 和 Highsnobiety，Taiga 是書籤加小眾圈。兩家都照這條路徑升級。
- **事後看預測力差的證據：** 長青型清單文，例如「best Japanese brands」、「最龜毛復刻牌」。McCoy's、Visvim、Hender Scheme、Porter 的 tier 都靠這類文章進榜，三個月後全部是「一直都在」，分不出熱度方向。Kapital 的 🔥 則靠 2024 年的資本事件和名人舊聞，同樣不是時變訊號。
- **tier 被當成版面格子用：** 「配件位」塞進 👀，「長青底盤」塞進 📈 或 🔥。結果 tier 的意思被稀釋，回測只能拿「沒出事」來給 ✅，應驗率就虛胖。
- **快照沒留可重測的基準數字：** 6 月沒有記任何一家的庫存率或完售時間，所以三個月後判不了 Kapital、Kaptain Sunshine 到底是升溫還是降溫，只能判有沒有事件。
- **新踩到的抓取陷阱：** Kapital webshop 首頁有 105 個「SOLD OUT」字串，但全部包在 HTML 註解 `<!-- … -->` 裡，是模板殘留。這是 E1「hidden 假完售」的另一種變形，計數前要先剝掉註解。`kapital.jp` 對不存在路徑也回 403，是 WAF，不是頁面不存在。
- **本次限制：**
  - 本輪 WebSearch 額度在中途用完（與其他 agent 共用上限），所以 Kapital、McCoy's、Kaptain、orSlow 的日文媒體與二手市場沒查完。
  - Yahoo 拍賣、Mercari、Grailed、Lyst、ZOZO 一個都沒讀到。唯一讀到的二手行情是 SupremeCommunity 上的聯名皮衣要價。
- **最該記住的 1 個教訓：🔥／📈 只能給有「時變訊號」的牌（消化速度、聯名或事件、二級溢價），而且快照當下就要記下同一抓法可以重測的基準數字。** 長青清單文只能證明「值得認識」，該放 📚，不能撐熱度 tier。

## 來源記錄
**親測（2026-10-25，curl＋Firefox UA；腳本與原始檔在本 scratchpad 的 `backtest/dl/`）：**
- `ec.apresse.jp/products.json`：200，151 型；不存在路徑回 404 當對照
- `www.taigatakahashi.com/products.json`：200，250 型
- `therealmccoys.com/products.json`：200；`therealmccoys.jp` 不是 Shopify，回的是 HTML
- `shop.ciota.jp/products.json`：200，86 型
- 選店 `dant.us/collections/orslow`、`stuf-f.com/collections/orslow`、`shopcanoeclub.com/collections/kapital` 的 `products.json`：都是 200
- `supremecommunity.com/.../supreme-a-presse-leather-jacket-7253/`：WebFetch 403，改用 curl 抓到 200，從中取出 resale 行
- `kapital-webshop.jp`：200（SOLD OUT 標記全在註解裡）；`kaptainsunshine.com`：200（NEW ARRIVALS 清單是空殼）

**親測 WebFetch：**
- Complex（9/9）、Pause（9/9）、Highsnobiety A.PRESSE profile（無絕對日期，推估 2025）、Highsnobiety Taiga 布料文（3 months ago）
- Taiga 官方 OK-RM blog、visvim 官方 topics、Artek 官方新聞（9/1）
- FASHIONSNAP Porter×PNS（9/30）、Heddels SDA（7/16）、Heddels Sugar Cane（7/8）、Hypebeast Kaptain Sunshine（8/10）、Wikipedia Kapital

**轉述未複核（只有搜尋摘要）：**
- Kapital 官方 news 7/17「POPEYE VS KAPITAL」與 8/5 短片（官網 403）
- visvim PR 7/14（POPEYE 8 月號）
- StyleZeitgeist 的 Taiga 女裝稿（10/25 回 404）
- SupremeCommunity「JPN 45 秒完售」：只出現在搜尋摘要，正文沒引用
- POTR×doublet（WWDJAPAN／fullress）
- orSlow FW26 Drop 3（Meadow 影片）
- SSENSE Taiga 季末折扣
- L Catterton 入主（FashionUnited 2025-01）

**unreadable[]（照 E2 不下結論）：**
- `kapital.jp`：403，不存在路徑也是 403，屬 WAF
- `yoshidakaban.com`：403
- `orslow.co.jp`、`fullcount.co.jp`：000，連線失敗；orSlow 現行官網是 `orslow.jp`，200，但 WP posts API 回空
- `dartisan.co.jp`：https 回 000，http 回 200（未深讀）
- `mrporter.com` journal：curl 與 WebFetch 都 403
- Kaptain Sunshine 清單頁：空殼

**control_checks[]：**
- 判 McCoy's「非領跑」之前，先用同一個 `products.json` 路徑量 A.PRESSE（10%）、Taiga（22%），確認這個方法量得到秒殺。
- Kapital 的「0 型完售」只出自單一美國選店，又沒有 6 月基準，所以**沒有**判成降溫。
