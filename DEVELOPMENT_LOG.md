# NFL 傳球空間分析專案

本專案最終目標:做一個「傳球空間(passing space)」分析工具,給教練或球探使用。

**目前進度**:

- ✅ **第一階段:載入並理解資料**(`notebooks/01_load_and_understand.ipynb`)
- ✅ **第二階段:聚焦單一傳球 play,切出 snap → pass 片段**(`notebooks/02_isolate_one_pass_play.ipynb`)
- ✅ **第三階段:量化空間 —— 接球員與最近防守者的距離(separation)**(`notebooks/03_separation_over_time.ipynb`)
- ✅ **第四階段:把 separation 推廣到整場比賽(批次化 + 統計)**(`notebooks/04_separation_whole_game.ipynb`)
- ✅ **第五階段:升級空間指標 —— Voronoi 控制區**(`notebooks/05_voronoi_control.ipynb`)
- ✅ **第六階段:聚焦傳球路徑上的空間(passing lane)**(`notebooks/06_passing_lane_space.ipynb`)
- ✅ **第七階段:三個指標整合成一張 play 卡(單頁摘要)**(`notebooks/07_play_card.ipynb`)
- ✅ **第八階段:嘗試用接球員運動修正 passing lane —— 一個誠實的負面結果**(`notebooks/08_lane_with_receiver_motion.ipynb`)
- ✅ **第九階段:互動式 play 瀏覽器(下拉選 play 即時出卡)**(`notebooks/09_interactive_play_explorer.ipynb`)
- ✅ **第十階段:擴充到多場(選比賽 → 選 play → 出卡,涵蓋全部 122 場)**(`notebooks/10_multi_game_explorer.ipynb`)

工具已能瀏覽整個球季 122 場;分析仍遵守「先用資料算、再下結論」。

---

## 資料夾結構

```
nfl_passing_project/
├── .venv/                      # 獨立 Python 虛擬環境(不要手動改)
├── config.py                   # 路徑設定(指向原始資料夾)
├── requirements.txt            # 相依套件清單
├── README.md                   # 交付用的精簡摘要(3–5 句)
├── DEVELOPMENT_LOG.md          # 本檔:完整的逐階段開發紀錄
├── export_play_cards.py        # 匯出 play 卡 PNG 的腳本
├── output/                     # 匯出的 play 卡 PNG(交付用靜態 output)
└── notebooks/
    ├── 01_load_and_understand.ipynb     # 第一階段:載入並理解資料
    ├── 02_isolate_one_pass_play.ipynb   # 第二階段:切出單一傳球 play 片段
    ├── 03_separation_over_time.ipynb    # 第三階段:接球員 separation 隨時間變化
    ├── 04_separation_whole_game.ipynb   # 第四階段:整場 separation 批次化與統計
    ├── 05_voronoi_control.ipynb         # 第五階段:Voronoi 控制區(整片場地空間歸屬)
    ├── 06_passing_lane_space.ipynb      # 第六階段:傳球路徑上的空間(passing lane)
    ├── 07_play_card.ipynb               # 第七階段:三個指標整合成一張 play 卡
    ├── 08_lane_with_receiver_motion.ipynb  # 第八階段:嘗試修正 passing lane(負面結果)
    ├── 09_interactive_play_explorer.ipynb  # 第九階段:互動式 play 瀏覽器(單場)
    └── 10_multi_game_explorer.ipynb        # 第十階段:多場瀏覽器(選比賽 → 選 play)
```

> 原始資料集放在 `/Users/jingleliao/Downloads/nfl-big-data-bowl-regional-event-data-main/data`,
> 本專案只「讀取」它,**不會修改或覆寫任何原始檔案**。

---

## 環境說明

- 偵測到你的系統:Python 3.13.1,且有 Anaconda 的 `(base)` 環境。
- 為避免跟 conda 互相干擾,本專案用標準 `venv` 建立了**獨立環境** `.venv`。
- 已安裝:`pandas`、`jupyter`、`notebook`、`matplotlib`、`scipy`、`ipywidgets`(版本見 `requirements.txt`)。
- `matplotlib` 是第二階段畫場上快照用的。筆記本已設定使用 macOS 內建中文字型 `PingFang TC`,避免中文顯示成方框。
- `scipy` 是第五階段 Voronoi 控制區用的(`cKDTree` 做最近鄰查詢)。
- `ipywidgets` 是第九階段互動介面用的(下拉選單)。互動元件需在 Jupyter 中實際執行才會顯示。

### 如果要重建環境(例如換電腦)

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

---

## 如何執行筆記本

第一階段:

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/01_load_and_understand.ipynb
```

第二階段(建議先跑過第一階段、理解資料後再進來):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/02_isolate_one_pass_play.ipynb
```

第三階段(可獨立執行,內部會自己重建第二階段的片段):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/03_separation_over_time.ipynb
```

第四階段(可獨立執行,處理整場所有傳球 play):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/04_separation_whole_game.ipynb
```

第五階段(可獨立執行,Voronoi 控制區):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/05_voronoi_control.ipynb
```

第六階段(可獨立執行,傳球路徑分析):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/06_passing_lane_space.ipynb
```

第七階段(可獨立執行,整合 play 卡):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/07_play_card.ipynb
```

第八階段(可獨立執行,passing lane 修正嘗試):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/08_lane_with_receiver_motion.ipynb
```

第九階段(單場互動介面,**需在 Jupyter 實際執行**才會出現下拉選單):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/09_interactive_play_explorer.ipynb
```

第十階段(多場互動介面,**需在 Jupyter 實際執行**;選比賽 → 選 play):

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
.venv/bin/jupyter notebook notebooks/10_multi_game_explorer.ipynb
```

瀏覽器會開啟 Jupyter。接著由上而下、**一格一格**執行(選中格子後按 `Shift + Enter`)。

---

## 預期結果(已實際跑過驗證)

### 第一階段(`01_load_and_understand.ipynb`)

照順序執行後,你會看到:

- **games**:122 列 × 7 欄 — 共 122 場比賽。
- **plays**:8557 列 × 32 欄 — 所有進攻 play。
- **players**:1679 列 × 7 欄 — 球員名冊。
- **pff**:188254 列 × 15 欄 — 每個 play 每位球員的球探標記。
- **tracking(單場)**:92644 列 × 16 欄 — 這場比賽每位球員每 0.1 秒的座標。
- **季別**:全部是 2021 球季。
- **週次**:第 1–8 週(各週場數:16/16/16/16/16/14/13/15)。
- **事件標籤**:ball_snap、pass_forward、pass_outcome_caught 等真實標記。
- **小練習答案(playId=137)**:進攻方 `DAL`、防守方 `TB`。

### 第二階段(`02_isolate_one_pass_play.ipynb`)

聚焦範例 play `playId=137`(DAL 進攻、TB 防守,Prescott 深傳左路給 Amari Cooper,成功 28 碼):

- **選定的 play**:`passResult='C'`(傳球成功)。
- **單一 play 片段**:整個 play 共 37 個 frame。
- **關鍵事件**:`ball_snap` 在 frame 7、`pass_forward` 在 frame 32 —— snap 到傳球約 **2.5 秒**。
- **切出的 dropback 片段**:frame 7–32 共 26 個 frame,每個 frame 剛好 23 列(22 位球員 + 1 顆球)。
- **補上人名與角色**:snap 當下可看到 Dak Prescott(QB/Pass)、5 位 Pass Block、5 位 Pass Route,防守方 Coverage 等。
- **場上快照**:snap 當下 22 位球員的散點圖,進攻方(藍)聚在攻防線、防守方(紅)散佈在前方盯人,肉眼確認資料正確。

### 第三階段(`03_separation_over_time.ipynb`)

同一個 play `playId=137`,計算每位接球員與**最近防守者**的距離(separation):

- **分組**:接球員 5 位(`pff_role = Pass Route`)、防守者 6 位(`pff_role = Coverage`)。
- **核心計算**:用歐氏距離,算出每位接球員、每個 frame 到最近防守者的距離,共 **130 列**(5 接球員 × 26 frame)。
- **傳球瞬間 separation 排名**(碼):Dalton Schultz 6.05、Ezekiel Elliott 4.58、Amari Cooper 3.34、Blake Jarwin 2.50、CeeDee Lamb 1.55。
- **一個觀察**:實際接球目標 Amari Cooper 並不是當下最空的人。這說明「最近防守者距離」只是空間的一個切面 —— 深傳常靠落點與時機,不是絕對的空。
- **折線圖**:separation 隨時間變化,一眼看出誰越跑越開、誰被盯死。

### 第四階段(`04_separation_whole_game.ipynb`)

把第三階段的計算包成函式,批次套用到整場(`SAMPLE_GAME_ID`)所有 play:

- **批次結果**:整場 97 個 play → 92 個傳球 play 成功計算,5 個非傳球 play(跑球/擒殺等)自動跳過,共 12164 列。
- **一致性驗證**:函式對 `playId=137` 算出的結果(130 列)與第三階段完全相同,證明批次化沒有改變計算。
- **接球員平均 separation**(傳球瞬間、至少跑 5 條路線):跑衛(RB)如 Ezekiel Elliott(6.54 碼)、Leonard Fournette(5.50)最高;外接員(WR)普遍落在 3 碼附近。
- **整體分佈**:傳球瞬間 separation 中位數 2.85 碼、平均 3.47 碼,分佈明顯右偏 —— 大多數傳球是在 1–4 碼的小空檔下出手,符合實況。

### 第五階段(`05_voronoi_control.ipynb`)

從「最近防守者距離」升級成「整片場地的空間歸屬」,同一個 play `playId=137`:

- **方法**:把球場鋪成 0.5 碼網格,用 `scipy` 的 `cKDTree` 幫每個網格點找最近球員,再依球員隊別數格子算面積(Voronoi 控制區的網格近似)。
- **正確性檢查**:進攻 + 防守控制面積相加 = 100%,網格總面積(6420 平方碼)接近球場實際面積(約 6396)。
- **snap 當下**:進攻 `DAL` 只控制 11%、防守 `TB` 控制 89% —— 因為進攻 11 人集中在攻防線一側,防守散開佔據大片下游場地。
- **熱力圖**:把「哪塊場地屬於誰」畫出來(藍=進攻 / 紅=防守),一眼看懂空間地圖。
- **時間變化**:控制佔比在 snap → pass 間先微降(鋒線被壓)、傳球前回升到 12.8%(接球員跑開、打出空間)。
- **一個體悟**:看「全場控制面積」時進攻方永遠只佔一小塊,所以它不太適合直接判斷傳球決策 —— 這帶出下一階段「聚焦傳球路徑上的空間」的方向。

### 第六階段(`06_passing_lane_space.ipynb`)

把視角收斂到「球真正要走的那條線」—— QB 到接球員的傳球路徑,同一個 play `playId=137`:

- **方法**:對每位接球員畫一條 QB→接球員線段,用「點到線段距離 + 投影參數 t」找出**真正擋在中間**(t∈[0,1])的防守員,取最近者當路徑風險。只算擋在中間的,避開把盯人後衛誤判成擋路。
- **幾何驗證**:點 (5,1) 到線段 (0,0)-(10,0) 距離 1.0、投影 t=0.5,計算正確。
- **傳球瞬間結果**:路徑最乾淨的是 Dalton Schultz(最近擋路者 18.7 碼);最擠的是 Amari Cooper(0.76 碼、4 人擋在中間)。
- **已知侷限(誠實標註)**:實際接球目標正是 Cooper(深傳 28 碼成功)。因為深傳是傳到接球員的**未來位置**,「QB→當下位置的直線」會低估成功機會。
- **傳球路徑圖**:每條通道依擋路程度上色(綠=乾淨 / 橘=有人靠近 / 紅=被擋),一眼看出哪條路傳得進去。

**三個指標的關係**:separation 看單點、Voronoi 看全場、passing lane 看球要飛過的通道 —— 一步步逼近 QB「這球傳不傳得進去」的真實決策。

### 第七階段(`07_play_card.ipynb`)

把前面三個指標 + 場上快照整合進**同一張 2×2 play 卡**,做成一個單頁摘要:

- **版面**:① 發球當下場上位置、② Voronoi 控制區、③ separation 隨時間、④ 傳球路徑,加上帶 play 資訊(對戰 / 檔數 / 傳球結果)的總標題與文字描述。
- **做法**:四張子圖各包一個「畫到指定 `ax`」的函式,全部沿用前面階段驗證過的計算,只是重新組裝排版。
- **可重用**:做成 `play_card(play_id)` 函式 —— 輸入一個 play、輸出一張卡。
- **一般化驗證**:除了示範的 `playId=137`,再用同場另一個 play(`playId=97`,攻防方向相反)測試,四張子圖都正確適應,證明沒有寫死在單一 play。
- **意義**:專案第一個「拿得出手給教練看」的產物,從一堆分析筆記本收斂成工具雛形。

### 第八階段(`08_lane_with_receiver_motion.ipynb`)— 一個誠實的負面結果

想修正第六階段 passing lane 對深傳失真的侷限。原本構想是「用球實際落點當路徑終點」,但:

- **資料做不到**:整場 92 個傳球 play 只有 3 個有 `pass_arrived`、1 個有 `pass_outcome_caught`,tracking 幾乎在傳球瞬間就截斷,沒有球飛行軌跡與落點座標。
- **退而求其次**:改用接球員傳球瞬間的速度 `s` 與方向 `dir`,等速外推「預測落點」。外推本身可信(Cooper 外推 0.5s 與真實後續位置吻合)。
- **但資料檢驗顯示修正無效**:換成預測落點後,實際接球目標 Cooper 的路徑風險反而更擠(0.76 → 0.03 碼)。
- **定位出真正根因**:passing lane 只看平面上「防守員離直線多近」,沒有考慮**球的高度與弧線**。深傳的球從防守員頭上飛過,平面指標必然誤判 —— 換路徑終點修不了這個本質問題。

**這一階段的價值**:不是「修好了」,而是**用資料誠實證明一條路行不通,並找到問題的真正源頭**。結論:passing lane 在這份資料上註定是平面近似,應定位為**輔助參考**,不該被當成深傳的可信指標。separation 與 Voronoi 控制區才是確實可信、可拿來包裝交付的指標。

### 第九階段(`09_interactive_play_explorer.ipynb`)

把 play 卡包成**互動介面** —— 從「筆記本分析」走到「教練點一點就能用」:

- **操作**:一個下拉選單列出全場 92 個傳球 play(每項顯示攻守 / 檔數 / 文字描述),選了就即時出對應的 play 卡。
- **重用,不重造**:繪圖邏輯直接沿用第七階段驗證過的 play 卡。
- **誠實標註**:依第八階段的發現,play 卡第④格(passing lane)標題標為「僅供參考:平面指標,對深傳不準」,避免誤導教練。
- **技術說明**:ipywidgets 的下拉選單需要在 **Jupyter 中實際執行**才會出現並響應點擊;無頭批次執行時不會互動(這是正常行為,非錯誤)。

### 第十階段(`10_multi_game_explorer.ipynb`)

把工具從**只看一場**擴充成**涵蓋全部 122 場**:

- **兩層選單**:先選比賽(122 場,顯示週次 + 主客隊),第二層自動更新成那場的傳球 play,選了就出卡。
- **「選到才讀 + 快取」**:整季 tracking 共約 850MB,不一次全載。選哪場讀哪場,讀過的場存在記憶體,重選同場不重讀(實測:首次讀取約 0.08s,命中快取約 0.03s)。
- **全季共用資料只讀一次**:`plays` / `players` / `pff`(全季)、`games`(列比賽)各讀一次;只有 tracking 逐場載入。
- **跨場驗證通過**:不同週的比賽都能正確辨識傳球 play、角色齊備、正常出卡。

**意義**:工具終於能分析整個球季,而不是一場 demo —— 也讓跨場統計(例如整季平均 separation 排行)成為可能。

---

## 下一階段(第十一階段,等你確認理解後再開始)

工具已能瀏覽整季。下一步有幾條路可走(可擇一或組合):

1. **跨場統計**:沿用第四階段方法但掃過多場,算整季的 separation 排行(逐場讀、累積結果,注意執行時間)。
2. **批次匯出報告**:挑定幾場,一次把 play 卡存成圖檔 / PDF。
3. **打包成獨立 app**(例如 Streamlit),不需要開 Jupyter 也能用。

一樣的原則:**先用資料算、再下結論**,不預設任何球員表現好壞,即使結論是「此路不通」。
