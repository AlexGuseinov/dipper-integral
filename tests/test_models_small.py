"""Soundness checks of the full-round models against exact cube sums.

(1) Every bit certified balanced must have zero cube sum for many random keys.
(2) For r=1,2 with small cubes, compare against exact answers computed by
    brute force over random keys (model 'unknown' but empirically balanced is
    allowed - it indicates imprecision, never unsoundness)."""
import random, sys
import numpy as np
from dipper import fast as F
from dipper.models import Checker


def empirical_zero_mask(active, rounds, mode, trials=40, seed=0):
    rng = random.Random(seed)
    z = (1 << 64) - 1
    for _ in range(trials):
        s = F.cube_plaintexts(active, rng.getrandbits(64))
        for _ in range(rounds):
            s = F.T(s ^ np.uint64(rng.getrandbits(64)), mode)
        z &= ~F.xor_reduce(s) & ((1 << 64) - 1)
    return z


def check(active, rounds, model, mode):
    ch = Checker(active, rounds, model, mode)
    res = ch.balanced_bits(); ch.close()
    emp = empirical_zero_mask(active, rounds, mode)
    cert = sum(1 << j for j, v in res.items() if v == "balanced")
    assert cert & ~emp == 0, f"UNSOUND {model} {mode} r={rounds} bits {cert & ~emp:016X}"
    return bin(cert).count("1"), bin(emp).count("1")


if __name__ == "__main__":
    rng = random.Random(3)
    cases = [(list(range(48, 64)), r) for r in (1, 2, 3, 4)] + \
            [(sorted(rng.sample(range(64), 12)), r) for r in (1, 2, 3)]
    for active, r in cases:
        for mode in ("add", "xor", "none"):
            row = [f"{len(active)}b r={r} {mode:4s}"]
            for model in ("mp", "mpc", "bdp"):
                c, e = check(active, r, model, mode)
                row.append(f"{model}:{c}/{e}")
            print("  ".join(row)); sys.stdout.flush()
    print("soundness OK: no certified bit contradicted by experiment")
