"""匯出 play 卡成 PNG(交付用的靜態 output)。

沿用第七/十階段的 play 卡繪圖邏輯,把幾個代表性 play 存成圖檔,
放進 output/ 資料夾,讓交付物自帶成品圖、不依賴互動環境。

執行:
    .venv/bin/python export_play_cards.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 無視窗後端,純存檔
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.spatial import cKDTree

sys.path.append(str(Path(__file__).resolve().parent))
from config import DATA_DIR, PROJECT_DIR

plt.rcParams["font.sans-serif"] = ["PingFang TC", "Heiti TC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# 要匯出的代表性 play:(gameId, playId, 檔名後綴, 一句話說明)
TARGETS = [
    (2021090900, 137, "deep_pass_complete", "深傳成功:最空的人不等於傳球目標"),
    (2021090900, 97, "deep_pass_incomplete", "深傳未成:外接員被緊盯"),
]

FIELD_X, FIELD_Y, STEP = 120.0, 53.3, 0.5
_gx = np.arange(0, FIELD_X, STEP) + STEP / 2
_gy = np.arange(0, FIELD_Y, STEP) + STEP / 2
_GX, _GY = np.meshgrid(_gx, _gy)
GRID = np.column_stack([_GX.ravel(), _GY.ravel()])


def _p2s(px, py, ax0, ay0, bx, by):
    vx, vy = bx - ax0, by - ay0
    wx, wy = px - ax0, py - ay0
    l2 = vx * vx + vy * vy
    if l2 == 0:
        return np.hypot(px - ax0, py - ay0), 0.0
    t = (wx * vx + wy * vy) / l2
    tc = max(0.0, min(1.0, t))
    return np.hypot(px - (ax0 + tc * vx), py - (ay0 + tc * vy)), t


def prepare_play(plays, players, pff, tracking, game_id, play_id):
    pl = plays[(plays["gameId"] == game_id) & (plays["playId"] == play_id)]
    if pl.empty:
        return None
    pl = pl.iloc[0]
    pt = tracking[(tracking["gameId"] == game_id) & (tracking["playId"] == play_id)]
    sr = pt.loc[pt["event"] == "ball_snap", "frameId"]
    pr = pt.loc[pt["event"] == "pass_forward", "frameId"]
    if sr.empty or pr.empty:
        return None
    snap_frame, pass_frame = sr.iloc[0], pr.iloc[0]
    roles = pff[(pff["gameId"] == game_id) & (pff["playId"] == play_id)][["nflId", "pff_role"]]
    seg = (
        pt[(pt["frameId"] >= snap_frame) & (pt["frameId"] <= pass_frame)]
        .merge(players[["nflId", "displayName"]], on="nflId", how="left")
        .merge(roles, on="nflId", how="left")
    )
    return {
        "info": pl, "off_team": pl["possessionTeam"], "def_team": pl["defensiveTeam"],
        "snap_frame": snap_frame, "pass_frame": pass_frame, "seg": seg,
    }


def _snapshot(d, ax):
    s = d["seg"][(d["seg"]["frameId"] == d["snap_frame"]) & d["seg"]["nflId"].notna()]
    o = s[s["team"] == d["off_team"]]
    f = s[s["team"] == d["def_team"]]
    ax.scatter(o["x"], o["y"], c="tab:blue", s=60, label=f"進攻 {d['off_team']}")
    ax.scatter(f["x"], f["y"], c="tab:red", s=60, label=f"防守 {d['def_team']}")
    ax.set_xlim(0, FIELD_X)
    ax.set_ylim(0, FIELD_Y)
    ax.set_aspect("equal")
    ax.set_title("① 發球當下場上位置")
    ax.legend(loc="upper right", fontsize=7)


def _voronoi(d, ax):
    s = d["seg"][(d["seg"]["frameId"] == d["snap_frame"]) & d["seg"]["nflId"].notna()]
    _, idx = cKDTree(s[["x", "y"]].to_numpy()).query(GRID)
    owner = s["team"].to_numpy()[idx]
    off_pct = (owner == d["off_team"]).sum() / len(owner) * 100
    ax.imshow(
        (owner == d["def_team"]).astype(int).reshape(_GX.shape), origin="lower",
        extent=[0, FIELD_X, 0, FIELD_Y], cmap=ListedColormap(["#a6c8ff", "#ffb3b3"]),
        alpha=0.7, aspect="equal",
    )
    ax.scatter(s[s["team"] == d["off_team"]]["x"], s[s["team"] == d["off_team"]]["y"], c="tab:blue", s=40)
    ax.scatter(s[s["team"] == d["def_team"]]["x"], s[s["team"] == d["def_team"]]["y"], c="tab:red", s=40)
    ax.set_xlim(0, FIELD_X)
    ax.set_ylim(0, FIELD_Y)
    ax.set_title(f"② Voronoi 控制區(進攻控制 {off_pct:.0f}%)")


def _separation(d, ax):
    rec = d["seg"][d["seg"]["pff_role"] == "Pass Route"]
    dfn = d["seg"][d["seg"]["pff_role"] == "Coverage"]
    for name, rg in rec.groupby("displayName"):
        xs, ys = [], []
        for fid, rrow in rg.groupby("frameId"):
            dd = dfn[dfn["frameId"] == fid][["x", "y"]].to_numpy()
            r0 = rrow.iloc[0]
            if len(dd):
                xs.append((fid - d["snap_frame"]) * 0.1)
                ys.append(np.sqrt((dd[:, 0] - r0["x"]) ** 2 + (dd[:, 1] - r0["y"]) ** 2).min())
        ax.plot(xs, ys, marker="o", markersize=2, label=name)
    ax.axvline((d["pass_frame"] - d["snap_frame"]) * 0.1, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("發球後秒數")
    ax.set_ylabel("separation(碼)")
    ax.set_title("③ 接球員與最近防守者距離")
    ax.legend(fontsize=6, loc="upper left")
    ax.grid(True, alpha=0.3)


def _lanes(d, ax):
    fr = d["seg"][(d["seg"]["frameId"] == d["pass_frame"]) & d["seg"]["nflId"].notna()]
    qb = fr[fr["pff_role"] == "Pass"]
    if qb.empty:
        ax.set_title("④ 傳球路徑(此 play 無 QB 標記)")
        return
    qb = qb.iloc[0]
    rec = fr[fr["pff_role"] == "Pass Route"]
    dfn = fr[fr["pff_role"] == "Coverage"]
    for _, r in rec.iterrows():
        blk = [
            dist for _, dd in dfn.iterrows()
            for dist, t in [_p2s(dd["x"], dd["y"], qb["x"], qb["y"], r["x"], r["y"])]
            if 0 <= t <= 1
        ]
        md = min(blk) if blk else np.nan
        color = "tab:green" if (np.isnan(md) or md >= 3) else ("orange" if md >= 1.5 else "tab:red")
        ax.plot([qb["x"], r["x"]], [qb["y"], r["y"]], "--", color=color, linewidth=1.3)
    ax.scatter(rec["x"], rec["y"], c="tab:blue", s=50, label="接球員")
    ax.scatter(dfn["x"], dfn["y"], c="tab:red", s=50, label="防守員")
    ax.scatter([qb["x"]], [qb["y"]], c="black", s=110, marker="*", label="QB")
    ax.set_xlim(0, FIELD_X)
    ax.set_ylim(0, FIELD_Y)
    ax.set_aspect("equal")
    ax.set_title("④ 傳球路徑(僅供參考:平面指標,對深傳不準)", color="dimgray")
    ax.legend(fontsize=7, loc="upper right")


def make_card(d, game_id, play_id):
    info = d["info"]
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    _snapshot(d, axes[0, 0])
    _voronoi(d, axes[0, 1])
    _separation(d, axes[1, 0])
    _lanes(d, axes[1, 1])
    title = (
        f"Play 卡 — game {game_id} / play {play_id}  |  "
        f"{d['off_team']}(攻) vs {d['def_team']}(守)  |  "
        f"第 {info.get('down', '?')} 檔還差 {info.get('yardsToGo', '?')} 碼  |  "
        f"結果 {info.get('passResult', '?')}"
    )
    fig.suptitle(title, fontsize=13, y=0.99)
    fig.text(0.5, 0.005, str(info.get("playDescription", "")), ha="center", fontsize=9, color="dimgray")
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    return fig


def main():
    out_dir = PROJECT_DIR / "output"
    out_dir.mkdir(exist_ok=True)

    plays = pd.read_csv(DATA_DIR / "plays.csv")
    players = pd.read_csv(DATA_DIR / "players.csv")
    pff = pd.read_csv(DATA_DIR / "pffScoutingData.csv")

    tracking_cache = {}
    for game_id, play_id, suffix, note in TARGETS:
        if game_id not in tracking_cache:
            tracking_cache[game_id] = pd.read_csv(DATA_DIR / "tracking" / f"tracking_{game_id}.csv")
        tracking = tracking_cache[game_id]
        d = prepare_play(plays, players, pff, tracking, game_id, play_id)
        if d is None:
            print(f"略過 game {game_id} play {play_id}(非傳球 play)")
            continue
        fig = make_card(d, game_id, play_id)
        out_path = out_dir / f"play_card_{game_id}_{play_id}_{suffix}.png"
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"已存:{out_path.name}  — {note}")

    print(f"\n全部完成,輸出位於:{out_dir}")


if __name__ == "__main__":
    main()
