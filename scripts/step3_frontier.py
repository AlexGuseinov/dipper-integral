"""C1 frontier: for each round count r, greedily shrink a certified cube while
at least one output bit of S^(r) stays certified (MP model), giving an upper
bound on the data complexity 2^d of an r-round (and, via the free final round,
an (r+1)-round output-transformed) distinguisher. Greedy => not proven minimal."""
import json, random, sys, time
sys.path.insert(0, ".")
from dipper.models import Checker

MODE = sys.argv[1] if len(sys.argv) > 1 else "add"
MODEL = sys.argv[2] if len(sys.argv) > 2 else "mp"


def certified(active, r, bits=None):
    ch = Checker(active, r, MODEL, MODE)
    ok = [j for j in (bits if bits is not None else range(64)) if ch.trail_exists(j) is False]
    ch.close()
    return ok


def shrink(start, r, rng):
    cube = set(start)
    bal = certified(cube, r)
    order = sorted(cube); rng.shuffle(order)
    changed = True
    while changed:
        changed = False
        for b in list(order):
            if b not in cube:
                continue
            trial = cube - {b}
            got = certified(trial, r, bal)          # certificates only shrink
            if got:
                cube, bal, changed = trial, got, True
    return sorted(cube), bal


if __name__ == "__main__":
    rounds = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [3, 4, 5, 6]
    import glob
    maxc = {}
    for fn in sorted(glob.glob("results/step3_maximal_cubes_*.json")):
        d = json.load(open(fn))
        if MODE in d and MODEL in d[MODE]:
            maxc.update(d[MODE][MODEL])
    out = {}
    for r in rounds:
        t0 = time.time()
        if str(r) not in maxc and r > 3:
            raise SystemExit(f"run step3_maximal_cubes.py for {MODE} r={r} first")
        per = maxc[str(r)]["balanced_by_const_bit"] if str(r) in maxc else {str(q): [0] for q in (0, 16, 32, 48)}
        starts = sorted(per, key=lambda p: -len(per[p]))[:4]
        best = None
        for si, p in enumerate(starts):
            if not per[p]:
                continue
            for seed in range(3):
                cube, bal = shrink(set(range(64)) - {int(p)}, r, random.Random(1000 * si + seed))
                if best is None or len(cube) < len(best[0]) or (len(cube) == len(best[0]) and len(bal) > len(best[1])):
                    best = (cube, bal)
        out[r] = {"dim": len(best[0]), "active": best[0], "balanced": best[1],
                  "seconds": round(time.time() - t0, 1)}
        print(MODE, MODEL, "r", r, "dim", len(best[0]), "balanced", len(best[1]),
              f"{time.time()-t0:.0f}s"); sys.stdout.flush()
    fn = f"results/step3_frontier_{MODE}_{MODEL}.json"
    try:
        prev = json.load(open(fn))
    except FileNotFoundError:
        prev = {}
    prev.update({str(k): v for k, v in out.items()})
    json.dump(dict(sorted(prev.items(), key=lambda kv: int(kv[0]))), open(fn, "w"), indent=1)
