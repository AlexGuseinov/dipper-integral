"""E21.1 — is AllSAT over the layer masks a bijective enumeration of trails?

The counter blocks solutions on the layer masks only, on the grounds that every
other variable (key-layer inputs, the addition's b', q, w, c) is a function of
those masks and of the pinned key pattern. If that were false, trails would be
over- or under-counted and every parity claim would be void.

Test: count the same (cube, pattern, bit) twice, once blocking on the masks and
once blocking on ALL variables of the formula. The two counts must agree."""
import json, random, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter, greedy_key_pattern

rng = random.Random(7)
rows, t0 = [], time.time()
for rounds, dim, cubes in ((2, 6, 4), (3, 6, 4), (4, 8, 3)):
    for _ in range(cubes):
        u = sorted(rng.sample(range(64), dim))
        cm = TrailCounter(u, rounds, projection="masks")
        ca = TrailCounter(u, rounds, projection="all")
        for j in rng.sample(range(64), 4):
            pat = greedy_key_pattern(cm, j, rng)
            if pat is None:
                continue
            nm, _ = cm.count(pat, j, cap=20000)
            na, _ = ca.count(pat, j, cap=20000)
            rows.append({"rounds": rounds, "dim": dim, "cube": u, "bit": j,
                         "pattern_weight": sum(bin(m).count("1") for m in pat),
                         "count_masks": nm, "count_all": na, "agree": nm == na})
            assert nm == na, rows[-1]
        cm.close(); ca.close()
        print(f"r={rounds} dim={dim}: {len(rows)} comparisons so far", flush=True)
out = {"comparisons": len(rows), "disagreements": sum(not r["agree"] for r in rows),
       "capped": sum(r["count_masks"] is None for r in rows),
       "max_count": max((r["count_masks"] or 0) for r in rows),
       "seconds": round(time.time() - t0, 1), "rows": rows}
json.dump(out, open("results/step16_projection_check.json", "w"), indent=1)
print({k: out[k] for k in ("comparisons", "disagreements", "capped", "max_count", "seconds")})
