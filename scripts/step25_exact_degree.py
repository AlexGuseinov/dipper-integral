"""Exact algebraic degree (in the plaintext bits, round keys as independent
variables) of every output bit of r-round Dipper and of the two variants.

Upper bound D: step6 (no monomial trail from any u with wt(u) > D).
Lower bound D: a presence proof (odd trail count for some key pattern) for a
monomial x^u with wt(u) = D. Then deg = D exactly. u is taken from the free-input
model under the cardinality constraint wt(u) >= D; if no proof is found for that
u, it is blocked and another u is tried. For every proof all trails are
re-enumerated and each is checked by the CNF-independent checker.
Usage: step25_exact_degree.py <mode:rounds,...;mode:rounds,...> <outfile>
"""
import json, os, random, sys, time
sys.path.insert(0, ".")
from pysat.solvers import Solver
from pysat.card import ITotalizer
from dipper.models import build
from dipper.count import TrailCounter, greedy_key_pattern_fast
from dipper.witness import check_trail

jobs = [(m, [int(r) for r in rs.split(",")]) for m, rs in (x.split(":") for x in sys.argv[1].split(";"))]
OUT = sys.argv[2]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
ub = {"add": json.load(open("results/step6_degree_add.json"))["add"]}
ub.update(json.load(open("results/step6_degree_xor_none.json")))
STAGES = [(1500, 40), (500, 400), (200, 3000)]
MAX_U = 6
if os.environ.get("REDO"):                 # second pass: many candidate monomials, small budget each
    STAGES = [(90, 40), (30, 400)]
    MAX_U = int(os.environ.get("MAX_U", "60"))


def save():
    json.dump(res, open(OUT + ".tmp", "w"), indent=1); os.replace(OUT + ".tmp", OUT)


STRATS = [((0,), "max"), ((), "max"), ((0,), "min")]   # v_1 = 0 first: at the degree limit the
                                                       # first-round key part of the monomial is often forced to 0


def prove(u, r, mode, j, seed):
    c = TrailCounter(u, r, mode)
    seen = set()
    try:
        for tries, cap in STAGES:
            for si, (fz, direction) in enumerate(STRATS):
                rng = random.Random(seed + cap + 17 * si)
                for _ in range(tries // len(STRATS)):
                    fzr = tuple(t for t in fz if t < r)
                    pat = greedy_key_pattern_fast(c, j, rng, forced_zero=fzr, direction=direction)
                    if pat is None:
                        break
                    if tuple(pat) in seen:
                        continue
                    seen.add(tuple(pat))
                    n, _ = c.count(pat, j, cap=cap)
                    if n is not None and n % 2 == 1:
                        n2, trails = c.count(pat, j, cap=n + 1, return_trails=n + 1)
                        ok = n2 == n and len(trails) == n and all(check_trail(t, u, j, mode)[0] for t in trails)
                        return {"count": n, "pattern": [f"{m:016X}" for m in pat], "all_trails_ok": ok,
                                "examined": len(seen), "strategy": f"{'v1=0 ' if fz else ''}{direction}"}
        return None
    finally:
        c.close()


for mode, rounds in jobs:
    for r in rounds:
        key = f"{mode}|{r}"
        rec = res.setdefault(key, {})
        pb = {int(k): v for k, v in ub[mode][str(r)]["per_bit"].items()}
        todo = [j for j in range(64) if str(j) not in rec or (os.environ.get("REDO") and not rec[str(j)]["exact"])]
        if not todo:
            continue
        m, out = build(None, r, "mp", mode)
        tot = ITotalizer(lits=[-v for v in m.inputs], ubound=64, top_id=m.pool.top)
        s = Solver(name="cadical153", bootstrap_with=m.cl + tot.cnf.clauses)
        fresh = max(tot.top_id, m.pool.top) + 1          # selector variables must not clash with the totalizer
        for j in todo:
            t0, D = time.time(), pb[j]
            base = [out[i] if i == j else -out[i] for i in range(64)]
            sel, fresh = fresh, fresh + 1
            got, tried_u = None, 0
            while tried_u < MAX_U and s.solve(assumptions=base + [-tot.rhs[64 - D], sel] if D > 0 else base + [sel]):
                model = set(l for l in s.get_model() if l > 0)
                u = [i for i, v in enumerate(m.inputs) if v in model]
                tried_u += 1
                if len(u) != D:
                    s.add_clause([-sel] + [-v if v in model else v for v in m.inputs]); continue
                pr = prove(u, r, mode, j, 1000 * r + j + 7 * tried_u)
                if pr:
                    got = dict(pr, u=u); break
                s.add_clause([-sel] + [-v if v in model else v for v in m.inputs])   # block this u
            s.add_clause([-sel])
            rec[str(j)] = {"upper": D, "exact": bool(got and got["all_trails_ok"]), "tried_u": tried_u,
                           "secs": round(time.time() - t0, 1), **({} if not got else got)}
            print(f"{mode} r={r} j={j} D={D} exact={rec[str(j)]['exact']} u_tried={tried_u} "
                  f"count={got and got['count']} {rec[str(j)]['secs']}s", flush=True)
            save()
        s.delete()
        ex = sum(1 for v in rec.values() if v["exact"])
        print(f"== {mode} r={r}: exact {ex}/64", flush=True)
