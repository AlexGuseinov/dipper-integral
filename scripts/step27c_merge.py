"""Merge the per-process outputs of step27c_verify.py into results/step27c_verify.json
with a summary (components, blocks by method, trails, used zero entries)."""
import collections, glob, json
M = {}
for f in sorted(glob.glob("results/step27c_verify_*.json")):
    M.update(json.load(open(f)))
assert sorted(map(int, M)) == list(range(64)), "missing cubes"
by, size = collections.Counter(), collections.Counter()
S = {"cubes": 64, "verified": sum(v["verified"] for v in M.values()), "components": 0, "singletons": 0,
     "blocks": 0, "trails7": 0, "trails6": 0, "failures": 0, "used_zero_entries": 0}
for v in M.values():
    S["components"] += v["components"]; S["singletons"] += v["how"]["single_count"] + v["how"]["single_lemma"]
    S["trails7"] += v["trails7"]; S["trails6"] += v["trails6"]; S["failures"] += v["failures"]
    S["used_zero_entries"] += v["used_zero_entries"]
    for b in v["blocks"]:
        S["blocks"] += 1; by[b["by"]] += 1; size[len(b["nodes"])] += 1
S["blocks_by_method"] = dict(by); S["block_sizes"] = {str(k): n for k, n in sorted(size.items())}
S["cubes_with_sum_argument"] = sorted(int(p) for p, v in M.items() if any(b["by"] == "sum" for b in v["blocks"]))
json.dump({"summary": S, "cubes": {str(p): M[str(p)] for p in sorted(map(int, M))}},
          open("results/step27c_verify.json", "w"))
print(json.dumps(S, indent=1))
