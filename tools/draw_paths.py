import json, heapq, collections
from pathlib import Path
# transport tables and the collision decoder: search(), neighbours(), snap(), FREE, GRAPH
exec(open(Path(__file__).with_name('pathfind.py'), encoding='utf-8').read())
def search_path(src, targets, radius=8, cap=500000):
    s0=snap(src[0],src[1])
    if not s0: return {}
    start=(s0[0],s0[1],0); dist={start:0.0}; prev={start:None}
    pq=[(0.0,start)]; out={}; left=set(targets)
    while pq and left and len(dist)<cap:
        dd,cur=heapq.heappop(pq)
        if dd>dist.get(cur,1e9)+1e-9: continue
        x,y,pl=cur
        for t in list(left):
            if pl==0 and abs(x-t[0])<=radius and abs(y-t[1])<=radius:
                pts=[]; c=cur
                while c: pts.append((c[0],c[1])); c=prev[c]
                out[t]=pts[::-1]; left.discard(t)
        nxt=[((nx,ny,pl),SEC_PER_TILE) for nx,ny in neighbours(x,y,pl)]
        for dest,cost,lvl in FREE.get(cur,[]): nxt.append((dest,cost))
        for v,cost in nxt:
            nd=dd+cost
            if nd<dist.get(v,1e9)-1e-9: dist[v]=nd; prev[v]=cur; heapq.heappush(pq,(nd,v))
    return out
def thin(pts, step=8):
    out=[pts[0]]
    for i,pt in enumerate(pts):
        if i%step==0 and pt!=out[-1]: out.append(pt)
    if pts[-1]!=out[-1]: out.append(pts[-1])
    return out
G=json.load(open(GRAPH, encoding='utf-8'))
N={q["id"]:q for q in G["nodes"]}
todo=[q for q in G["edges"] if q["mode"]=="walk" and not q.get("path")]
bysrc=collections.defaultdict(list)
for q in todo: bysrc[q["from"]].append(q)
done=0
for src,es in bysrc.items():
    a=N[src]; tg={(N[q["to"]]["x"],N[q["to"]]["y"]):q for q in es}
    got=search_path((a["x"],a["y"]), list(tg.keys()))
    for t,pts in got.items():
        tg[t]["path"]=[[int(x),int(y)] for x,y in thin(pts)]; done+=1
left=[q for q in G["edges"] if q["mode"]=="walk" and not q.get("path")]
print(f"drew {done}; still without a path: {len(left)}")
for q in left: print("   ",N[q['from']]['name'],"↔",N[q['to']]['name'])
json.dump(G,open(GRAPH,'w',encoding='utf-8'))
print("updated", GRAPH)
