"""Independent re-run of the 7-round presence probe, with key patterns persisted.

For the 63-dimensional cube with constant bit p, and every output bit j, search
for a key pattern whose trail count is ODD: that proves the monomial x^{u_p}k^v
occurs in S^(r)_j, hence the cube sum is not identically zero, hence bit j is
NOT balanced over that cube (the converse direction to the paper's certificates).

Round 1 is pinned to the all-zero key pattern, which is exact at dimension 63.
Every record keeps the pattern, so the result can be re-verified without
re-running the search; when a trail is returned it is validated by the
CNF-independent checker."""
import json, random, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter, find_odd_pattern
from dipper.witness import check_trail

p = int(sys.argv[1]) if len(sys.argv) > 1 else 0
rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 7
tries = int(sys.argv[3]) if len(sys.argv) > 3 else 300
cap = int(sys.argv[4]) if len(sys.argv) > 4 else 20000
active = sorted(set(range(64)) - {p})
out, t0 = {}, time.time()
c = TrailCounter(active, rounds)
for j in range(64):
    t1 = time.time()
    rng = random.Random(1000 * p + j)
    r = find_odd_pattern(c, j, rng, tries=tries, cap=cap, forced_zero=(0,))
    rec = {"status": r["status"], "examined": r.get("examined"), "capped": r.get("capped"),
           "secs": round(time.time() - t1, 1)}
    if r["status"] == "odd":
        rec["count"] = r["count"]
        rec["pattern"] = [f"{m:016X}" for m in r["pattern"]]
        if r.get("trail"):
            ok, why = check_trail(r["trail"], active, j, "add")
            rec["witness_ok"] = ok
            rec["witness_note"] = why
            rec["trail"] = [f"{m:016X}" for m in r["trail"]]
    out[j] = rec
    print(j, rec["status"], rec.get("count"), "witness", rec.get("witness_ok"),
          f'{rec["secs"]}s', flush=True)
res = {"constant_bit": p, "rounds": rounds, "tries": tries, "cap": cap,
       "odd_found": sum(v["status"] == "odd" for v in out.values()),
       "witness_checked": sum(v.get("witness_ok") is True for v in out.values()),
       "witness_failed": sum(v.get("witness_ok") is False for v in out.values()),
       "unresolved": [j for j, v in out.items() if v["status"] != "odd"],
       "seconds": round(time.time() - t0, 1), "bits": out}
json.dump(res, open(f"results/step17_presence_p{p}_r{rounds}.json", "w"), indent=1)
print({k: res[k] for k in ("odd_found", "witness_checked", "witness_failed", "unresolved", "seconds")})
