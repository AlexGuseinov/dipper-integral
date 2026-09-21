"""Validation benchmark: reproduce published conventional-BDP integral
distinguishers of GIFT-64 and PRESENT with the same SAT machinery
(Eskandari et al., 'Finding Integral Distinguishers with Ease', SAC 2018, Table 2:
GIFT-64 9 rounds / 63 active bits / 30 balanced bits, 10 rounds none;
PRESENT 9 rounds / 60 active bits / 1 balanced bit, 10 rounds none)."""
import json, sys, time
sys.path.insert(0, ".")
from pysat.solvers import Solver
from dipper.anf import monomial_table
from dipper.models import Model, sbox_layer
from dipper.cipher import PERM as GIFT_PERM

GIFT_SB = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9, 0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]
PRESENT_SB = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
PRESENT_PERM = [(16 * i) % 63 if i != 63 else 63 for i in range(64)]


def bdp_table(sb):
    mp = monomial_table(lambda x: sb[x], 4, 4)
    return [[int(any(mp[u][v] for u in range(16) if u & k == k)) for v in range(16)] for k in range(16)]


def balanced(sb, perm, active, rounds):
    tab = bdp_table(sb)
    m = Model()
    x = m.vars(64)
    for i in range(64):
        m.add([x[i]] if i in active else [-x[i]])
    for _ in range(rounds):
        x = sbox_layer(m, x, tab)
        y = [None] * 64
        for i in range(64):
            y[perm[i]] = x[i]
        x = y
    s = Solver(name="cadical153", bootstrap_with=m.cl)
    bal = [j for j in range(64)
           if not s.solve(assumptions=[x[i] if i == j else -x[i] for i in range(64)])]
    s.delete()
    return bal


def best_over_constant_positions(sb, perm, rounds, n_const, step):
    best, per = (-1, None), {}
    for start in range(0, 64, step):
        const = set(range(start, start + n_const))
        b = balanced(sb, perm, set(range(64)) - const, rounds)
        per[start] = len(b)
        if len(b) > best[0]:
            best = (len(b), sorted(const))
    return best + (per,)


if __name__ == "__main__":
    t0 = time.time(); out = {}
    for name, sb, perm, nconst, step, published in (
            ("GIFT-64", GIFT_SB, GIFT_PERM, 1, 1, {"9": 30, "10": 0}),
            ("PRESENT", PRESENT_SB, PRESENT_PERM, 4, 4, {"9": 1, "10": 0})):
        out[name] = {}
        for r in (9, 10):
            n, const, per = best_over_constant_positions(sb, perm, r, nconst, step)
            out[name][r] = {"active_bits": 64 - nconst, "max_balanced": n,
                            "constant_bits": const, "published": published[str(r)],
                            "balanced_by_first_constant_bit": per,
                            "note": "bit 0 = LSB; published GIFT-64 figure uses MSB-first indexing"}
            print(name, r, out[name][r]); sys.stdout.flush()
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open("results/benchmark_spn.json", "w"), indent=1)
