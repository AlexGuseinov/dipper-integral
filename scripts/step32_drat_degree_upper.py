"""DRAT certificates for the certified degree upper bounds of step6.

deg_x S^(r)_j <= D is certified by unsatisfiability of the exact-MP model with a free
input mask of Hamming weight >= D+1 and output e_j (step6_degree.py). For every
(variant, round, bit) of results/step25_degree_summary.json the instance for D = the
recorded upper bound is written out (model clauses, the totaliser that counts the input
weight, and the unit clauses), re-solved by an external CaDiCaL with a DRAT proof, and
the proof is checked by drat-trim.
Usage: step32_drat_degree_upper.py <cadical> <drat-trim> <modes> <outfile>"""
import json, os, sys, time
sys.path.insert(0, ".")
from pysat.card import ITotalizer
from dipper.models import build
from dipper.drat import Drat

CAD, DT, MODES, OUT = sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4]
D = Drat(CAD, DT)
summ = json.load(open("results/step25_degree_summary.json"))["per_bit"]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
for k in sorted(summ, key=lambda s: (s.split("|")[0], int(s.split("|")[1]))):
    mode, r = k.split("|")
    if mode not in MODES or k in res:
        continue
    t0 = time.time()
    m, out = build(None, int(r), "mp", mode)
    tot = ITotalizer(lits=[-v for v in m.inputs], ubound=64, top_id=m.pool.top)
    base = Drat.base(m.cl + tot.cnf.clauses)
    st = {"instances": 0, "unsat": 0, "verified": 0, "max_secs": 0.0}
    for j in range(64):
        U = summ[k][str(j)]["upper"]
        units = [[out[i] if i == j else -out[i]] for i in range(64)] + [[-tot.rhs[64 - (U + 1)]]]
        rr = D.check(base, units)
        st["instances"] += 1; st["unsat"] += rr["status"] == "UNSAT"; st["verified"] += bool(rr["verified"])
        st["max_secs"] = max(st["max_secs"], rr["secs"])
    tot.delete()
    st["certified"] = st["verified"] == st["instances"] == 64
    st["secs"] = round(time.time() - t0, 1)
    res[k] = st
    print(k, st, flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
print("TOTAL", {f: sum(v[f] for v in res.values()) for f in ("instances", "unsat", "verified")})
