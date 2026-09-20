import zipfile, collections, json, math, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
# a checkout of https://github.com/Skretzo/shortest-path; override with SHORTEST_PATH
SP_RES = Path(os.environ.get('SHORTEST_PATH') or ROOT / 'shortest-path') / 'src' / 'main' / 'resources'
GRAPH = Path(os.environ.get('TRAVEL_GRAPH') or ROOT / 'data' / 'osrs-travel-graph.json')
BUILD = Path(os.environ.get('BUILD_DIR') or ROOT / 'build')
if not (SP_RES / 'collision-map.zip').exists():
    sys.exit(f"no collision-map.zip under {SP_RES} — set SHORTEST_PATH to a shortest-path checkout")
Z = zipfile.ZipFile(SP_RES / 'collision-map.zip')
REG, FLAGS = 64, 2
regions = {}
for name in Z.namelist():
    if '_' not in name: continue
    rx, ry = map(int, name.split('_'))
    regions[(rx, ry)] = Z.read(name)

def bit(data, i):                      # BitSet.valueOf byte order: little-endian bytes, LSB first
    byte = i >> 3
    return byte < len(data) and (data[byte] >> (i & 7)) & 1

def flag(x, y, z, f):
    d = regions.get((x // REG, y // REG))
    if d is None: return False
    i = ((z * REG * REG + (y & 63) * REG + (x & 63)) * FLAGS) + f
    return bool(bit(d, i))

n = lambda x,y,z: flag(x,y,z,0)          # can step north
e = lambda x,y,z: flag(x,y,z,1)          # can step east
s = lambda x,y,z: n(x, y-1, z)
w = lambda x,y,z: e(x-1, y, z)
def neighbours(x, y, z):
    out = []
    if n(x,y,z): out.append((x,y+1))
    if s(x,y,z): out.append((x,y-1))
    if e(x,y,z): out.append((x+1,y))
    if w(x,y,z): out.append((x-1,y))
    if n(x,y,z) and e(x,y,z) and e(x,y+1,z) and n(x+1,y,z): out.append((x+1,y+1))
    if n(x,y,z) and w(x,y,z) and w(x,y+1,z) and n(x-1,y,z): out.append((x-1,y+1))
    if s(x,y,z) and e(x,y,z) and e(x,y-1,z) and s(x+1,y,z): out.append((x+1,y-1))
    if s(x,y,z) and w(x,y,z) and w(x,y-1,z) and s(x-1,y,z): out.append((x-1,y-1))
    return out

def walkable(x,y,z=0): return bool(neighbours(x,y,z))
def snap(x, y, z=0, r=25):
    if walkable(x,y,z): return (x,y)
    best=None
    for dx in range(-r,r+1):
        for dy in range(-r,r+1):
            if walkable(x+dx,y+dy,z):
                d=dx*dx+dy*dy
                if best is None or d<best[0]: best=(d,(x+dx,y+dy))
    return best[1] if best else None

def bfs(src, targets, z=0, cap=400000):
    tset = {t:None for t in targets}
    q = collections.deque([src]); dist = {src:0}
    left = set(targets)
    while q and left and len(dist) < cap:
        cur = q.popleft(); d = dist[cur]
        if cur in left:
            tset[cur] = d; left.discard(cur)
        for nb in neighbours(cur[0], cur[1], z):
            if nb not in dist:
                dist[nb] = d+1; q.append(nb)
    return tset, len(dist)

print("regions loaded:", len(regions))
# sanity: Lumbridge castle courtyard should be walkable, and the Falador wall should block
for (x,y,label) in [(3222,3218,"Lumbridge castle"),(2965,3380,"Falador centre"),(3057,3311,"Falador farm"),(2650,3366,"Ardougne farm")]:
    print(f"  {label} ({x},{y}) walkable={walkable(x,y)} snapped={snap(x,y)}")

g = json.load(open(GRAPH, encoding='utf-8'))
N = {n["id"]:n for n in g["nodes"]}
walks = [e for e in g["edges"] if e["mode"]=="walk"]
# group by source so one BFS serves several targets
from collections import defaultdict
bysrc = defaultdict(list)
for ed in walks: bysrc[ed["from"]].append(ed)
results = {}
for src, es in bysrc.items():
    a = N.get(src)
    if not a or "x" not in a: continue
    s0 = snap(a["x"], a["y"])
    if not s0: print("  no walkable tile near", a["name"]); continue
    tg = {}
    for ed in es:
        b = N.get(ed["to"])
        if not b or "x" not in b: continue
        t = snap(b["x"], b["y"])
        if t: tg[t] = ed
    got, explored = bfs(s0, list(tg.keys()))
    for t, d in got.items():
        results[(src, tg[t]["to"])] = d
    print(f"  {a['name']}: {len([1 for d in got.values() if d is not None])}/{len(tg)} reached, {explored} tiles explored")
BUILD.mkdir(parents=True, exist_ok=True)
out = BUILD / 'tile_dist.json'
json.dump({f"{k[0]}|{k[1]}":v for k,v in results.items()}, open(out,'w'))
print("wrote", out)
