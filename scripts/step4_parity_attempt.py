"""Documented negative result: exact trail counting (parity per key monomial)
for a persistent gap bit is infeasible — the trail count exceeds the cap even
at two rounds, because each key-XOR layer multiplies trails by key monomials."""
import json, random, sys, time
sys.path.insert(0, ".")
from dipper.exact import trail_parities

rng = random.Random(3)
active = sorted(rng.sample(range(64), 12))
out = []
for r, j, cap in ((2, 0, 100_000), (2, 30, 100_000)):
    t = time.time()
    res = trail_parities(active, r, j, cap=cap)
    res.update(rounds=r, bit=j, active=active, cap=cap, seconds=round(time.time() - t, 1))
    out.append(res); print(res); sys.stdout.flush()
json.dump(out, open("results/step4_parity_attempt.json", "w"), indent=1)
