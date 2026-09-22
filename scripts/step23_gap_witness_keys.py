"""Explicit round keys with a nonzero cube sum for the 46 persistent gap bits.

A presence proof (odd trail count for key pattern v) implies that the cube sum,
restricted to round keys whose bits lie inside v (all other key bits 0), has the
monomial k^v; since the sum of that restricted function over all k <= v equals
the coefficient of k^v, some k <= v gives a nonzero cube sum. We search such
keys directly: first k = v, then random sub-patterns of v. Every key found is
re-checked with the scalar reference implementation (dipper/cipher.py), so the
result depends neither on the SAT model nor on the trail counting.
"""
import json, random, sys, time
import numpy as np
sys.path.insert(0, ".")
from dipper import fast
from dipper.cipher import encrypt_rk

cases = json.load(open("results/step22_gap_presence.json"))["cases"]
TRIES = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
out, t00 = [], time.time()
try:
    prev = {(c["cube"], c["rounds"], c["bit"], tuple(c.get("active", []))): c
            for c in json.load(open("results/step23_gap_witness_keys.json"))["cases"] if c.get("reference_check")}
except FileNotFoundError:
    prev = {}


def cube_sum_fast(act, rks, j):
    s = fast.cube_plaintexts(act, 0)
    for rk in rks:
        s = fast.T(s ^ np.uint64(rk))
    return (fast.xor_reduce(s) >> j) & 1


def cube_sum_ref(act, rks, j):
    acc = 0
    for x in range(1 << len(act)):
        p = sum(((x >> i) & 1) << b for i, b in enumerate(act))
        acc ^= encrypt_rk(p, rks)
    return (acc >> j) & 1


for cs in cases:
    act, r, j = cs["active"], cs["rounds"], cs["bit"]
    key = (cs["cube"], r, j, tuple(act))
    if key in prev:
        out.append(prev[key]); continue
    v = [int(m, 16) for m in cs["pattern"]]
    rng = random.Random(1234 + 97 * j + r)
    t0, found, tried = time.time(), None, 0
    def rnd(level):
        """random 64-bit word with bit density 2^-level (level 0: density 3/4)."""
        if level == 0:
            return rng.getrandbits(64) | rng.getrandbits(64)
        w = (1 << 64) - 1
        for _ in range(level):
            w &= rng.getrandbits(64)
        return w

    def candidates():
        yield list(v)
        for n in range(TRIES):
            lev = n % 6
            yield [m & rnd(lev) for m in v]
    for rks in candidates():
        tried += 1
        if cube_sum_fast(act, rks, j):
            found = rks
            break
    rec = dict(cube=cs["cube"], active=act, rounds=r, bit=j, tried=tried, secs=round(time.time() - t0, 1))
    if found:
        rec["round_keys"] = [f"{k:016X}" for k in found]
        rec["reference_check"] = bool(cube_sum_ref(act, found, j))
    out.append(rec)
    print(rec, flush=True)
    json.dump({"partial": True, "cases": out}, open("results/step23_gap_witness_keys.json", "w"), indent=1)
summ = {"cases": len(out), "with_explicit_key": sum(1 for x in out if x.get("reference_check")),
        "seconds": round(time.time() - t00, 1)}
print(summ)
json.dump({"summary": summ, "cases": out}, open("results/step23_gap_witness_keys.json", "w"), indent=1)
