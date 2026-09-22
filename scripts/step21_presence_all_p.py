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
from dipper.count import TrailCounter, greedy_key_pattern_fast as greedy_key_pattern
from dipper.witness import check_trail

rounds = 7
STAGES = [(4000, 40), (800, 400), (300, 3000), (100, 40000)]
ps = [int(x) for x in sys.argv[1].split(",")]
OUT = sys.argv[2]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}


def known_patterns(p):
    """bit -> patterns that were odd for bit j at other constant-bit positions,
    closest positions first (same nibble, then same word, then the rest), at most 12."""
    src = {}
    p0 = json.load(open("results/step20_presence_r7_complete.json"))["per_bit"]
    for j, v in p0.items():
        src.setdefault(int(j), []).append((0, tuple(int(m, 16) for m in v["pattern"])))
    for f in glob.glob("results/step21_presence_*_p.json"):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for q, rec in d.items():
            for j, b in rec.get("bits", {}).items():
                if b.get("witness_ok"):
                    src.setdefault(int(j), []).append((int(q), tuple(int(m, 16) for m in b["pattern"])))
    rank = lambda q: (q // 4 != p // 4, q // 16 != p // 16, abs(q - p))
    return {j: [pat for q, pat in sorted(v, key=lambda x: rank(x[0])) if q != p][:12] for j, v in src.items()}


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
    seeds = known_patterns(p)
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
            n, tr = c.count(list(pat), j, cap=200, return_trails=1)
            if n is not None and n % 2 == 1:
                hit, how = ("odd", n, (list(pat), tr[0])), "seed"
                break
        if not hit:                                          # 2) partial seeds: keep rounds >= keep, redo the rest
            base = [c.out[i] if i == j else -c.out[i] for i in range(64)]
            for keep in (2, 3):
                for pat in seeds.get(j, []):
                    fixed = [-v for v in c.kv[0]]
                    for t in range(keep, rounds):
                        fixed += [c.kv[t][i] if (pat[t] >> i) & 1 else -c.kv[t][i] for i in range(64)]
                    if not c.s.solve(assumptions=base + fixed):
                        continue
                    prng = random.Random(31 * p + j + keep)
                    free = [(t, i) for t in range(1, keep) for i in range(64)]
                    for _ in range(8):
                        prng.shuffle(free)
                        fx = list(fixed)
                        c.s.solve(assumptions=base + fx)
                        model = set(l for l in c.s.get_model() if l > 0)
                        for t, i in free:
                            lit = c.kv[t][i]
                            if lit in model:
                                fx.append(lit); continue
                            if c.s.solve(assumptions=base + fx + [lit]):
                                fx.append(lit); model = set(l for l in c.s.get_model() if l > 0)
                        cand = [sum(1 << i for i, v in enumerate(row) if v in model) for row in c.kv]
                        if tuple(cand) in seen:
                            continue
                        seen.add(tuple(cand))
                        n, tr = c.count(cand, j, cap=40, return_trails=1)
                        if n is not None and n % 2 == 1:
                            hit, how = ("odd", n, (cand, tr[0])), f"partial seed (rounds>={keep + 1})"
                            break
                    if hit:
                        break
                if hit:
                    break
        if not hit:                                          # 3) staged random search
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
