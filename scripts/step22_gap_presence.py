"""Presence proofs for the persistent gap bits of Section 7 (step4_tightness).

A persistent gap bit is empirically zero in all trials but not certified. An odd
trail count for some key pattern proves that its cube sum is not identically zero
(for independent round keys), i.e. that the bit is NOT balanced.
"""
import json, random, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter, greedy_key_pattern
from dipper.witness import check_trail

rows = json.load(open(sys.argv[1]))
rows = rows["rows"] if isinstance(rows, dict) else rows
STAGES = [(2000, 1500), (800, 8000), (200, 40000)]
out, t00 = [], time.time()
for row in rows:
    if not row.get("persistent_bits"):
        continue
    act, r = row["active"], row["rounds"]
    c = TrailCounter(act, r)
    for j in row["persistent_bits"]:
        t0, seen, hit = time.time(), set(), None
        for tries, cap in STAGES:
            rng = random.Random(31 * j + r + cap)
            for _ in range(tries):
                pat = greedy_key_pattern(c, j, rng, direction="max")
                if pat is None:
                    hit = ("no trail",); break
                if tuple(pat) in seen:
                    continue
                seen.add(tuple(pat))
                n, tr = c.count(pat, j, cap=cap, return_trails=1)
                if n is not None and n % 2 == 1:
                    hit = ("odd", n, pat, tr[0]); break
            if hit:
                break
        rec = dict(cube=row["cube"], active=act, rounds=r, bit=j, examined=len(seen),
                   secs=round(time.time() - t0, 1))
        if hit and hit[0] == "odd":
            ok, _ = check_trail(hit[3], act, j, "add")
            rec.update(status="odd", count=hit[1], witness_ok=ok,
                       pattern=[f"{m:016X}" for m in hit[2]])
        else:
            rec["status"] = hit[0] if hit else "unresolved"
        out.append(rec)
        print({k: v for k, v in rec.items() if k not in ("active", "pattern")}, flush=True)
    c.close()
summary = {"cases": len(out), "odd_with_valid_witness": sum(1 for x in out if x.get("witness_ok")),
           "unresolved": [(x["cube"], x["rounds"], x["bit"]) for x in out if not x.get("witness_ok")],
           "seconds": round(time.time() - t00, 1)}
print(summary)
json.dump({"summary": summary, "cases": out}, open("results/step22_gap_presence.json", "w"), indent=1)
