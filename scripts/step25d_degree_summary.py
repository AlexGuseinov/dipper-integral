"""Merge all degree results into one table: for every (variant, round, bit) the
certified upper bound (step6) and the proven lower bound (presence proofs of
step25/step25c, ANF of step25b for one-round bits, step21 for Dipper at 7 rounds)."""
import json
ub = {"add": json.load(open("results/step6_degree_add.json"))["add"]}
ub.update(json.load(open("results/step6_degree_xor_none.json")))
lo = {}
import os
for f in ("results/step25_degree_part1.json", "results/step25_degree_part2.json",
          "results/step25_degree_add.json", "results/step25_degree_xor_lo.json"):
    if not os.path.exists(f):
        continue
    for k, v in json.load(open(f)).items():
        for j, x in v.items():
            if x["exact"]:
                lo[(k, int(j))] = (x["upper"], "presence")
for k, x in json.load(open("results/step25c_degree_hard.json")).items():
    mode, r, j = k.split("|")
    if x.get("lower") is not None:
        key = (f"{mode}|{r}", int(j))
        if key not in lo or lo[key][0] < x["lower"]:
            lo[key] = (x["lower"], "presence")
for j, x in json.load(open("results/step25b_anf_degree_r1.json")).items():
    lo[("add|1", int(j))] = (x["degree"], "ANF")
for j in range(64):
    lo[("add|7", j)] = (63, "presence (step21)")
rounds = {"add": range(1, 8), "xor": range(1, 12), "none": range(1, 12)}
out, summ = {}, {}
for mode, rs in rounds.items():
    for r in rs:
        k = f"{mode}|{r}"
        pb = ub[mode][str(r)]["per_bit"] if str(r) in ub[mode] else {str(j): 63 for j in range(64)}
        rows = {}
        for j in range(64):
            U = pb[str(j)]
            L, how = lo.get((k, j), (None, None))
            rows[j] = {"upper": U, "lower": L, "how": how}
        out[k] = rows
        exact = sum(1 for x in rows.values() if x["lower"] == x["upper"])
        gaps = {j: (x["lower"], x["upper"]) for j, x in rows.items() if x["lower"] != x["upper"]}
        summ[k] = {"exact": exact, "gaps": gaps,
                   "mean_upper": round(sum(x["upper"] for x in rows.values()) / 64, 2),
                   "mean_lower": round(sum((x["lower"] or 0) for x in rows.values()) / 64, 2)}
json.dump({"summary": summ, "per_bit": out}, open("results/step25_degree_summary.json", "w"), indent=1)
tot = sum(v["exact"] for v in summ.values()); n = 64 * len(summ)
print(f"exact {tot}/{n}")
for k, v in summ.items():
    if v["gaps"]:
        print(k, v["exact"], v["gaps"])
