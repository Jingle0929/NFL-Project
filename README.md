# NFL Passing Space Analysis Tool

## What this is (3–5 sentence summary)

Using NFL Big Data Bowl player tracking data, I built a "passing space" analysis tool that quantifies the space on the field at the moment of each pass: how far a receiver is from the nearest coverage defender (separation), which team controls each part of the field (Voronoi control area), all combined into a single-page **play card** and wrapped in an interactive explorer that covers an entire 122-game slate. It reveals a counterintuitive pattern — **the most open receiver at the moment of release is often not the one the quarterback throws to**, because deep passes rely on timing and ball placement and are frequently completed into very tight windows (game-wide median separation of about 2.85 yards). The tool is for **coaches and scouts**: it lets them quickly review the passing decision and spatial structure of a given play without reading raw tracking frames.

## Deliverables

- **Code**: ten sequential Jupyter notebooks under `notebooks/` (load data → spatial metrics → play card → interactive tool), plus `export_play_cards.py` (export static images) and `route_space_v1.py` (a polished single-metric demo).
- **Output**: play card PNGs under `output/` (see below).
- **Technical appendix**: the full stage-by-stage development log is in [`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md).

## Output examples

Two representative play cards (both deep passes, one complete and one incomplete):

- `output/play_card_2021090900_137_deep_pass_complete.png` — completed deep pass, demonstrating "the most open receiver is not the target."
- `output/play_card_2021090900_97_deep_pass_incomplete.png` — incomplete deep pass, receiver tightly covered.

Each play card has four panels: (1) player positions at the snap, (2) Voronoi control area, (3) separation over time, (4) passing lane (reference only).

There is also a single-metric demo in `output/route_space_v1_2021090900_137_amari_cooper.png` (plus its `.csv`), focused on one route runner.

## How to run

Requirements: Python 3.13, with the dataset located at the path configured in `config.py` (`DATA_DIR`).

```bash
cd /Users/jingleliao/Downloads/nfl_passing_project
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# Set the data path (or edit the default in config.py)
export NFL_DATA_DIR="/path/to/nfl-big-data-bowl.../data"

# Re-generate the output play card PNGs
.venv/bin/python export_play_cards.py

# Or open the interactive tool (dropdowns appear only when run live in Jupyter)
.venv/bin/jupyter notebook notebooks/10_multi_game_explorer.ipynb
```

## Methods and honest limitations

- **separation** (receiver distance to nearest coverage defender) and the **Voronoi control area** (spatial ownership of the whole field) are the tool's two primary metrics, both validated against the data.
- **passing lane** (blockers along the throwing line) is a 2D metric and is **unreliable for deep passes**: it only looks at how close a defender is to the straight line, ignoring the height and arc of the ball. An attempt to fix it by extrapolating receiver motion still failed when checked against the data (see stage 8 in `DEVELOPMENT_LOG.md`). The play card therefore labels this panel "reference only."
- Guiding principle throughout: **compute from the data first, draw conclusions second** — no assumptions about whether a player performed well or badly. The raw dataset is read-only and never modified.
