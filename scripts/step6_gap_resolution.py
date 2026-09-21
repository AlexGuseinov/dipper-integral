"""Attempted exact resolution of every persistent gap bit (dipper/resolve.py).
Records the key support and key-degree bound of each cube-sum polynomial; the
exact decision is run only when the number of low-weight evaluations is small."""
import json, sys, time
sys.path.insert(0, ".")
from dipper.resolve import decide, key_structure

rows = json.load(open("results/step4_tightness_add.json"))["rows"]
cases = [(r["cube"], r["active"], r["rounds"], j) for r in rows for j in r["persistent_bits"]]
out = []
for name, act, r, j in cases:
    t = time.time()
    res = decide(act, r, j)
    res.update(cube=name, dim=len(act), rounds=r, bit=j, seconds=round(time.time() - t, 1))
    res.pop("support", None)
    out.append(res); print(res); sys.stdout.flush()
summary = {"cases": len(out),
           "verdicts": {v: sum(o["verdict"] == v for o in out) for v in {o["verdict"] for o in out}},
           "support_size_range": [min(o.get("support_size", 0) for o in out), max(o.get("support_size", 0) for o in out)],
           "degree_bound_range": [min(o.get("degree_bound", 0) for o in out), max(o.get("degree_bound", 0) for o in out)]}
print(summary)
json.dump({"summary": summary, "cases": out}, open("results/step6_gap_resolution.json", "w"), indent=1)
