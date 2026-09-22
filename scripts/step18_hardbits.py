"""Widened presence search on the bits left unresolved by step17.

The search cost is dominated by patterns whose trail count is large: those are
enumerated up to `cap` and then discarded.  Since a presence proof needs a SMALL
odd count, a large cap is wasted work, so the search is staged: many cheap tries
with a small cap first, then fewer tries with a larger one.  Partial results are
written after every stage so the run can be stopped at any point.
"""
import json, random, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter, greedy_key_pattern
from dipper.witness import check_trail

p, rounds = 0, 7
bits = [int(x) for x in sys.argv[1].split(",")]
STAGES = [(2000, 1500), (800, 8000), (200, 40000)]      # (tries, cap)
OUT = "results/step18_hardbits.json"

active = sorted(set(range(64)) - {p})
c = TrailCounter(active, rounds)
out = {}


def search(j, tries, cap, seen, stats):
    rng = random.Random(1009 * j + tries + cap)
    for _ in range(tries):
        pat = greedy_key_pattern(c, j, rng, forced_zero=(0,), direction="max")
        if pat is None:
            return {"status": "no trail"}
        key = tuple(pat)
        if key in seen:
            continue
        seen.add(key)
        n, trails = c.count(pat, j, cap=cap, return_trails=1)
        if n is None:
            stats["capped"] += 1
            continue
        stats["counted"] += 1
        stats["min"] = n if stats["min"] is None else min(stats["min"], n)
        if n % 2 == 1:
            return {"status": "odd", "pattern": pat, "count": n,
                    "trail": trails[0] if trails else None}
    return None


for j in bits:
    t0, seen = time.time(), set()
    stats = {"capped": 0, "counted": 0, "min": None}
    res = None
    for tries, cap in STAGES:
        res = search(j, tries, cap, seen, stats)
        print(f"  bit {j} stage(tries={tries},cap={cap}) "
              f"examined={len(seen)} counted={stats['counted']} capped={stats['capped']} "
              f"min={stats['min']} {'HIT' if res else '-'}", flush=True)
        if res:
            break
    rec = {"examined": len(seen), "secs": round(time.time() - t0, 1), **stats}
    if res and res["status"] == "odd":
        rec["status"] = "odd"
        rec["count"] = res["count"]
        rec["pattern"] = [f"{m:016X}" for m in res["pattern"]]
        if res.get("trail"):
            ok, why = check_trail(res["trail"], active, j, "add")
            rec["witness_ok"], rec["witness_note"] = ok, why
            rec["trail"] = [f"{m:016X}" for m in res["trail"]]
    else:
        rec["status"] = res["status"] if res else "even/capped"
    out[j] = rec
    print(j, {k: v for k, v in rec.items() if k not in ("pattern", "trail")}, flush=True)
    json.dump({"constant_bit": p, "rounds": rounds, "stages": STAGES, "bits": out},
              open(OUT, "w"), indent=1)
