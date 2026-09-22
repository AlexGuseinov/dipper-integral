"""Reproduces the forced-mask analysis (A6 of the handover) from scratch.

Outputs results/step14_forced_masks.json: the forced set of every input
pattern, its size per nibble class, which nibbles/words are separable by a
single position or by a full support, and which partitions are feasible."""
import json, sys, time
sys.path.insert(0, ".")
from dipper.forced import forced_set, separable

mode = sys.argv[1] if len(sys.argv) > 1 else "add"
t0 = time.time()
F_bit = {i: forced_set(i, mode) for i in range(64)}
by_nibble = {n: F_bit[4 * n] for n in range(16)}
const_on_nibble = all(F_bit[4 * n + b] == by_nibble[n] for n in range(16) for b in range(4))
sizes = {n: bin(by_nibble[n]).count("1") for n in range(16)}
inter = 0xFFFFFFFFFFFFFFFF
for v in F_bit.values():
    inter &= v
single = {n: [p for p in range(64) if (by_nibble[n] >> p) & 1 == 0
              and all((by_nibble[m] >> p) & 1 for m in range(16) if m != n)]
          for n in range(16)}
full_support = {n: separable([n], by_nibble) for n in range(16)}
words = {"D": [0, 1, 2, 3], "C": [4, 5, 6, 7], "B": [8, 9, 10, 11], "A": [12, 13, 14, 15]}
word_single = {w: [p for p in range(64)
                   if all((by_nibble[n] >> p) & 1 == 0 for n in ns)
                   and all((by_nibble[m] >> p) & 1 for m in range(16) if m not in ns)]
               for w, ns in words.items()}
partitions = {
    "16 nibbles": [[n] for n in range(16)],
    "4 words": list(words.values()),
    "2 halves": [words["A"] + words["B"], words["C"] + words["D"]],
    "{A},{C},{B,D}": [words["A"], words["C"], words["B"] + words["D"]],
    "{A},{C},{B},{D}": list(words.values()),
    "{A},{B,C,D}": [words["A"], words["B"] + words["C"] + words["D"]],
    "{C},{A,B,D}": [words["C"], words["A"] + words["B"] + words["D"]],
    "{A,C},{B,D}": [words["A"] + words["C"], words["B"] + words["D"]],
}
part_res = {name: {"feasible": all(separable(cl, by_nibble) is not None for cl in classes),
                   "supports": {str(cl): separable(cl, by_nibble) for cl in classes}}
            for name, classes in partitions.items()}
out = {"mode": mode, "forced_constant_on_nibble": const_on_nibble,
       "forced_by_nibble_hex": {n: f"{v:016X}" for n, v in by_nibble.items()},
       "sizes_by_nibble": sizes, "intersection_over_all_inputs": bin(inter).count("1"),
       "single_position_separable_nibbles": {n: v for n, v in single.items() if v},
       "full_support_separable_nibbles": {n: v for n, v in full_support.items() if v is not None},
       "word_single_position": {w: v for w, v in word_single.items() if v},
       "partitions": part_res, "seconds": round(time.time() - t0, 1)}
json.dump(out, open(f"results/step14_forced_masks_{mode}.json", "w"), indent=1)
print("forced set constant on each nibble:", const_on_nibble)
print("sizes by nibble:", sizes)
print("intersection over all 64 inputs (positions forced for every input):", out["intersection_over_all_inputs"])
print("single-position separable nibbles:", out["single_position_separable_nibbles"])
print("full-support separable nibbles:", sorted(out["full_support_separable_nibbles"]))
print("word separated by a single position:", out["word_single_position"])
print("feasible partitions:", [k for k, v in part_res.items() if v["feasible"]])
