# Step 1 — specification check and reproduction of the published integral

## Reference implementation vs. published test vectors (Table 3) — RESOLVED

All four vectors are reproduced; the implementation agrees with the authors'
reference code (github.com/AlexGuseinov/Dipper-lightweight-cipher,
`yosys synthesis/Dipper_verilog/ref/dipper_reference.py`, Spec v1.1) on 1000
random encryptions.

The published paper's key-schedule text contains two errors (spec v1.1 and the
reference code are consistent with each other):
1. Dipper-64/128 round key: paper Eq. (7) says K[127:64]; spec/code use K[63:0].
2. Dipper-64/96 S-boxes: paper Eq. (9) says top nibble [15:12] of words 1,2,4,5;
   spec/code use bits K[95:92], K[71:68], K[47:44], K[23:20] = k5[15:12], k4[7:4],
   k2[15:12], k1[7:4]. (Spec comments call these "top nibbles"; that is how the
   error entered the paper.)

History: before the reference code was available, a brute-force search over
key-schedule conventions (`scripts/spec_check_96_bruteforce.c`) found no match —
it only allowed top-nibble S-box positions, which is exactly the wrong assumption.

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
