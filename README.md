# OSRS Farm Run Planner

A single-page tool that works out the fastest herb, tree, fruit tree and hardwood
farm run for your account, and draws it on the game map.

**Live site:** https://irpepper.github.io/osrs-farm-run-planner/

## What makes it different

Routes are solved on a real travel graph rather than a hand-written list of "best teleports".

- **88 nodes, 200+ edges** — every patch, teleport landing, spirit tree, fairy ring,
  mushtree and quetzal stop, with real world coordinates.
- **Walking times are pathfound, not estimated.** Every walk edge is a breadth-first
  search over the game's collision map, so routes go around Falador's wall and through
  the Gnome maze instead of cutting straight lines. Times convert at running speed
  (2 tiles per 0.6s tick) plus 3s for doors and clicks.
- **Teleports are edges from anywhere**, which is what lets the router mix walking,
  hops and teleports freely — then a Held-Karp pass orders the stops that benefit from it.
- **Shortcuts and escorts included** — 5,600 transitions from the Shortest Path plugin's
  tables, including Agility shortcuts gated on your level, and Elkoy through the maze.

## Features

- Levels, quests, diaries and per-item transport toggles (each piece of jewelry separately)
- Per-stop unlocks for spirit trees, mushtrees and quetzal destinations
- Character import: levels from Wise Old Man by name, quests and diaries by pasting WikiSync data
- Choose where the run starts, and a "minimise teleports" mode that penalises rune-burning spells
- Tabs: **Route**, **Graph** (force-directed, with best travel to every node),
  **Map** (pan and zoom, numbered stops, real paths), **Hardwood**, and **Edit graph**
  for switching individual nodes or edges off by hand
- Everything is stored in your browser; no accounts, no backend

## Running it

`index.html` is entirely self-contained — the graph, the map image and all code are inlined.
Open the file, or serve the folder:

```sh
python3 -m http.server 8000
```

## Publishing to GitHub Pages

```sh
gh repo create osrs-farm-run-planner --public --source=. --remote=origin --push
gh api -X POST repos/:owner/osrs-farm-run-planner/pages -f 'source[branch]=main' -f 'source[path]=/'
```

Or in the web UI: **Settings → Pages → Source: Deploy from a branch → main / (root)**.

## Data and credits

- Collision map and transport tables from the
  [Shortest Path](https://github.com/Skretzo/shortest-path) RuneLite plugin (BSD 2-Clause).
- Map tiles, patch coordinates and requirements from the
  [OSRS Wiki](https://oldschool.runescape.wiki/) (CC BY-NC-SA 3.0).
- Player data from [Wise Old Man](https://wiseoldman.net/) and
  [WikiSync](https://runescape.wiki/w/RuneScape:WikiSync).
- Old School RuneScape is a trademark of Jagex Ltd. This is an unofficial fan tool.

Travel times are estimates for comparing routes, not exact tick counts.

## Known gaps

- Drawn map paths use doors and gates only, so a route timed via an Agility shortcut may
  show the long way round.
- Diary teleports with daily charge limits (Explorer's ring, Ardougne cloak) are treated
  as unlimited.
- The Zanaris shed walk is a manual estimate; it needs a staff in hand, which the
  pathfinder skips.
