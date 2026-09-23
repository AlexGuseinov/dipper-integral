"""Probe (not used in the paper's claims): towards the integral-resistance property of
Hebborn et al. (ASIACRYPT 2021) for 7-round Dipper, with RK_1 as whitening key.
For each output bit j, the matrix B_j has rows = the presence patterns v^(p,j) of step20/21
(v_1 = 0) and columns = the 64 input monomials x^(e_bar_q). Edge p -> q (q != p) if pattern
v^(p,j) has a trail from x^(e_bar_q) to e_j. Output: results/step34_ir_edges.json."""
import glob, json, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter
P = {}
for f in glob.glob("results/step21_presence_*_p.json"):
    for p, rec in json.load(open(f)).items():
        if rec.get("done"):
            for j, b in rec["bits"].items(): P[(int(p), int(j))] = [int(m, 16) for m in b["pattern"]]
for j, v in json.load(open("results/step20_presence_r7_complete.json"))["per_bit"].items():
    P.setdefault((0, int(j)), [int(m, 16) for m in v["pattern"]])
assert len(P) == 4096
c = TrailCounter(None, 7); inp, out = c.m.inputs, c.out
t0 = time.time(); edges = {}
for j in range(64):
    oa = [out[i] if i == j else -out[i] for i in range(64)]
    for p in range(64):
        V = P[(p, j)]
        ka = [c.kv[t][i] if (m >> i) & 1 else -c.kv[t][i] for t, m in enumerate(V) for i in range(64)]
        E = []
        for q in range(64):
            if q == p: continue
            ia = [-inp[i] if i == q else inp[i] for i in range(64)]
            if c.s.solve(assumptions=oa + ka + ia): E.append(q)
        edges[(p, j)] = E
    print(j, sum(len(edges[(p, j)]) for p in range(64)), round(time.time()-t0), flush=True)
json.dump({f"{p},{j}": e for (p, j), e in edges.items()}, open("results/step34_ir_edges.json", "w"))
