"""Small-scale end-to-end check of the key-recovery procedure of Section 'Consequences'.

Same structure as the 8-round attack (6-round certificate + free round + one
key-guessed round), scaled down to the 4-round certificate of the 4-dimensional
cube {60,61,62,63} (bit 1 of S^(4) certified), i.e. a 6-round attack that is
fully executable. For random master keys (real 128-bit schedule) we record how
many of the 16 guesses of the 4 relevant RK_6 bits survive after k structures,
and whether the right guess always survives."""
import json, random, sys
sys.path.insert(0, ".")
from dipper.cipher import encrypt_rk, expand_key, T_inv
from scripts.step5_key_recovery import dependency_of_Tinv_bit

CUBE, BIT, R_CERT = [60, 61, 62, 63], 1, 4
DEPS = sorted(dependency_of_Tinv_bit(BIT))


def guess_to_mask(g):
    return sum(((g >> i) & 1) << b for i, b in enumerate(DEPS))


def run(trials=200, max_structs=8, seed=5):
    rng = random.Random(seed)
    surv = [[0] * (max_structs + 1) for _ in range(trials)]
    right_always = True
    for t in range(trials):
        rks = expand_key(rng.getrandbits(128), 128, R_CERT + 2)
        right = sum(((rks[-1] >> b) & 1) << i for i, b in enumerate(DEPS))
        alive = set(range(16))
        surv[t][0] = 16
        for s in range(1, max_structs + 1):
            const = rng.getrandbits(64)
            cts = []
            for v in range(1 << len(CUBE)):
                p = const & ~sum(1 << b for b in CUBE)
                for i, b in enumerate(CUBE):
                    p |= ((v >> i) & 1) << b
                cts.append(T_inv(encrypt_rk(p, rks)))     # keyless inversion of last round
            for g in list(alive):
                acc = 0
                for z in cts:
                    acc ^= T_inv(z ^ guess_to_mask(g)) >> BIT & 1
                if acc:
                    alive.discard(g)
            if right not in alive:
                right_always = False
            surv[t][s] = len(alive)
    mean = [sum(row[s] for row in surv) / trials for s in range(max_structs + 1)]
    return {"deps_Z_bits": DEPS, "right_key_always_survives": right_always,
            "mean_surviving_guesses_after_k_structures": [round(x, 2) for x in mean],
            "fraction_unique_after_k": [round(sum(row[s] == 1 for row in surv) / trials, 3)
                                        for s in range(max_structs + 1)]}


if __name__ == "__main__":
    res = run()
    print(res)
    json.dump(res, open("results/step5_attack_smallscale.json", "w"), indent=1)
