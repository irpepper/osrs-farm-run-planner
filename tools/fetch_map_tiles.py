import urllib.request, json, io, os, concurrent.futures as cf
from pathlib import Path
from PIL import Image
V="2026-08-12_a"; Z=0; TILE=256   # zoom 0: 1 pixel per world tile, 256 tiles per image
ROOT=Path(__file__).resolve().parent.parent
GRAPH=Path(os.environ.get('TRAVEL_GRAPH') or ROOT/'data'/'osrs-travel-graph.json')
BUILD=Path(os.environ.get('BUILD_DIR') or ROOT/'build')
g=json.load(open(GRAPH, encoding='utf-8'))
xs=[n["x"] for n in g["nodes"]]; ys=[n["y"] for n in g["nodes"]]
# main landmass only; Prifddinas and Zanaris sit in their own map areas
pts=[(n["x"],n["y"]) for n in g["nodes"] if n["y"]<4200]
x0,x1=min(p[0] for p in pts)-60, max(p[0] for p in pts)+60
y0,y1=min(p[1] for p in pts)-60, max(p[1] for p in pts)+60
tx0,tx1=x0//TILE, x1//TILE; ty0,ty1=y0//TILE, y1//TILE
print(f"world box {x0}-{x1} x {y0}-{y1}; tiles {tx0}-{tx1} by {ty0}-{ty1} = {(tx1-tx0+1)*(ty1-ty0+1)} images")
def fetch(t):
    tx,ty=t
    u=f"https://maps.runescape.wiki/osrs/versions/{V}/tiles/rendered/0/{Z}/0_{tx}_{ty}.png"
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"farm-planner/1.0 (route planner)"}),timeout=25)
        return t, r.read()
    except Exception: return t, None
todo=[(tx,ty) for tx in range(tx0,tx1+1) for ty in range(ty0,ty1+1)]
canvas=Image.new("RGB",((tx1-tx0+1)*TILE,(ty1-ty0+1)*TILE),(11,14,10))
ok=0
with cf.ThreadPoolExecutor(8) as ex:
    for (tx,ty),data in ex.map(fetch,todo):
        if not data: continue
        ok+=1
        im=Image.open(io.BytesIO(data)).convert("RGB")
        canvas.paste(im,((tx-tx0)*TILE,(ty1-ty)*TILE))   # world y grows north, images grow down
print(f"{ok}/{len(todo)} tiles fetched")
BUILD.mkdir(parents=True, exist_ok=True)
canvas.save(BUILD/"map_full.png")
print("full canvas", canvas.size, "->", BUILD/"map_full.png")
