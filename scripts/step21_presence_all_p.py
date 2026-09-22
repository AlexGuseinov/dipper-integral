"""7-round presence proofs for every cube of dimension 63 (constant bit p).

For each p and each output bit j: first try the key patterns that already gave
an odd count for bit j at other positions of the constant bit (cheap), then a
staged random search over maximal key patterns (see step18). Every trail found
is validated by the CNF-independent checker. Results are checkpointed after
every bit, so the run can be interrupted and resumed.
Usage: step21_presence_all_p.py <p-list> <outfile>
"""
import glob, json, os, random, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter, greedy_key_pattern
from dipper.witness import check_trail

rounds = 7
STAGES = [(2000, 1500), (800, 8000), (200, 40000)]
ps = [int(x) for x in sys.argv[1].split(",")]
OUT = sys.argv[2]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}


def known_patterns():
    """bit -> list of patterns (ints) that were odd for some constant-bit position."""
    seeds = {}
    p0 = json.load(open("results/step20_presence_r7_complete.json"))["per_bit"]
    for j, v in p0.items():
        seeds.setdefault(int(j), []).append(tuple(int(m, 16) for m in v["pattern"]))
    for f in glob.glob("results/step21_presence_*_p.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for rec in d.values():
            for j, b in rec.get("bits", {}).items():
                if b.get("witness_ok"):
                    seeds.setdefault(int(j), []).append(tuple(int(m, 16) for m in b["pattern"]))
    return seeds


def save():
    tmp = OUT + ".tmp"
    json.dump(res, open(tmp, "w"), indent=1)
    os.replace(tmp, OUT)


for p in ps:
    rec = res.setdefault(str(p), {"done": False, "bits": {}})
    if rec.get("done"):
        continue
    t0 = time.time()
    active = sorted(set(range(64)) - {p})
    c = TrailCounter(active, rounds)
    seeds = known_patterns()
    for j in range(64):
        if str(j) in rec["bits"] and rec["bits"][str(j)].get("witness_ok"):
            continue
        tj, seen, hit, how = time.time(), set(), None, None
        for pat in seeds.get(j, []):                       # 1) reuse known patterns
            if pat in seen:
                continue
            seen.add(pat)
            if not c.exists(list(pat), j):
                continue
            n, tr = c.count(list(pat), j, cap=1500, return_trails=1)
            if n is not None and n % 2 == 1:
                hit, how = ("odd", n, (list(pat), tr[0])), "seed"
                break
        if not hit:                                          # 2) staged random search
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
                        hit, how = ("odd", n, (pat, tr[0])), f"search cap={cap}"
                        break
                if hit:
                    break
        if hit and hit[0] == "odd":
            pat, trail = hit[2]
            ok, _ = check_trail(trail, active, j, "add")
            rec["bits"][str(j)] = {"count": hit[1], "witness_ok": ok, "how": how,
                                   "examined": len(seen), "secs": round(time.time() - tj, 1),
                                   "pattern": [f"{m:016X}" for m in pat]}
        else:
            rec["bits"][str(j)] = {"status": hit[0] if hit else "unresolved",
                                   "examined": len(seen), "secs": round(time.time() - tj, 1)}
        b = rec["bits"][str(j)]
        print(f"p={p} j={j} {b.get('how', b.get('status'))} count={b.get('count')} "
              f"ok={b.get('witness_ok')} ex={b['examined']} {b['secs']}s", flush=True)
        save()
    c.close()
    solved = [int(j) for j, b in rec["bits"].items() if b.get("witness_ok")]
    rec.update(done=True, resolved=len(solved),
               unresolved=[j for j in range(64) if j not in solved],
               secs=round(rec.get("secs", 0) + time.time() - t0, 1))
    print(f"== p={p} resolved {len(solved)}/64 unresolved={rec['unresolved']} {rec['secs']}s", flush=True)
    save()
