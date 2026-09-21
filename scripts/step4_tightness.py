"""C2 (precision): compare certified balanced bits with experiment on cubes
small enough to evaluate. For each (cube, r):
  cert   = bits certified by the model (sound => must be zero in every trial)
  emp    = bits with zero cube sum in all N1 trials (random constants and
           independent random round keys)
  gap    = emp \\ cert, re-tested with N2 further trials ('persistent' if still zero)
A persistent gap bit is an empirically stable zero-sum property that the model
does not certify: either an exact property lost to trail cancellation, or a
cube sum that is non-zero only with small probability. Both are reported."""
import json, random, sys, time, zlib
import numpy as np
sys.path.insert(0, ".")
from dipper import fast as F
from dipper.models import Checker

N1, N2 = 200, 3000
MODE = sys.argv[1] if len(sys.argv) > 1 else "add"


def sums(active, r, trials, rng):
    """yield the XOR-sum of S^(r) for independent trials"""
    for _ in range(trials):
        s = F.cube_plaintexts(active, rng.getrandbits(64))
        for _ in range(r):
            s = F.T(s ^ np.uint64(rng.getrandbits(64)), MODE)
        yield F.xor_reduce(s)


def zero_mask(active, r, trials, rng, bits_mask=(1 << 64) - 1):
    z = bits_mask
    for v in sums(active, r, trials, rng):
        z &= ~v
        if z == 0:
            break
    return z & bits_mask


def cubes(rng):
    out = [("word-" + w, list(range(lo, lo + 16))) for w, lo in (("A", 48), ("B", 32), ("C", 16), ("D", 0))]
    for k in (1, 2, 3):
        for _ in range(4):
            nib = sorted(rng.sample(range(16), k))
            out.append((f"nibbles{nib}", [4 * n + b for n in nib for b in range(4)]))
    for d in (4, 8, 12):
        for _ in range(4):
            out.append((f"random{d}", sorted(rng.sample(range(64), d))))
    return out


if __name__ == "__main__":
    rng = random.Random(4242)
    rows, t0 = [], time.time()
    for name, act in cubes(rng):
        for r in (2, 3, 4, 5):
            ch = Checker(set(act), r, "mp", MODE)
            res = ch.balanced_bits(); ch.close()
            cert = sum(1 << j for j, v in res.items() if v == "balanced")
            emp = zero_mask(act, r, N1, random.Random(zlib.crc32(f"{name}|{act}|{r}".encode())))
            assert cert & ~emp == 0, ("UNSOUND", name, r)
            gap = emp & ~cert
            persistent = zero_mask(act, r, N2 if len(act) <= 12 else N2 // 3,
                                   random.Random(zlib.crc32(f"retest|{act}|{r}".encode())), gap) if gap else 0
            row = dict(cube=name, dim=len(act), active=act, rounds=r,
                       certified=bin(cert).count("1"), empirical_zero=bin(emp).count("1"),
                       gap=bin(gap).count("1"), gap_persistent=bin(persistent).count("1"),
                       persistent_bits=[j for j in range(64) if persistent >> j & 1])
            rows.append(row)
            print(f"{name:22s} d={len(act):2d} r={r} cert={row['certified']:2d} "
                  f"emp={row['empirical_zero']:2d} gap={row['gap']:2d} persistent={row['gap_persistent']:2d}")
            sys.stdout.flush()
    json.dump({"mode": MODE, "N1": N1, "N2": N2, "rows": rows,
               "seconds": round(time.time() - t0, 1)},
              open(f"results/step4_tightness_{MODE}.json", "w"), indent=1)
