"""專案設定:集中管理路徑。

原始資料集放在別的資料夾、保持不動;
本專案只讀取資料,不會覆寫或修改原始檔案。
"""

import os
from pathlib import Path

# 原始資料集資料夾(唯讀,不要在這裡寫入任何檔案)。
#
# clone 這個 repo 後,請把路徑指向你本機的資料集。兩種方式擇一:
#   1.(建議)設環境變數 NFL_DATA_DIR,例如:
#        export NFL_DATA_DIR="/path/to/nfl-big-data-bowl.../data"
#   2. 直接改下面 _DEFAULT_DATA_DIR 的值。
#
# 資料集本身很大(約 850MB),不隨 repo 一起提供;請自行下載 NFL Big Data Bowl 資料。
_DEFAULT_DATA_DIR = (
    "/Users/jingleliao/Downloads/nfl-big-data-bowl-regional-event-data-main/data"
)
DATA_DIR = Path(os.environ.get("NFL_DATA_DIR", _DEFAULT_DATA_DIR))

# 本專案資料夾(程式碼與產出都放這裡)
PROJECT_DIR = Path(__file__).resolve().parent

# 本階段用來示範的單一場比賽 gameId(2021 球季第 1 週,TB vs DAL)
SAMPLE_GAME_ID = 2021090900
