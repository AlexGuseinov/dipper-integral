"""Collect all JSON results into results/summary.json (used by the paper tables)."""
import glob, json
S = {}
maxc = {}
for fn in sorted(glob.glob("results/step3_maximal_cubes_*.json")):
    d = json.load(open(fn))
    for mode, models in d.items():
        for model, rounds in models.items():
            for r, v in rounds.items():
                maxc.setdefault(mode, {}).setdefault(model, {})[int(r)] = v
S["maximal_cubes"] = {mode: {model: {r: {"max_balanced": v["max_balanced"],
                                         "cubes_with_certificate": v["cubes_with_certificate"],
                                         "timeouts": len(v.get("timeouts", []))}
                                     for r, v in sorted(rs.items())}
                             for model, rs in ms.items()} for mode, ms in maxc.items()}
def longest(rs):
    r = max(r for r, v in rs.items() if v["max_balanced"] > 0)
    return r if (r + 1) in rs and rs[r + 1]["max_balanced"] == 0 else f">={r} (not evaluated beyond)"
S["longest_certified_rounds"] = {mode: {model: longest(rs) for model, rs in ms.items()} for mode, ms in maxc.items()}
# per-cube identity between models on maximal cubes
ident = {}
for mode, ms in maxc.items():
    for r in sorted(set.union(*[set(rs) for rs in ms.values()])):
        have = [m for m in ms if r in ms[m]]
        sets = [{p: sorted(v) for p, v in ms[m][r]["balanced_by_const_bit"].items()} for m in have]
        ident[f"{mode}/r{r} ({','.join(have)})"] = all(s == sets[0] for s in sets)
S["maximal_cubes_models_identical"] = ident
S["frontier"] = {}
for fn in sorted(f for f in glob.glob("results/step3_frontier_*_*.json") if "empirical" not in f):
    mode, model = fn.split("_")[-2], fn.split("_")[-1][:-5]
    S["frontier"][f"{mode}/{model}"] = {r: {"dim": v["dim"], "n_balanced": len(v["balanced"])}
                                         for r, v in json.load(open(fn)).items()}
S["empirical_word_cubes"] = {}
for mode, fn in (("add", "results/step1_empirical_integral.json"),
                 ("xor", "results/empirical_word_cubes_xor.json"),
                 ("none", "results/empirical_word_cubes_none.json")):
    try:
        d = json.load(open(fn))
        S["empirical_word_cubes"][mode] = {w: v["balanced_bits_per_round"] for w, v in d["words"].items()}
    except FileNotFoundError:
        pass
for name in ("benchmark_spn", "step4_model_comparison_add", "step5_key_recovery", "step5_attack_smallscale"):
    try:
        d = json.load(open(f"results/{name}.json"))
        S[name] = d.get("summary", d) if name.startswith("step4") else d
    except FileNotFoundError:
        pass
t = json.load(open("results/step4_tightness_add.json"))["rows"]
agg = {}
for row in t:
    a = agg.setdefault(row["rounds"], {"cases": 0, "certified": 0, "empirical_zero": 0, "gap": 0, "gap_persistent": 0})
    a["cases"] += 1
    for k in ("certified", "empirical_zero", "gap", "gap_persistent"):
        a[k] += row[k]
S["tightness_by_round"] = agg
json.dump(S, open("results/summary.json", "w"), indent=1)
print(json.dumps({k: S[k] for k in ("longest_certified_rounds", "maximal_cubes_models_identical", "frontier", "tightness_by_round")}, indent=1))
