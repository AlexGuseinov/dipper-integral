"""7-round presence proofs for every cube of dimension 63 (constant bit p).

For each p and each output bit j, search a key pattern with an odd trail count
(staged caps, see step18) and validate the trail with the CNF-independent checker.
Usage: step21_presence_all_p.py <p-list> <outfile>. Results are written after every p.
"""
import json, os, random, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter, greedy_key_pattern
from dipper.witness import check_trail

rounds = 7
STAGES = [(2000, 1500), (800, 8000), (200, 40000)]
ps = [int(x) for x in sys.argv[1].split(",")]
OUT = sys.argv[2]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}

for p in ps:
    if str(p) in res and res[str(p)].get("done"):
        continue
    t0 = time.time()
    active = sorted(set(range(64)) - {p})
    c = TrailCounter(active, rounds)
    bits = {}
    for j in range(64):
        seen, hit = set(), None
        for tries, cap in STAGES:
            rng = random.Random(7919 * p + 1009 * j + cap)
            for _ in range(tries):
                pat = greedy_key_pattern(c, j, rng, forced_zero=(0,), direction="max")
                if pat is None:
                    hit = ("no trail", None, None); break
                if tuple(pat) in seen:
                    continue
                seen.add(tuple(pat))
                n, tr = c.count(pat, j, cap=cap, return_trails=1)
                if n is not None and n % 2 == 1:
                    hit = ("odd", n, (pat, tr[0])); break
            if hit:
                break
        if hit and hit[0] == "odd":
            pat, trail = hit[2]
            ok, _ = check_trail(trail, active, j, "add")
            bits[j] = {"count": hit[1], "witness_ok": ok,
                       "pattern": [f"{m:016X}" for m in pat]}
        else:
            bits[j] = {"status": hit[0] if hit else "unresolved", "examined": len(seen)}
    c.close()
    solved = [j for j, b in bits.items() if b.get("witness_ok")]
    res[str(p)] = {"done": True, "resolved": len(solved),
                   "unresolved": [j for j in range(64) if j not in solved],
                   "secs": round(time.time() - t0, 1), "bits": bits}
    print(p, len(solved), res[str(p)]["unresolved"], res[str(p)]["secs"], flush=True)
    json.dump(res, open(OUT, "w"), indent=1)
