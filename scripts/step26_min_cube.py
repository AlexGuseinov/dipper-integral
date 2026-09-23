"""Smallest bit-aligned cube with a certificate, per round, within MP-EL.

Write a cube as I = {0..63} minus Z (Z = constant bits). If (I, r, j) has no
trail, then by the monotonicity lemma no 63-dimensional cube containing I has a
trail for j, so every p in Z must lie in P_j = {p : the cube with constant bit p
certifies j}. Certified Z form a down-closed family, so the largest certified Z
is found level by level (a set is a candidate only if all its subsets of one size
smaller are certified). Every "not certified" answer is a trail and is validated
by the CNF-independent checker, so the minimality statement rests on checked
trails plus the certificates it reports.
Usage: step26_min_cube.py <mode> <rounds,...>
"""
import itertools, json, sys, time
sys.path.insert(0, ".")
from pysat.solvers import Solver
from dipper.models import build
from dipper.witness import check_trail

mode = sys.argv[1]
rounds = [int(x) for x in sys.argv[2].split(",")]
import glob
maxc = {}
for f in glob.glob("results/step3_maximal_cubes_*.json"):
    d = json.load(open(f))
    if mode in d and "mp" in d[mode]:
        maxc.update(d[mode]["mp"])
out = {}
for r in rounds:
    t0 = time.time()
    ref = maxc.get(str(r), {}).get("balanced_by_const_bit")
    m, outv = build(None, r, "mp", mode)
    s = Solver(name="cadical153", bootstrap_with=m.cl)
    queries, trails_checked, trails_bad = 0, 0, 0

    def certified(Z, j):
        global queries, trails_checked, trails_bad
        queries += 1
        I = [i for i in range(64) if i not in Z]
        a = [m.inputs[i] if i in I else -m.inputs[i] for i in range(64)]
        a += [outv[i] if i == j else -outv[i] for i in range(64)]
        if not s.solve(assumptions=a):
            return True
        val = set(l for l in s.get_model() if l > 0)
        trail = [sum(1 << i for i, v in enumerate(vs) if v in val) for _, vs in m.trace]
        ok, _ = check_trail(trail, I, j, mode)
        trails_checked += 1; trails_bad += (not ok)
        return False

    # the pruning uses the 63-dimensional answers: re-derive and validate every "not certified" one
    mism, bal = 0, {p: set() for p in range(64)}
    for j in range(64):
        for p in range(64):
            if certified({p}, j):
                bal[p].add(j)
    if ref is not None:
        mism = sum(bal[p] != set(ref[str(p)]) for p in range(64))
    else:
        mism = "no stored 63-dim result"
    best = {}                                        # j -> (max |Z|, all certified Z of that size)
    for j in range(64):
        P = sorted(p for p, b in bal.items() if j in b)
        if not P:
            continue
        level = [frozenset([p]) for p in P]          # certified by the 63-dim results
        best[j] = (1, [sorted(z) for z in level])
        k = 1
        while level:
            cert_set = set(level)
            cand = set()
            for A in level:
                for p in P:
                    if p > max(A):
                        B = A | {p}
                        if all((B - {q}) in cert_set for q in B):
                            cand.add(B)
            nxt = [B for B in sorted(cand, key=sorted) if certified(B, j)]
            k += 1
            if nxt:
                best[j] = (k, [sorted(z) for z in nxt])
            level = nxt
    s.delete()
    mz = max((v[0] for v in best.values()), default=0)
    out[r] = {"max_constant_bits": mz, "min_dimension": 64 - mz,
              "bits_at_min": {j: v[1] for j, v in best.items() if v[0] == mz},
              "per_bit_max_constant": {j: v[0] for j, v in best.items()},
              "mismatch_with_63dim_results": mism, "queries": queries, "trails_checked": trails_checked, "trails_failed": trails_bad,
              "secs": round(time.time() - t0, 1)}
    print(mode, r, {k: v for k, v in out[r].items() if k != "per_bit_max_constant"}, flush=True)
json.dump(out, open(f"results/step26_min_cube_{mode}.json", "w"), indent=1)
