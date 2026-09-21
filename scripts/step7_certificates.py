"""Checkable artifacts for every boundary result.

UNSAT side (a property IS certified): DRAT proofs from an external CaDiCaL,
checked by drat-trim, for
  * Dipper r=6: every certified (63-cube, bit) pair and the 2^60 frontier cube,
  * Dipper r=5: the two word-cube properties (A, C) and the r=3,4,5 frontier cubes,
  * Dipper-XOR r=9 and Dipper-no-add r=10: every certified (63-cube, bit) pair.
SAT side (NO certificate): for every (63-cube, bit) pair at Dipper r=7,
Dipper-XOR r=10 and Dipper-no-add r=11 (3 x 4096 queries), the trail found by the
solver is validated by the CNF-independent checker dipper/witness.py.

Usage: python3 scripts/step7_certificates.py <cadical> <drat-trim> <outdir>"""
import json, os, subprocess, sys, time
sys.path.insert(0, ".")
from pysat.solvers import Solver
from dipper.models import build
from dipper.witness import check_trail
from dipper.proofs import unsat_proof

CAD, DRAT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)


def load(fn, mode, r):
    return json.load(open(fn))[mode]["mp"][str(r)]["balanced_by_const_bit"]


targets = []
for mode, fn, r in (("add", "results/step3_maximal_cubes_add.json", 6),
                    ("xor", "results/step3_maximal_cubes_xor_r8-9-10.json", 9),
                    ("none", "results/step3_maximal_cubes_none_r8-9-10-11.json", 10)):
    for p, bits in load(fn, mode, r).items():
        targets += [(mode, r, sorted(set(range(64)) - {int(p)}), j) for j in bits]
fr = json.load(open("results/step3_frontier_add_mp.json"))
for r, v in fr.items():
    targets += [("add", int(r), v["active"], j) for j in v["balanced"]]
for w, lo in (("A", 48), ("C", 16)):
    m, out = build(set(range(lo, lo + 16)), 5, "mp", "add")
    s = Solver(name="cadical153", bootstrap_with=m.cl)
    for j in range(64):
        if not s.solve(assumptions=[out[i] if i == j else -out[i] for i in range(64)]):
            targets.append(("add", 5, list(range(lo, lo + 16)), j))
    s.delete()

rows, t0 = [], time.time()
for mode, r, act, j in targets:
    row = unsat_proof(act, r, j, mode, OUT, CAD, DRAT)
    rows.append(row)
    if row["drat_trim"] != "VERIFIED":
        print("FAILED", row); sys.stdout.flush()
print(f"UNSAT proofs: {len(rows)}, verified: {sum(r['drat_trim']=='VERIFIED' for r in rows)}, "
      f"{time.time()-t0:.0f}s"); sys.stdout.flush()

wit, t0 = {}, time.time()
for mode, r in (("add", 7), ("xor", 10), ("none", 11)):
    n_ok = n_sat = 0
    for p in range(64):
        act = set(range(64)) - {p}
        m, out = build(act, r, "mp", mode)
        s = Solver(name="cadical153", bootstrap_with=m.cl)
        for j in range(64):
            if not s.solve(assumptions=[out[i] if i == j else -out[i] for i in range(64)]):
                continue
            n_sat += 1
            val = {abs(l): l > 0 for l in s.get_model()}
            masks = [sum(1 << i for i, v in enumerate(vs) if val[v]) for _, vs in m.trace]
            ok, why = check_trail(masks, sorted(act), j, mode)
            n_ok += ok
            if not ok:
                print("INVALID TRAIL", mode, r, p, j, why)
        s.delete()
    wit[f"{mode}/r{r}"] = {"queries": 64 * 64, "sat": n_sat, "trails_valid": n_ok}
    print(mode, r, wit[f"{mode}/r{r}"], f"{time.time()-t0:.0f}s"); sys.stdout.flush()

tool = lambda c: subprocess.run(["git", "-C", os.path.dirname(os.path.dirname(c)) if c.endswith("build/cadical") else os.path.dirname(c),
                                 "log", "-1", "--format=%H"], capture_output=True, text=True).stdout.strip()
json.dump({"tools": {"cadical_commit": tool(CAD), "drat_trim_commit": tool(DRAT),
                     "cadical_version": subprocess.run([CAD, "--version"], capture_output=True, text=True).stdout.strip()},
           "unsat": {"count": len(rows), "verified": sum(r["drat_trim"] == "VERIFIED" for r in rows),
                     "total_proof_bytes": sum(r["proof_bytes"] for r in rows), "rows": rows},
           "sat_witnesses": wit},
          open("results/step7_certificates.json", "w"), indent=1)
