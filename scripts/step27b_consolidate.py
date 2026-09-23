"""Merge the runs of step27 into one record per cube, keeping only records that are
invertible with zero validation failures."""
import glob, json
recs = {}
for f in sorted(glob.glob("results/step27_lc_*.json")):
    for p, r in json.load(open(f)).items():
        if r.get("invertible") and r.get("failures", 1) == 0 and int(p) not in recs:
            recs[int(p)] = r
missing = sorted(set(range(64)) - set(recs))
print("valid cubes:", len(recs), "missing:", missing,
      "trails:", sum(r["trails_checked"] for r in recs.values()))
json.dump({str(p): recs[p] for p in sorted(recs)}, open("results/step27_linear_combinations_final.json", "w"), indent=1)
