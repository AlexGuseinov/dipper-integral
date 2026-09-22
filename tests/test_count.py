"""Validation of dipper/count.py against directly computed ANF coefficients.

lambda^{(j)}_{u,v} = coefficient of x^u prod_t RK_t^{v_t} in S^(r)_j
                   = XOR over x' <= u and RK'_t <= v_t of S^(r)_j(x', RK')

is computed on the left by evaluating the reference cipher (Moebius inversion)
and on the right by the SAT trail counter (monomial prediction). Patterns come
from the greedy search, so the comparison covers the patterns the presence
machinery actually uses, including ones with an odd count."""
import random, sys
import numpy as np
sys.path.insert(0, ".")
from dipper import fast as F
from dipper.count import TrailCounter, greedy_key_pattern


def coeff_by_moebius(u_bits, v_masks, r, j, mode="add"):
    kpos = [(t, i) for t, m in enumerate(v_masks) for i in range(64) if (m >> i) & 1]
    assert len(kpos) <= 12, "Moebius sum too large"
    acc = 0
    for kb in range(1 << len(kpos)):
        rks = [0] * r
        for idx, (t, i) in enumerate(kpos):
            if (kb >> idx) & 1:
                rks[t] |= 1 << i
        s = F.cube_plaintexts(u_bits, 0)
        for t in range(r):
            s = F.T(s ^ np.uint64(rks[t]), mode)
        acc ^= (F.xor_reduce(s) >> j) & 1
    return acc


def run(rounds, dim, cubes, seed, cap=300000, per_cube=8):
    rng = random.Random(seed)
    checked = odd = 0
    for _ in range(cubes):
        u = sorted(rng.sample(range(64), dim))
        c = TrailCounter(u, rounds)
        for j in rng.sample(range(64), per_cube):
            pat = greedy_key_pattern(c, j, rng, direction="min")
            if pat is None:                      # no trail: coefficient must be 0
                for v in ([0] * rounds, [1 << rng.randrange(64) for _ in range(rounds)]):
                    assert coeff_by_moebius(u, v, rounds, j) == 0
                    checked += 1
                continue
            if sum(bin(m).count("1") for m in pat) > 10:
                continue                         # keep the Moebius sum cheap
            n, _ = c.count(pat, j, cap=cap)
            if n is None:
                continue                         # capped: no claim to check
            lam = coeff_by_moebius(u, pat, rounds, j)
            assert n % 2 == lam, (rounds, u, [hex(x) for x in pat], j, n, lam)
            checked += 1
            odd += lam
        c.close()
    return checked, odd


if __name__ == "__main__":
    tot = nz = 0
    for rounds, dim, cubes, seed in ((2, 5, 6, 11), (2, 8, 4, 12), (3, 5, 6, 13), (3, 8, 4, 14)):
        c, n = run(rounds, dim, cubes, seed)
        tot += c; nz += n
        print(f"r={rounds} dim={dim}: {c} coefficients agree ({n} of them odd)")
        sys.stdout.flush()
    print(f"total {tot} comparisons, {nz} odd, no disagreement")
