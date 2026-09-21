"""C1: all 64 maximal cubes (63 active bits) for r = 4..7 rounds, three models.

Monotonicity (MP model): the first round starts with a key XOR, which lets a
trail start from any mask containing the cube. Hence reach(I') is a subset of
reach(I) whenever I is a subset of I', and 'no certificate for any 63-bit cube'
implies 'no certificate for any cube of dimension <= 63'. (The 64-bit cube is
the trivial full-codebook property and is excluded.)"""
import json, sys, time
sys.path.insert(0, ".")
from dipper.models import Checker

MODES = sys.argv[1].split(",") if len(sys.argv) > 1 else ["add"]
MODELS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["mp", "mpc", "bdp"]
ROUNDS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [4, 5, 6, 7]
out = {}
t0 = time.time()
for mode in MODES:
    out[mode] = {}
    for model in MODELS:
        out[mode][model] = {}
        for r in ROUNDS:
            per_const = {}
            timeouts = {}
            t1 = time.time()
            for p in range(64):
                ch = Checker(set(range(64)) - {p}, r, model, mode)
                res = ch.balanced_bits(conflict_budget=100_000)
                for j in [j for j, v in res.items() if v == "timeout"]:     # retry
                    v = ch.trail_exists(j, conflict_budget=5_000_000)
                    res[j] = "balanced" if v is False else ("unknown" if v else "timeout")
                ch.close()
                per_const[p] = [j for j, v in res.items() if v == "balanced"]
                timeouts.setdefault(r, []).extend((p, j) for j, v in res.items() if v == "timeout")
            counts = {p: len(v) for p, v in per_const.items()}
            out[mode][model][r] = {"balanced_by_const_bit": per_const,
                                   "max_balanced": max(counts.values()),
                                   "cubes_with_certificate": sum(c > 0 for c in counts.values()),
                                   "timeouts": timeouts.get(r, []),
                                   "seconds": round(time.time() - t1, 1)}
            print(mode, model, r, "max", max(counts.values()), "cubes w/ cert",
                  sum(c > 0 for c in counts.values()), "timeouts", len(timeouts.get(r, [])), f"{time.time()-t1:.1f}s"); sys.stdout.flush()
tag = "_".join(MODES) + ("" if len(sys.argv) <= 2 else "_r" + "-".join(map(str, ROUNDS)))
json.dump(out, open(f"results/step3_maximal_cubes_{tag}.json", "w"), indent=1)
print("total", round(time.time() - t0, 1))
