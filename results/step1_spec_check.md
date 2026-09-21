# Step 1 — specification check and reproduction of the published integral

## Reference implementation vs. published test vectors (Table 3)

| Variant | Vector | Result |
|---|---|---|
| Dipper-64/128 | P=0123…CDEF, K=0001…0E0F | **reproduced** (4B46284387969060) |
| Dipper-64/128 | P=FF…FF, K=FF…FF | **reproduced** (6ABB4518063706B0) |
| Dipper-64/96 | P=0123…CDEF, K=0011…AABB | **not reproduced** (text-faithful impl: 7060A90BBB4D69C5) |
| Dipper-64/96 | P=0, K=0 | **not reproduced** (text-faithful impl: 1D6E0C3187AA2116) |

Findings:
1. The 128-bit vectors are reproduced only if the round key is `RK_r = K^(r)[63:0]`;
   Eq. (7) of the paper states `K^(r)[127:64]`. Either the text or the reference
   code uses the other half; the code (vectors) is taken as normative here.
2. The 96-bit vectors could not be reproduced under Eqs. (7)–(10), nor under a
   brute-force search over: all 720 word permutations, all positions of the two
   rotations (both directions), every 3- or 4-subset of S-box words, all 6
   round-constant word positions and 3 extraction windows
   (`scripts/spec_check_96_bruteforce.c`, zero-key vector). The authors' reference
   code should be consulted; this is reported as an open erratum.
3. The round function itself is confirmed: the 128-bit vectors exercise all
   28 rounds of it. Since every integral certificate in this work holds for
   arbitrary independent round keys, neither discrepancy affects the results.

## Structural identities (tests/test_vectors.py, tests/test_fast.py)
- `T^{-1}(T(x)) = x` and `T^{-1}(R_k(x)) = x XOR k` for 2000 random inputs, for
  Dipper and the XOR / no-addition variants.
- Round constants: period 31, RC_1..RC_5 = 01,02,05,0A,15 (matches Table 2).
- numpy engine matches the reference bit-exactly.

## Reproduction of the published experimental integral (Section 9)
Published setup: one 16-bit word saturated, other 48 bits constant; bound stated
as "16-bit saturation distinguishers of at most five rounds".

Final run (`scripts/step1_empirical_integral.py add 7 1000`): 1000 trials with fresh
random constants and independent random round keys + 16 trials with the real
128-bit key schedule; a bit counts as balanced only if its sum is 0 in all 1016 trials.
(A first run with 80 trials reported word C: 39 bits at r=4 and 4 bits at r=5; the two
extra bits are non-zero with probability ~0.5-1% and disappear with 1016 trials.
Every entry below equals the MP-certified count, see step4_tightness_add.json.)

| Saturated word | r=1 | r=2 | r=3 | r=4 | r=5 | r=6 |
|---|---|---|---|---|---|---|
| A | 64 | 64 | 64 | 38 | 3 | 0 |
| B | 64 | 56 | 24 | 0 | 0 | 0 |
| C | 64 | 64 | 64 | 38 | 3 | 0 |
| D | 64 | 60 | 25 | 0 | 0 | 0 |

(balanced bits of the state S^(r) = output of r full rounds, Eq. (5))

- The published maximum of five rounds is reproduced, and the round count refers
  to the direct state/ciphertext S^(r).
- Free final round: in every trial, XOR_cube T^{-1}(S^(r+1)) == XOR_cube S^(r)
  held exactly. Hence the 5-round property is also a 6-round distinguisher on the
  output-transformed ciphertext T^{-1}(C), without any key guess (RK_6 cancels).
  This is an extension of the published result under a different output test,
  not a contradiction of it.

## What we will prove (fixed scope for Steps 2–4)
- Statement form: "for every choice of the constant bits and of all round keys
  (independent, hence also for both real key schedules), bit j of S^(r) sums to 0
  over cube I." Certificate = infeasibility of a sound monomial-trail model.
- No certificate beyond round r means only: no certificate in that model/family.
- Round counts are reported both for S^(r) and, separately, for the r+1-round
  output-transformed test.
