"""Step 1: reproduce the published experimental 16-bit word-saturation integrals.

For each saturated word (A,B,C,D) and each round count r, we compute the XOR sum
of the state S^(r) over the 2^16-plaintext cube for many independent trials
(fresh random constants for the 48 inactive bits and fresh independent random
round keys). A bit is reported 'empirically balanced' only if its sum is zero in
every trial. We also check, for every trial, that
    XOR_cube T^{-1}(S^(r+1)) == XOR_cube S^(r)
(the free final round: RK_{r+1} cancels over an even-size cube)."""
import json, random, sys, time
import numpy as np
sys.path.insert(0, ".")
from dipper import fast as F
from dipper.cipher import expand_key

WORDS = {"A": 48, "B": 32, "C": 16, "D": 0}
MAXR, TRIALS, KS_TRIALS = 7, 64, 16


def run(mode="add", seed=2026):
    rng = random.Random(seed)
    out = {}
    for name, lo in WORDS.items():
        act = list(range(lo, lo + 16))
        zero_all = [(1 << 64) - 1] * (MAXR + 1)        # AND of "sum==0" masks
        free_round_ok = True
        for t in range(TRIALS + KS_TRIALS):
            const = rng.getrandbits(64)
            if t < TRIALS:
                rks = [rng.getrandbits(64) for _ in range(MAXR + 1)]
            else:
                rks = expand_key(rng.getrandbits(128), 128, MAXR + 1)
            s = F.cube_plaintexts(act, const)
            sums = []
            for r in range(1, MAXR + 2):
                s = F.T(s ^ np.uint64(rks[r - 1]), mode)
                sums.append((F.xor_reduce(s), F.xor_reduce(F.T_inv(s, mode))))
            for r in range(1, MAXR + 1):
                zero_all[r] &= ~sums[r - 1][0] & ((1 << 64) - 1)
                if sums[r][1] != sums[r - 1][0]:
                    free_round_ok = False
        out[name] = {
            "balanced_bits_per_round": {r: bin(zero_all[r]).count("1") for r in range(1, MAXR + 1)},
            "balanced_mask_hex": {r: f"{zero_all[r]:016X}" for r in range(1, MAXR + 1)},
            "free_round_identity_holds": free_round_ok,
        }
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "add"
    if len(sys.argv) > 2:
        MAXR = int(sys.argv[2])
    if len(sys.argv) > 3:
        TRIALS = int(sys.argv[3])
    t0 = time.time()
    res = {"mode": mode, "trials_random_rk": TRIALS, "trials_real_ks128": KS_TRIALS,
           "words": run(mode)}
    res["seconds"] = round(time.time() - t0, 1)
    json.dump(res, open("results/step1_empirical_integral.json" if mode == "add" else f"results/empirical_word_cubes_{mode}.json", "w"), indent=1)
    for w, v in res["words"].items():
        print(w, v["balanced_bits_per_round"], "free-round identity:", v["free_round_identity_holds"])
    print("seconds", res["seconds"])
