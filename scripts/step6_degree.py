"""Certified upper bounds on the algebraic degree (in the plaintext bits, round
keys free) of every output bit of r-round Dipper and of the analysis variants.

deg_x(S^(r)_j) <= d  is certified by unsatisfiability of the exact-MP model with
a free input mask u of Hamming weight >= d+1 and output e_j (no monomial x^u with
wt(u) > d can appear). Bits are grouped by the word (A,B,C,D) of the last ARX
layer that produced them."""
import json, sys, time
sys.path.insert(0, ".")
from pysat.solvers import Solver
from pysat.card import ITotalizer
from dipper.models import build
from dipper.cipher import PERM_INV

MODES = sys.argv[1].split(",") if len(sys.argv) > 1 else ["add", "xor", "none"]
RMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 7
BUDGET = 2_000_000
WORD = "DCBA"


def degree_bounds(mode, r):
    m, out = build(None, r, "mp", mode)
    tot = ITotalizer(lits=[-v for v in m.inputs], ubound=64, top_id=m.pool.top)
    s = Solver(name="cadical153", bootstrap_with=m.cl + tot.cnf.clauses)
    res, timeouts = {}, 0
    for j in range(64):
        base = [out[i] if i == j else -out[i] for i in range(64)]

        def sat_at_least(d):              # trail from some u with wt(u) >= d ?
            nonlocal timeouts
            if d == 0:
                assum = base
            else:
                assum = base + [-tot.rhs[64 - d]]   # #zeros <= 64-d
            s.conf_budget(BUDGET)
            v = s.solve_limited(assumptions=assum)
            if v is None:
                timeouts += 1
                return True                # unresolved -> treat as possible (sound)
            return v
        lo, hi = 0, 64                     # invariant: sat(lo) (or lo=0), unsat(hi+1)
        if not sat_at_least(0):
            res[j] = -1                    # constant output (never happens)
            continue
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if sat_at_least(mid):
                lo = mid
            else:
                hi = mid - 1
        res[j] = lo
    s.delete()
    return res, timeouts


if __name__ == "__main__":
    out = {}
    for mode in MODES:
        out[mode] = {}
        for r in range(1, RMAX + 1):
            t0 = time.time()
            res, to = degree_bounds(mode, r)
            by_word = {w: sorted(res[j] for j in range(64) if WORD[PERM_INV[j] // 16] == w) for w in "ABCD"}
            out[mode][r] = {"per_bit": res, "timeouts": to,
                            "by_word_min_max": {w: [v[0], v[-1]] for w, v in by_word.items()},
                            "seconds": round(time.time() - t0, 1)}
            print(mode, r, {w: f"{v[0]}-{v[-1]}" for w, v in by_word.items()}, "timeouts", to,
                  f"{time.time()-t0:.0f}s"); sys.stdout.flush()
            json.dump(out, open(f"results/step6_degree_{'_'.join(MODES)}.json", "w"), indent=1)
            if min(res.values()) >= 64:
                break
