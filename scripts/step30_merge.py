"""Merge the per-process outputs of step30_drat_lincomb.py into results/step30_drat_lincomb.json."""
import glob, json
M = {}
for f in sorted(glob.glob("results/step30_drat_lincomb_*.json")):
    M.update(json.load(open(f)))
assert sorted(map(int, M)) == list(range(64)), "missing cubes"
T = {k: sum(v[k] for v in M.values()) for k in
     ["trails", "trails6", "trails7", "drat", "drat_ok", "zero_rows", "zero_entries", "counted_entries"]}
T["certified_cubes"] = sum(v["certified"] for v in M.values())
T["failures"] = sum(len(v["fail"]) for v in M.values())
T["mismatch"] = sum(len(v["parity_mismatch"]) for v in M.values())
T["duplicates"] = sum(v["duplicates"] for v in M.values())
T["zero_inconsistent"] = sum(len(v["zero_inconsistent"]) for v in M.values())
T["secs"] = round(sum(v["secs"] for v in M.values()), 1)
print(T)
json.dump({"summary": T, "cubes": {p: M[p] for p in sorted(M, key=int)}},
          open("results/step30_drat_lincomb.json", "w"), indent=0)
