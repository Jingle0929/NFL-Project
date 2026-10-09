"""Route space, version 1: ONE play, ONE route runner, ONE static picture.

Question (for a coach or scout):
    "When does this route-running player create space from defenders, and how
     much space is available when the quarterback releases the pass?"

What this script makes:
    output/route_space_v1_<game>_<play>_<player>.png   the picture
    output/route_space_v1_<game>_<play>_<player>.csv   the numbers behind the line chart

The calculation is the one from notebooks/03_separation_over_time.ipynb:
    - route runner   = a player whose pff_role is "Pass Route"
    - defenders      = players whose pff_role is "Coverage"
    - distance       = straight-line distance, sqrt((x1-x2)^2 + (y1-y2)^2), in yards
    - nearest        = the smallest of those distances in each frame
    - time           = (frameId - snap frame) * 0.1 seconds

Run it:
    python3 route_space_v1.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw straight to a file, no pop-up window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse, Rectangle

sys.path.append(str(Path(__file__).resolve().parent))
from config import DATA_DIR, PROJECT_DIR

# ---------------------------------------------------------------------------
# 1. CHOICES YOU CAN CHANGE
# ---------------------------------------------------------------------------
GAME_ID = 2021090900
PLAY_ID = 137
SELECTED_PLAYER = "Amari Cooper"  # must be a "Pass Route" player on this play

SECONDS_PER_FRAME = 0.1  # the tracking data has 10 frames per second

# Team colours (offense = circles, defense = squares, so colour is never the only clue)
TEAM_COLOURS = {"DAL": "#003594", "TB": "#D50A0A"}
HIGHLIGHT = "#F59E0B"  # orange ring + path for the selected player
INK = "#1F2937"        # dark text / main line
MUTED = "#6B7280"      # secondary text
BALL = "#7B4A1E"

# ---------------------------------------------------------------------------
# 2. LOAD THE DATA (read-only)
# ---------------------------------------------------------------------------
plays = pd.read_csv(DATA_DIR / "plays.csv")
players = pd.read_csv(DATA_DIR / "players.csv")
pff = pd.read_csv(DATA_DIR / "pffScoutingData.csv")
tracking = pd.read_csv(DATA_DIR / "tracking" / f"tracking_{GAME_ID}.csv")

play = plays[(plays["gameId"] == GAME_ID) & (plays["playId"] == PLAY_ID)].iloc[0]
offense, defense = play["possessionTeam"], play["defensiveTeam"]

track = tracking[(tracking["gameId"] == GAME_ID) & (tracking["playId"] == PLAY_ID)]
roles = pff[(pff["gameId"] == GAME_ID) & (pff["playId"] == PLAY_ID)][["nflId", "pff_role"]]

# Attach each player's name and his job on this play. The ball has no nflId,
# so its name and role stay empty.
track = track.merge(players[["nflId", "displayName"]], on="nflId", how="left").merge(
    roles, on="nflId", how="left"
)

# The two key moments, taken from the "event" column of the tracking data.
snap_frame = int(track.loc[track["event"] == "ball_snap", "frameId"].iloc[0])
release_frame = int(track.loc[track["event"] == "pass_forward", "frameId"].iloc[0])
release_sec = (release_frame - snap_frame) * SECONDS_PER_FRAME

# "left" means the offense is moving toward SMALLER x values.
play_direction = track["playDirection"].iloc[0]

# ---------------------------------------------------------------------------
# 3. THE CALCULATION: distance to the nearest coverage defender, every frame
# ---------------------------------------------------------------------------
runner = track[track["displayName"] == SELECTED_PLAYER]
if runner.empty or (runner["pff_role"] != "Pass Route").any():
    raise SystemExit(f"{SELECTED_PLAYER} is not a 'Pass Route' player on this play.")
coverage = track[track["pff_role"] == "Coverage"]

rows = []
for frame_id, me in runner.set_index("frameId").iterrows():
    defenders_now = coverage[coverage["frameId"] == frame_id]
    distances = np.sqrt((defenders_now["x"] - me["x"]) ** 2 + (defenders_now["y"] - me["y"]) ** 2)
    nearest = distances.idxmin()
    rows.append(
        {
            "frameId": frame_id,
            "seconds_since_snap": round((frame_id - snap_frame) * SECONDS_PER_FRAME, 1),
            "nearest_coverage_defender": defenders_now.loc[nearest, "displayName"],
            "distance_yd": round(float(distances[nearest]), 2),
            # True = inside the snap -> release window used in notebook 03
            "in_snap_to_release_window": snap_frame <= frame_id <= release_frame,
        }
    )
sep = pd.DataFrame(rows)
window = sep[sep["in_snap_to_release_window"]]

at_snap = window.iloc[0]
at_release = window.iloc[-1]
smallest = window.loc[window["distance_yd"].idxmin()]
largest = window.loc[window["distance_yd"].idxmax()]

# ---------------------------------------------------------------------------
# 4. DRAW
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(16, 10.5), facecolor="white")
grid = fig.add_gridspec(2, 2, height_ratios=[3.1, 1], width_ratios=[1, 1.05], hspace=0.16, wspace=0.14,
                        left=0.045, right=0.975, top=0.875, bottom=0.03)
ax_field = fig.add_subplot(grid[0, 0])
ax_line = fig.add_subplot(grid[0, 1])
ax_notes = fig.add_subplot(grid[1, :])

runner_number = int(runner["jerseyNumber"].iloc[0])
fig.suptitle(
    f"How much space did {SELECTED_PLAYER} (#{runner_number}, {offense}) have on this play?",
    fontsize=17, fontweight="bold", color=INK, x=0.045, ha="left", y=0.975,
)
fig.text(
    0.045, 0.925,
    f"Game {GAME_ID}, play {PLAY_ID}  |  {offense} on offense, {defense} on defense  |  "
    f"quarter {play['quarter']}, down {play['down']} with {play['yardsToGo']} yards to go\n"
    f"Official play description: {play['playDescription']}",
    fontsize=10, color=MUTED, ha="left", va="top", linespacing=1.5,
)

# ---- 4a. Field view at the moment of pass release -------------------------
now = track[track["frameId"] == release_frame]
people = now[now["nflId"].notna()]
ball_now = now[now["team"] == "football"].iloc[0]

x_min, x_max = 82, 120  # only the part of the 120-yard field where the players are
ax_field.set_facecolor("#F1F6EE")
ax_field.set_xlim(x_min, x_max)
ax_field.set_ylim(0, 53.3)
ax_field.set_aspect("equal")

# End zone: in this data x runs 0-120; x 110-120 is an end zone. The play
# started at the DAL 2-yard line (x = 108), so this is DAL's own end zone.
ax_field.add_patch(Rectangle((110, 0), 10, 53.3, color=TEAM_COLOURS.get(offense, "#888"), alpha=0.10, lw=0))
ax_field.text(118.6, 46, f"{play['yardlineSide']} END ZONE", rotation=90, ha="center", va="center",
              fontsize=10, color=MUTED, fontweight="bold")

# Yard lines every 5 yards, with the usual field numbers every 10.
for x in range(85, 111, 5):
    ax_field.axvline(x, color="white", lw=1.6, zorder=1)
    ax_field.axvline(x, color="#C9D3C3", lw=0.6, zorder=1)
tick_x = [90, 100, 110]
ax_field.set_xticks(tick_x)
ax_field.set_xticklabels(["20-yard line", "10-yard line", "goal line"], fontsize=9, color=MUTED)
ax_field.set_yticks([])
ax_field.set_ylabel("field width: 53.3 yards (sideline to sideline)", fontsize=9, color=MUTED)
for side in ax_field.spines.values():
    side.set_color("#C9D3C3")
ax_field.tick_params(length=0)

# Line of scrimmage = where the ball was placed before the play started.
los_x = play["absoluteYardlineNumber"]
ax_field.axvline(los_x, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=2)
ax_field.text(los_x - 0.4, 52.3, "line of scrimmage\n(where the play started)", fontsize=8.5, color=INK,
              ha="right", va="top", linespacing=1.3)

# Players: offense = circles, defense = squares, jersey number inside.
for team, marker in [(offense, "o"), (defense, "s")]:
    group = people[people["team"] == team]
    ax_field.scatter(group["x"], group["y"], s=230, marker=marker, color=TEAM_COLOURS.get(team, "#888"),
                     edgecolor="white", linewidth=1.3, zorder=4,
                     label=f"{team} ({'offense' if team == offense else 'defense'})")
    for _, p in group.iterrows():
        ax_field.text(p["x"], p["y"], str(int(p["jerseyNumber"])), color="white", fontsize=7,
                      fontweight="bold", ha="center", va="center", zorder=5)

# Selected player: orange ring, plus the path he ran from snap to release.
path = runner[(runner["frameId"] >= snap_frame) & (runner["frameId"] <= release_frame)]
me_now = path.iloc[-1]
ax_field.plot(path["x"], path["y"], color=HIGHLIGHT, lw=3, zorder=3, solid_capstyle="round",
              label=f"{SELECTED_PLAYER}'s path, snap to release")
ax_field.scatter([path["x"].iloc[0]], [path["y"].iloc[0]], s=70, facecolor="white", edgecolor=HIGHLIGHT,
                 linewidth=2, zorder=3)
ax_field.scatter([me_now["x"]], [me_now["y"]], s=520, facecolor="none", edgecolor=HIGHLIGHT, linewidth=3.2, zorder=6)
ax_field.text(me_now["x"] - 1.4, me_now["y"] - 1.6, f"{SELECTED_PLAYER} #{runner_number}\n(selected player)",
              fontsize=10, fontweight="bold", color=INK, ha="right", va="top", linespacing=1.3)

# Nearest coverage defender at release, with the distance written on the link.
nd = people[people["displayName"] == at_release["nearest_coverage_defender"]].iloc[0]
ax_field.plot([me_now["x"], nd["x"]], [me_now["y"], nd["y"]], color=INK, lw=1.6, ls=":", zorder=3)
ax_field.annotate(
    f"{at_release['distance_yd']:.2f} yd to the nearest\ncoverage defender,\n{nd['displayName']} #{int(nd['jerseyNumber'])}",
    xy=((me_now["x"] + nd["x"]) / 2, (me_now["y"] + nd["y"]) / 2), xytext=(92.5, 19.5),
    fontsize=10, color=INK, ha="center", va="center", linespacing=1.3,
    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkB=4),
)

# Quarterback and ball.
qb = people[people["pff_role"] == "Pass"]
if not qb.empty:
    qb = qb.iloc[0]
    ax_field.annotate(f"quarterback (the passer)\n{qb['displayName']} #{int(qb['jerseyNumber'])}",
                      xy=(qb["x"], qb["y"]), xytext=(115.6, 33), fontsize=9, color=INK, ha="center",
                      linespacing=1.3, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkB=9))
ax_field.add_patch(Ellipse((ball_now["x"], ball_now["y"]), 1.5, 0.9, facecolor=BALL, edgecolor="white", lw=1.2, zorder=7))
ax_field.annotate("ball", xy=(ball_now["x"], ball_now["y"]), xytext=(116.3, 15.5), fontsize=9, color=INK,
                  ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkB=6))
ax_field.scatter([], [], s=90, marker="o", color=BALL, label="ball")  # legend entry only

# Offensive direction arrow, drawn above the field.
arrow_from, arrow_to = (0.80, 0.20) if play_direction == "left" else (0.20, 0.80)
ax_field.annotate("", xy=(arrow_to, 1.045), xytext=(arrow_from, 1.045), xycoords="axes fraction",
                  arrowprops=dict(arrowstyle="-|>", color=TEAM_COLOURS.get(offense, INK), lw=3, mutation_scale=22))
ax_field.text(0.5, 1.075, f"{offense} OFFENSE IS ATTACKING THIS WAY", transform=ax_field.transAxes,
              ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=TEAM_COLOURS.get(offense, INK))
ax_field.set_title(f"1. Where everyone is when the pass is released ({release_sec:.1f} s after the snap)",
                   fontsize=12.5, fontweight="bold", color=INK, loc="left", pad=44)
ax_field.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="white", edgecolor="#C9D3C3",
                framealpha=0.95, borderpad=0.7, labelspacing=0.7)

# ---- 4b. Line chart: distance to nearest coverage defender over time -------
y_top = max(8.0, sep["distance_yd"].max() * 1.22)
ax_line.set_ylim(0, y_top)
ax_line.set_xlim(sep["seconds_since_snap"].min() - 0.1, sep["seconds_since_snap"].max() + 0.1)

# Background bands: one band per stretch with the SAME nearest defender.
run_id = (sep["nearest_coverage_defender"] != sep["nearest_coverage_defender"].shift()).cumsum()
bands = ["#EEF0F3", "#FBF3E4"]
for i, (_, stretch) in enumerate(sep.groupby(run_id)):
    start = stretch["seconds_since_snap"].iloc[0] - 0.05
    end = stretch["seconds_since_snap"].iloc[-1] + 0.05
    ax_line.axvspan(start, end, color=bands[i % 2], lw=0, zorder=0)
    ax_line.text((start + end) / 2, y_top * 0.035, f"nearest coverage defender:\n{stretch['nearest_coverage_defender'].iloc[0]}",
                 ha="center", va="bottom", fontsize=9.5, color=INK, linespacing=1.3)
    if i > 0:
        ax_line.axvline(start, color=MUTED, lw=1, ls=":", zorder=1)
        ax_line.text(start + 0.04, y_top * 0.20, "nearest defender\nchanges here", fontsize=8.5, color=MUTED,
                     ha="left", va="bottom", linespacing=1.3)

# Frames outside the snap -> release window are drawn faded (context only).
ax_line.plot(sep["seconds_since_snap"], sep["distance_yd"], color="#B6BCC6", lw=1.5, marker="o", markersize=3,
             zorder=2, label="before the snap / after release (context only)")
ax_line.plot(window["seconds_since_snap"], window["distance_yd"], color=INK, lw=2.2, marker="o", markersize=4,
             zorder=3, label="snap to release (the supplied calculation)")

# Snap and pass release markers.
for x, label, align in [(0.0, "SNAP\n(play starts)", "right"), (release_sec, "PASS RELEASED\n(ball leaves the\nquarterback's hand)", "right")]:
    ax_line.axvline(x, color=HIGHLIGHT, lw=2.4, zorder=2)
    ax_line.text(x - 0.04, y_top * 0.985, label, ha=align, va="top", fontsize=9.5, fontweight="bold",
                 color=INK, linespacing=1.3)

# Three numbers read straight from the table: at snap, the smallest, at release.
ax_line.scatter([at_release["seconds_since_snap"]], [at_release["distance_yd"]], s=110, facecolor=HIGHLIGHT,
                edgecolor="white", linewidth=1.5, zorder=5)
ax_line.annotate(f"{at_snap['distance_yd']:.2f} yd at the snap", xy=(0, at_snap["distance_yd"]),
                 xytext=(0.12, at_snap["distance_yd"] - 1.0), fontsize=9.5, color=INK,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9))
ax_line.annotate(f"smallest: {smallest['distance_yd']:.2f} yd\nat {smallest['seconds_since_snap']:.1f} s",
                 xy=(smallest["seconds_since_snap"], smallest["distance_yd"]),
                 xytext=(smallest["seconds_since_snap"] - 0.75, smallest["distance_yd"] - 0.95), fontsize=9.5,
                 color=INK, linespacing=1.3, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9))
ax_line.annotate(f"{at_release['distance_yd']:.2f} yd\nat release", xy=(release_sec, at_release["distance_yd"]),
                 xytext=(release_sec + 0.1, at_release["distance_yd"] - 1.35), fontsize=10.5, fontweight="bold",
                 color=INK, linespacing=1.3, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9))

ax_line.set_xlabel("time since the snap (seconds)", fontsize=10.5, color=INK)
ax_line.set_ylabel("distance to the nearest coverage defender (yards)", fontsize=10.5, color=INK)
ax_line.set_title(f"2. {SELECTED_PLAYER}'s distance to the nearest coverage defender over time",
                  fontsize=12.5, fontweight="bold", color=INK, loc="left", pad=44)
ax_line.grid(axis="y", color="#E5E7EB", lw=0.8)
ax_line.set_axisbelow(True)
for side in ["top", "right"]:
    ax_line.spines[side].set_visible(False)
for side in ["left", "bottom"]:
    ax_line.spines[side].set_color("#9CA3AF")
ax_line.tick_params(colors=MUTED, labelsize=9.5)
ax_line.legend(loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=2, fontsize=8.5, frameon=False)

# ---- 4c. Notes --------------------------------------------------------------
ax_notes.axis("off")
changes = window["nearest_coverage_defender"].ne(window["nearest_coverage_defender"].shift()).sum() - 1
shows = (
    "WHAT THIS SHOWS\n"
    f"•  Left: all 22 players and the ball at the moment the pass is released. The orange line is the path\n"
    f"    {SELECTED_PLAYER} ran from the snap to that moment.\n"
    f"•  Right: for every 0.1 s, the straight-line distance from {SELECTED_PLAYER} to whichever coverage\n"
    f"    defender is closest. Higher = more space around him.\n"
    f"•  From snap to release the distance went from {at_snap['distance_yd']:.2f} yd, up to {largest['distance_yd']:.2f} yd at "
    f"{largest['seconds_since_snap']:.1f} s, down to {smallest['distance_yd']:.2f} yd\n"
    f"    at {smallest['seconds_since_snap']:.1f} s, and was {at_release['distance_yd']:.2f} yd at release.\n"
    f"•  The nearest defender is not one fixed person: it changed {changes} time(s) on this play. The line follows\n"
    f"    whoever is closest at each moment, so a jump or bend can come from a switch, not from one matchup."
)
cannot = (
    "WHAT THIS CANNOT ESTABLISH\n"
    "•  Whether a passing lane was open. This is distance to one defender only; it ignores defenders standing\n"
    "    between the quarterback and the receiver, the height and arc of the ball, and where the ball came down.\n"
    "•  Who was assigned to cover him, or whether anyone played well or badly. It is one play.\n"
    "•  Only players tagged \"Coverage\" count as defenders here (the supplied definition). Pass rushers\n"
    "    (defenders chasing the quarterback) are left out, even when one is physically closer.\n"
    "•  What happened at the catch: the tracking for this play ends 0.5 s after release, with no catch event.\n"
    "•  Positions are flat x/y dots, 10 per second. Body lean, reach and which way players face are not used."
)
ax_notes.text(0.0, 1.0, shows, fontsize=9.6, color=INK, va="top", ha="left", linespacing=1.5, transform=ax_notes.transAxes)
ax_notes.text(0.515, 1.0, cannot, fontsize=9.6, color=INK, va="top", ha="left", linespacing=1.5, transform=ax_notes.transAxes)

# ---------------------------------------------------------------------------
# 5. SAVE + PRINT THE NUMBERS SO YOU CAN CHECK THEM
# ---------------------------------------------------------------------------
out_dir = PROJECT_DIR / "output"
out_dir.mkdir(exist_ok=True)
stem = f"route_space_v1_{GAME_ID}_{PLAY_ID}_{SELECTED_PLAYER.lower().replace(' ', '_')}"
fig.savefig(out_dir / f"{stem}.png", dpi=130)
sep.to_csv(out_dir / f"{stem}.csv", index=False)

print(f"Offense {offense}, defense {defense}, playDirection = {play_direction}")
print(f"Snap frame {snap_frame}, release frame {release_frame}, snap to release = {release_sec:.1f} s")
print(sep.to_string(index=False))
print(f"\nSaved: {out_dir / (stem + '.png')}")
