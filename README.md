# NFL 傳球空間分析工具

## 這是什麼(3–5 句摘要)

我用 NFL Big Data Bowl 的球員追蹤資料,建了一個「傳球空間」分析工具:它量化每一次傳球時場上的空間狀況,包含接球員與最近防守者的距離(separation)、整片場地被哪一隊控制(Voronoi 控制區),並整合成一張單頁 **play 卡**、再包成能瀏覽整季 122 場比賽的互動介面。它揭露了一個反直覺的現象 —— **傳球瞬間最空的接球員,往往不是四分衛實際傳球的對象**,因為深傳靠的是落點與時機,常在很小的空檔(整場中位數約 2.85 碼)下完成。這個工具是給**教練與球探**用的:快速檢視某個 play 的傳球決策與空間結構,而不必逐格看原始追蹤資料。

## 交付物

- **程式**:`notebooks/` 下十個循序的 Jupyter notebook(載入資料 → 空間指標 → play 卡 → 互動工具),外加 `export_play_cards.py`(匯出靜態圖)。
- **output**:`output/` 下的 play 卡 PNG(見下方)。
- **技術附錄**:完整的逐階段開發紀錄見 [`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md)。

## Output 範例

兩張代表性 play 卡(皆為深傳,一成一敗):

- `output/play_card_2021090900_137_deep_pass_complete.png` — 深傳成功,示範「最空的人不等於傳球目標」。
- `output/play_card_2021090900_97_deep_pass_incomplete.png` — 深傳未成,外接員被緊盯。

每張 play 卡含四格:① 發球當下場上位置、② Voronoi 控制區、③ separation 隨時間變化、④ 傳球路徑(僅供參考)。

## 如何執行

需求:Python 3.13、資料集放在 `config.py` 指定的 `DATA_DIR`。

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# 重新產出 output 的 play 卡 PNG
.venv/bin/python export_play_cards.py

# 或開互動工具(需在 Jupyter 實際執行才會出現下拉選單)
.venv/bin/jupyter notebook notebooks/10_multi_game_explorer.ipynb
```

## 方法與誠實的限制

- **separation**(接球員與最近防守者距離)與 **Voronoi 控制區**(整片場地的空間歸屬)是本工具的兩個主力指標,皆經資料驗證。
- **passing lane**(傳球路徑上的擋路者)是平面指標,**對深傳不可靠**:它只看防守者離直線多近,不考慮球的高度與弧線。嘗試用接球員運動外推修正後,資料顯示仍無效(見 `DEVELOPMENT_LOG.md` 第八階段)。因此 play 卡上已把這一格標註為「僅供參考」。
- 全程原則:**先用資料算、再下結論**,不預設球員表現好壞;原始資料集唯讀,不修改。
