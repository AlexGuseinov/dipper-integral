"""Exact decision for the three persistent gap bits whose low-weight
evaluation count is smallest (dipper/resolve.py). Enumerates key points of
weight 0,1,2,... inside the key support and stops at the first nonzero cube sum
(a witness that the bit is NOT balanced); completing all weights <= D would
prove the bit balanced. A time limit applies per case; unfinished cases are
reported as such."""
import json, sys, time
from itertools import combinations
sys.path.insert(0, ".")
from dipper.resolve import key_structure, cube_sum_bit

LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 900
d = json.load(open("results/step6_gap_resolution.json"))["cases"]
rows = json.load(open("results/step4_tightness_add.json"))["rows"]
act_of = {(r["cube"], r["rounds"], tuple(r["active"])): r["active"] for r in rows}
cases = sorted(d, key=lambda c: c.get("evaluations", 1e99))[:3]
out = []
for c in cases:
    act = next(r["active"] for r in rows if r["cube"] == c["cube"] and r["rounds"] == c["rounds"] and c["bit"] in r["persistent_bits"])
    ks = key_structure(act, c["rounds"], c["bit"])
    sup, D = ks["support"], ks["degree_bound"]
    t0, n, verdict, witness = time.time(), 0, "unfinished (time limit)", None
    done = False
    for w in range(D + 1):
        for T in combinations(sup, w):
            rks = [0] * c["rounds"]
            for rr, i in T:
                rks[rr] |= 1 << i
            n += 1
            if cube_sum_bit(act, c["rounds"], c["bit"], rks):
                verdict, witness, done = "NOT balanced (witness found)", [list(t) for t in T], True
                break
            if time.time() - t0 > LIMIT:
                done = True; break
        if done:
            break
    else:
        verdict = "balanced EXACTLY"
    row = dict(cube=c["cube"], active=act, rounds=c["rounds"], bit=c["bit"], support=len(sup), degree_bound=D,
               evaluated=n, max_weight_reached=w, verdict=verdict, witness=witness, seconds=round(time.time() - t0, 1))
    out.append(row); print(row); sys.stdout.flush()
json.dump(out, open("results/step6_gap_small.json", "w"), indent=1)
