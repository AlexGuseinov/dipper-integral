"""DRAT certificates for the certified bits of the two minimal six-round cubes of Dipper
(dimension 60; constant nibble {4,5,6,7} or {12,13,14,15}), as found by step26.
Each (cube, bit) certificate is the UNSAT answer of MP-EL with input 1_I and output e_j.
Usage: step33_drat_min_cubes.py <cadical> <drat-trim>"""
import ast, json, sys
sys.path.insert(0, ".")
from dipper.models import build
from dipper.drat import Drat

D = Drat(sys.argv[1], sys.argv[2])
rec = json.load(open("results/step26_min_cube_add.json"))["6"]
rec = ast.literal_eval(rec) if isinstance(rec, str) else rec
cubes = {}
for j, lst in rec["bits_at_min"].items():
    for const in lst:
        cubes.setdefault(tuple(const), []).append(int(j))
out = {}
for const, bits in sorted(cubes.items()):
    act = sorted(set(range(64)) - set(const))
    m, o = build(set(act), 6, "mp", "add")
    base = Drat.base(m.cl)
    res = {}
    for j in sorted(bits):
        r = D.check(base, [[o[i] if i == j else -o[i]] for i in range(64)])
        res[j] = r
    out[",".join(map(str, const))] = {"bits": sorted(bits), "results": res,
                                     "all_verified": all(r["status"] == "UNSAT" and r["verified"] for r in res.values())}
    print(const, sorted(bits), out[",".join(map(str, const))]["all_verified"], flush=True)
json.dump(out, open("results/step33_drat_min_cubes.json", "w"), indent=1)
