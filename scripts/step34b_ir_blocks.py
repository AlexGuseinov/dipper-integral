"""Probe (not used in the paper's claims): strongly connected components of the graphs of
step34 and the invertibility of their diagonal blocks (entries counted, cap 2000).
Result: most blocks are singular; almost all singular blocks are pairs of input monomials
that differ inside one nibble (equal rows). Output: results/step34b_ir_blocks.json."""
import glob, json, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter
SP="results"
E = json.load(open(SP+"/step34_ir_edges.json"))
P = {}
for f in glob.glob("results/step21_presence_*_p.json"):
    for p, rec in json.load(open(f)).items():
        if rec.get("done"):
            for j, b in rec["bits"].items(): P[(int(p), int(j))] = [int(m, 16) for m in b["pattern"]]
for j, v in json.load(open("results/step20_presence_r7_complete.json"))["per_bit"].items():
    P.setdefault((0, int(j)), [int(m, 16) for m in v["pattern"]])
sys.setrecursionlimit(10000)
def sccs(G):
    idx, low, st, on, comps, k = {}, {}, [], set(), [], [0]
    def sc(v):
        idx[v]=low[v]=k[0]; k[0]+=1; st.append(v); on.add(v)
        for w in G[v]:
            if w not in idx: sc(w); low[v]=min(low[v],low[w])
            elif w in on: low[v]=min(low[v],idx[w])
        if low[v]==idx[v]:
            c=[]
            while True:
                w=st.pop(); on.discard(w); c.append(w)
                if w==v: break
            comps.append(sorted(c))
    for v in G:
        if v not in idx: sc(v)
    return comps
def rank(rows, n):
    rows=list(rows); r=0
    for b in range(n):
        piv=next((i for i in range(r,len(rows)) if rows[i]>>b&1),None)
        if piv is None: continue
        rows[r],rows[piv]=rows[piv],rows[r]
        for i in range(len(rows)):
            if i!=r and rows[i]>>b&1: rows[i]^=rows[r]
        r+=1
    return r
c = TrailCounter(None, 7); inp=c.m.inputs
def count(V, q, j, cap):
    a=[c.out[i] if i==j else -c.out[i] for i in range(64)]
    a+=[c.kv[t][i] if (m>>i)&1 else -c.kv[t][i] for t,m in enumerate(V) for i in range(64)]
    a+=[-inp[i] if i==q else inp[i] for i in range(64)]
    c._sel+=1; sel=c.m.pool.id(("sel",c._sel)); n=0
    while n<cap and c.s.solve(assumptions=a+[sel]):
        val={abs(l):l>0 for l in c.s.get_model()}
        c.s.add_clause([-sel]+[-v if val[v] else v for v in c.proj]); n+=1
    capped = n>=cap and c.s.solve(assumptions=a+[sel]); c.s.add_clause([-sel])
    return None if capped else n
stats={"blocks":0,"sizes":{},"invertible":0,"singular":0,"uncountable":0}
bad=[]
t0=time.time()
for j in range(64):
    G={p:E[f"{p},{j}"] for p in range(64)}
    for comp in sccs(G):
        if len(comp)==1: continue
        stats["blocks"]+=1; stats["sizes"][len(comp)]=stats["sizes"].get(len(comp),0)+1
        M=[]; unc=False
        for p in comp:
            row=0
            for b,q in enumerate(comp):
                if q!=p and q not in G[p]: continue
                n=count(P[(p,j)], q, j, 2000)
                if n is None: unc=True; break
                row|=(n&1)<<b
            if unc: break
            M.append(row)
        if unc: stats["uncountable"]+=1; bad.append((j,comp,"unc")); continue
        if rank(M,len(comp))==len(comp): stats["invertible"]+=1
        else: stats["singular"]+=1; bad.append((j,comp,"sing"))
    print(j, stats, round(time.time()-t0), flush=True)
json.dump({"stats":stats,"bad":bad}, open(SP+"/step34b_ir_blocks.json","w"))
