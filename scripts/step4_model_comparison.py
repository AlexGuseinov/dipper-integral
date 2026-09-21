"""C2: certification power and cost of the three propagation models on the
same cube set as the tightness study (plus the 4 word cubes), Dipper and variants."""
import json, sys, time, random
sys.path.insert(0, ".")
from dipper.models import Checker
from scripts.step4_tightness import cubes

MODE = sys.argv[1] if len(sys.argv) > 1 else "add"
rows = []
for name, act in cubes(random.Random(4242)):
    for r in (2, 3, 4, 5, 6):
        row = {"cube": name, "dim": len(act), "rounds": r}
        for model in ("mp", "mpc", "bdp"):
            t = time.time()
            ch = Checker(set(act), r, model, MODE)
            res = ch.balanced_bits(conflict_budget=1_000_000); ch.close()
            row[model] = sorted(j for j, v in res.items() if v == "balanced")
            row[model + "_timeouts"] = sum(v == "timeout" for v in res.values())
            row[model + "_s"] = round(time.time() - t, 2)
        row["identical"] = row["mp"] == row["mpc"] == row["bdp"]
        rows.append(row)
        print(name, r, {m: len(row[m]) for m in ("mp", "mpc", "bdp")}, "identical" if row["identical"] else "DIFFERENT")
        sys.stdout.flush()
summary = {"cases": len(rows), "identical": sum(r["identical"] for r in rows),
           "time_s": {m: round(sum(r[m + "_s"] for r in rows), 1) for m in ("mp", "mpc", "bdp")}}
print(summary)
json.dump({"mode": MODE, "summary": summary, "rows": rows}, open(f"results/step4_model_comparison_{MODE}.json", "w"), indent=1)
