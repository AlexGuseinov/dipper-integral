"""Exact decision of whether a cube sum is identically zero (all keys).

g(k) = XOR over the cube of S^(r)_j, a polynomial in the merged key variables
k_1' = (constants XOR RK_1) and RK_2..RK_r. From the exact-MP model we compute
  * the support: key bits that occur in at least one monomial trail,
  * an upper bound D on the key-degree of g (max number of key bits created
    along a trail).
A multilinear polynomial of degree <= D vanishes identically iff it vanishes on
every point of Hamming weight <= D (Moebius inversion recovers each coefficient
a_S, |S| <= D, from those points). Evaluating g on all such points inside the
support therefore decides g == 0 exactly; any nonzero value is a witness."""
from itertools import combinations
import numpy as np
from pysat.solvers import Solver
from pysat.card import ITotalizer
from .models import build
from . import fast as F


def key_structure(active, r, j, mode="add", budget=5_000_000):
    m, out = build(set(active), r, "mp", mode)
    kvars = []                                    # (round, bit, var) created key bits
    extra = []
    for rr, (x, y) in enumerate(m.keylayers):
        for i in range(64):
            v = m.pool.id(("kv", rr, i))
            extra += [[-v, y[i]], [-v, -x[i]], [v, -y[i], x[i]]]  # v = y & ~x
            kvars.append((rr, i, v))
    base = [out[i] if i == j else -out[i] for i in range(64)]
    s = Solver(name="cadical153", bootstrap_with=m.cl + extra)
    if not s.solve(assumptions=base):
        s.delete(); return {"trails": False}
    support = []
    for rr, i, v in kvars:
        s.conf_budget(budget)
        res = s.solve_limited(assumptions=base + [v])
        if res is None:
            s.delete(); return {"trails": True, "status": "timeout-support"}
        if res:
            support.append((rr, i))
    lits = [v for rr, i, v in kvars if (rr, i) in set(support)]
    tot = ITotalizer(lits=[-l for l in lits], ubound=len(lits), top_id=max(m.pool.top, max(abs(l) for c in extra for l in c)))
    s.append_formula(tot.cnf.clauses)
    lo, hi = 0, len(lits)
    while lo < hi:                                # max key weight of a trail
        mid = (lo + hi + 1) // 2
        s.conf_budget(budget)
        res = s.solve_limited(assumptions=base + [-tot.rhs[len(lits) - mid]])
        if res is None:
            s.delete(); return {"trails": True, "status": "timeout-degree", "support": support}
        lo, hi = (mid, hi) if res else (lo, mid - 1)
    s.delete()
    return {"trails": True, "status": "ok", "support": support, "degree_bound": lo}


def cube_sum_bit(active, r, j, rks, mode="add"):
    s = F.cube_plaintexts(active, 0)
    for rr in range(r):
        s = F.T(s ^ np.uint64(rks[rr]), mode)
    return (F.xor_reduce(s) >> j) & 1


def decide(active, r, j, mode="add", max_evals=3_000_000):
    ks = key_structure(active, r, j, mode)
    if not ks["trails"]:
        return {"verdict": "certified (no trail)"}
    if ks.get("status") != "ok":
        return {"verdict": "undecided", **ks}
    sup, D = ks["support"], ks["degree_bound"]
    from math import comb
    n_eval = sum(comb(len(sup), i) for i in range(D + 1))
    info = {"support_size": len(sup), "degree_bound": D, "evaluations": n_eval}
    if n_eval > max_evals:
        return {"verdict": "undecided (too many evaluations)", **info}
    for w in range(D + 1):
        for T in combinations(sup, w):
            rks = [0] * r
            for rr, i in T:
                rks[rr] |= 1 << i
            if cube_sum_bit(active, r, j, rks, mode):
                return {"verdict": "NOT balanced (witness)", "witness": T, **info}
    return {"verdict": "balanced EXACTLY (cancellation)", **info}


def _setup(active, r, j, mode):
    m, out = build(set(active), r, "mp", mode)
    kv, extra = [], []
    for rr, (x, y) in enumerate(m.keylayers):
        row = []
        for i in range(64):
            v = m.pool.id(("kv", rr, i))
            extra += [[-v, y[i]], [-v, -x[i]], [v, -y[i], x[i]]]
            row.append(v)
        kv.append(row)
    base = [out[i] if i == j else -out[i] for i in range(64)]
    return m, out, kv, extra, base


def count_trails_with_key(m, s, base, kv, keymono, cap):
    """Number of trails (projected on masks) whose key monomial equals keymono."""
    assum = base + [v if keymono[rr][i] else -v for rr, row in enumerate(kv) for i, v in enumerate(row)]
    n, blocks = 0, []
    sel = m.pool.id(("sel", len(m.pool.obj2id)))       # activation literal for blocking clauses
    while n < cap and s.solve(assumptions=assum + [sel]):
        model = s.get_model()
        val = {abs(l): l > 0 for l in model}
        n += 1
        s.add_clause([-sel] + [-v if val[v] else v for v in m.masks])
    s.add_clause([-sel])                              # retire blocking clauses
    return n


def presence_witness(active, r, j, mode="add", tries=20, cap=20000, seed=0):
    """Try to PROVE that x^I (with arbitrary key monomial) occurs in S^(r)_j,
    i.e. the cube sum is NOT identically zero. For a key monomial k^v taken from
    a trail, the coefficient of x^I k^v equals the parity of the trails with that
    exact key pattern; an odd count is a proof. Returns (proved, info)."""
    import random
    rng = random.Random(seed)
    m, out, kv, extra, base = _setup(active, r, j, mode)
    s = Solver(name="cadical153", bootstrap_with=m.cl + extra)
    flat = [v for row in kv for v in row]
    tried = set()
    for t in range(tries):
        # random phase: push solver towards different key monomials
        pref = [v if rng.random() < 0.5 else -v for v in flat]
        s.set_phases(pref)
        if not s.solve(assumptions=base):
            s.delete(); return False, {"reason": "no trail (certified balanced)"}
        model = s.get_model(); val = {abs(l): l > 0 for l in model}
        key = tuple(tuple(int(val[v]) for v in row) for row in kv)
        if key in tried:
            continue
        tried.add(key)
        n = count_trails_with_key(m, s, base, kv, key, cap)
        if n < cap and n % 2 == 1:
            s.delete()
            return True, {"trails_for_key_monomial": n, "key_weight": sum(map(sum, key)), "attempt": t}
    s.delete()
    return False, {"reason": "no odd key monomial found", "tried": len(tried)}
