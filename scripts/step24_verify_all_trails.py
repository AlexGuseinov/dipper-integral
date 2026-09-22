"""Re-enumerate every trail behind every presence proof and validate each one.

For each proof (cube, output bit j, key pattern v) the trails are enumerated
again, every trail is checked by the CNF-independent checker (dipper/witness.py),
and the number of trails must equal the recorded count and be odd. Covers the
seven-round proofs of step20/step21 and the gap-bit proofs of step22.
Resumable: results are written after every cube.
"""
import glob, json, os, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter
from dipper.witness import check_trail

OUT = "results/step24_all_trails_verified.json"
res = json.load(open(OUT)) if os.path.exists(OUT) else {}

jobs = {}                                             # (label, active tuple, rounds) -> [(j, pattern, count)]
p0 = json.load(open("results/step20_presence_r7_complete.json"))["per_bit"]
jobs[("p=0", tuple(sorted(set(range(64)) - {0})), 7)] = [(int(j), v["pattern"], v["count"]) for j, v in p0.items()]
for f in glob.glob("results/step21_presence_*_p.json"):
    for p, rec in json.load(open(f)).items():
        if rec.get("done"):
            jobs[(f"p={p}", tuple(sorted(set(range(64)) - {int(p)})), 7)] = [
                (int(j), b["pattern"], b["count"]) for j, b in rec["bits"].items()]
for c in json.load(open("results/step22_gap_presence.json"))["cases"]:
    jobs.setdefault((f"gap {c['cube']} r={c['rounds']}", tuple(c["active"]), c["rounds"]), []).append(
        (c["bit"], c["pattern"], c["count"]))

t00 = time.time()
for (label, act, r), items in sorted(jobs.items(), key=lambda x: x[0][0]):
    k = f"{label}|{r}|{','.join(map(str, act))}"
    if k in res and res[k].get("n_proofs") == len(items):
        continue
    t0 = time.time()
    c = TrailCounter(list(act), r)
    bad, ntr = [], 0
    for j, pat, cnt in items:
        v = [int(m, 16) for m in pat]
        n, trails = c.count(v, j, cap=cnt + 1, return_trails=cnt + 1)
        ok = n == cnt and n % 2 == 1 and len(trails) == n
        for t in trails:
            good, _ = check_trail(t, list(act), j, "add")
            ok &= good
        ntr += len(trails)
        if not ok:
            bad.append({"bit": j, "recorded": cnt, "recount": n})
    c.close()
    res[k] = {"label": label, "rounds": r, "n_proofs": len(items), "n_trails": ntr,
              "failures": bad, "secs": round(time.time() - t0, 1)}
    print(label, r, "proofs", len(items), "trails", ntr, "failures", len(bad), res[k]["secs"], "s", flush=True)
    json.dump(res, open(OUT + ".tmp", "w"), indent=1); os.replace(OUT + ".tmp", OUT)
tot = {"proofs": sum(v["n_proofs"] for v in res.values()), "trails": sum(v["n_trails"] for v in res.values()),
       "failures": sum(len(v["failures"]) for v in res.values())}
print("TOTAL", tot, round(time.time() - t00, 1), "s")
