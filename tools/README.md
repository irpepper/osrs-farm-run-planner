# Build tools

These regenerate the travel graph. They are not needed to run the site — `index.html`
is self-contained and already has the graph and map inlined.

| Script | What it does |
|---|---|
| `collision.py` | Decodes the collision map shipped with the RuneLite Shortest Path plugin (2 bits per tile: can-step-north, can-step-east) and exposes `neighbours()` / `snap()`. |
| `pathfind.py` | Loads the plugin's transport tables (doors, gates, stiles, ladders, NPC escorts, Agility shortcuts) and runs Dijkstra in seconds over tiles plus those transitions. |
| `draw_paths.py` | Records the tile-by-tile route for every walk edge, thinned to every 8th tile, so the map can draw real paths. |
| `fetch_map_tiles.py` | Downloads OSRS Wiki map tiles and composites them into the background image. |

Requirements: Python 3.11+, `pillow`, and a checkout of
[Skretzo/shortest-path](https://github.com/Skretzo/shortest-path) for `collision-map.zip`
and the `transports/*.tsv` tables.

`pathfind.py` and `draw_paths.py` pull in the scripts above them, so run any of them
directly — `python tools/draw_paths.py` — from anywhere. Paths default to this repo and
can be overridden with environment variables:

| Variable | Default | Used for |
|---|---|---|
| `SHORTEST_PATH` | `./shortest-path` | the shortest-path checkout holding `src/main/resources` |
| `TRAVEL_GRAPH` | `./data/osrs-travel-graph.json` | the graph to read (and, for `draw_paths.py`, rewrite in place) |
| `BUILD_DIR` | `./build` | `tile_dist.json` and `map_full.png` output |

Speed model: running is 2 tiles per 0.6s tick (3.33 tiles/s), plus 3s per edge for doors and clicks.
