import re, json, heapq, collections
from pathlib import Path
# collision decoder: neighbours(), snap(), plus SP_RES / GRAPH / BUILD — stop before it loads the graph
exec(open(Path(__file__).with_name('collision.py'), encoding='utf-8').read().split("g = json.load")[0])
RES = SP_RES / 'transports'
SEC_PER_TILE = 0.3      # 2 tiles per 0.6s tick

def load_transitions():
    free, agi = collections.defaultdict(list), collections.defaultdict(list)
    kept=skipped=0
    for fn in ['transports.tsv','agility_shortcuts.tsv']:
        head=None
        for line in open(RES / fn, encoding='utf-8'):
            if line.startswith('#'):
                if 'Origin' in line: head=line.lstrip('# ').rstrip('\n').split('\t')
                continue
            if not line.strip() or not head: continue
            c=line.rstrip('\n').split('\t')
            def col(name): 
                k=head.index(name) if name in head else -1
                return c[k] if 0<=k<len(c) else ''
            mo=re.match(r'(\d+)\s+(\d+)\s+(\d+)', c[0] if c else '')
            md=re.match(r'(\d+)\s+(\d+)\s+(\d+)', col('Destination'))
            if not mo or not md: continue
            if col('Items').strip(): skipped+=1; continue          # needs an item in hand
            skills=col('Skills').strip()
            lvl=0
            if skills:
                ms=re.findall(r'(\d+)\s+(\w+)', skills)
                if any(s.lower()!='agility' for _,s in ms): skipped+=1; continue
                lvl=max((int(n) for n,_ in ms), default=0)
            dur=col('Duration').strip()
            cost=max(0.6, (float(dur) if dur.replace('.','',1).isdigit() else 1)*0.6)
            o=tuple(map(int,mo.groups())); d=tuple(map(int,md.groups()))
            (free if lvl==0 else agi)[o].append((d,cost,lvl)); kept+=1
    return free, agi, kept, skipped

FREE, AGI, kept, skipped = load_transitions()
print(f"transitions: {kept} usable ({sum(len(v) for v in FREE.values())} free, {sum(len(v) for v in AGI.values())} agility), {skipped} skipped for items or other skills")

def search(src, targets, use_agility, radius=8, cap=500000):
    s0=snap(src[0],src[1])
    if not s0: return {}
    start=(s0[0],s0[1],0)
    dist={start:0.0}; maxagi={start:0}
    pq=[(0.0,start)]; out={}; left=set(targets)
    while pq and left and len(dist)<cap:
        d,(x,y,p)=heapq.heappop(pq)
        if d>dist.get((x,y,p),1e9)+1e-9: continue
        for t in list(left):
            if p==0 and abs(x-t[0])<=radius and abs(y-t[1])<=radius:
                out[t]=(d, maxagi[(x,y,p)]); left.discard(t)
        nxt=[((nx,ny,p), SEC_PER_TILE, 0) for nx,ny in neighbours(x,y,p)]
        for dest,cost,lvl in FREE.get((x,y,p),[]): nxt.append((dest,cost,0))
        if use_agility:
            for dest,cost,lvl in AGI.get((x,y,p),[]): nxt.append((dest,cost,lvl))
        for v,cost,lvl in nxt:
            nd=d+cost
            if nd < dist.get(v,1e9)-1e-9:
                dist[v]=nd; maxagi[v]=max(maxagi[(x,y,p)],lvl); heapq.heappush(pq,(nd,v))
    return out
