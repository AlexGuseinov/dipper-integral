"""Consequences of the certified 6-round properties.

(1) Free final round: for any r-round certificate on bit j of S^(r),
    XOR_cube T^{-1}(C_{r+1})_j = 0 for every key (RK_{r+1} cancels).
(2) One more round (r+2): bit j of T^{-1}(T^{-1}(C) XOR RK_{r+2}) is balanced;
    evaluating it requires guessing the bits of RK_{r+2} on which bit j of T^{-1}
    depends. We compute this dependency set exactly (structurally) and verify it
    by random bit flips."""
import json, random, sys
sys.path.insert(0, ".")
from dipper.cipher import T_inv, PERM, ROT

WORD = {0: "D", 1: "C", 2: "B", 3: "A"}


def dependency_of_Tinv_bit(j):
    """Set of bits of Z on which bit j of T^{-1}(Z) = S^{-1}(mix^{-1}(P^{-1}(Z))) depends."""
    nib = j // 4
    deps = set()
    for b in range(4 * nib, 4 * nib + 4):          # inputs of the inverse S-box = mix^{-1} outputs
        w, i = b // 16, b % 16                     # word index (0=D) and bit in word
        # mix^{-1}: rotate right by ROT[word] after (for A, C) subtraction of B, D
        rot = ROT[3 - w]
        src = (i + rot) % 16                       # bit of the (subtracted) word before rotr
        if WORD[w] in "BD":
            pre = [16 * w + src]
        else:                                      # A - B or C - D: bits 0..src of both
            partner = w + 1                        # A(3)-B(2), C(1)-D(0)? fix below
            partner = 2 if w == 3 else 0
            pre = [16 * w + t for t in range(src + 1)] + [16 * partner + t for t in range(src + 1)]
        for p in pre:                              # before P^{-1}: bit p of P^{-1}(Z) = Z[PERM[p]]
            deps.add(PERM[p])
    return deps


def verify(j, deps, trials=20000, seed=1):
    rng = random.Random(seed)
    seen = set()
    for _ in range(trials):
        z = rng.getrandbits(64); b = rng.randrange(64)
        if (T_inv(z) >> j & 1) != (T_inv(z ^ (1 << b)) >> j & 1):
            seen.add(b)
    return seen


if __name__ == "__main__":
    cert = json.load(open("results/step3_maximal_cubes_add.json"))["add"]["mp"]["6"]["balanced_by_const_bit"]
    front = json.load(open("results/step3_frontier_add_mp.json"))["6"]
    bits = sorted({j for v in cert.values() for j in v})
    out = {}
    for j in bits:
        d = dependency_of_Tinv_bit(j)
        s = verify(j, d)
        assert s <= d, (j, sorted(s - d))
        out[j] = {"guessed_key_bits": len(d), "observed_dependencies": len(s),
                  "cubes_63": [int(p) for p, v in cert.items() if j in v],
                  "in_60dim_frontier_cube": j in front["balanced"]}
        print(j, out[j])
    # 8-round partial key recovery with the cheapest bit in the 60-dim cube
    best = min((j for j in bits if out[j]["in_60dim_frontier_cube"]), key=lambda j: out[j]["guessed_key_bits"])
    g = out[best]["guessed_key_bits"]
    n_struct = 8   # measured wrong-guess survival ~0.565 per structure (step5_attack_smallscale): 15*0.565^8 < 0.2
    data_log2 = 60 + __import__("math").log2(n_struct)
    summary = {"bit": best, "guessed_RK8_bits": g, "structures_2^60": n_struct,
               "data_log2": round(data_log2, 2),
               "time_log2_partial_decryptions": round(data_log2, 2),
               "note": "distinguisher 6 rounds + free round 7 + 1 key-guessed round = 8 rounds"}
    print("8-round partial key recovery:", summary)
    json.dump({"per_bit": out, "attack8": summary}, open("results/step5_key_recovery.json", "w"), indent=1)
