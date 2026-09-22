"""Second pass for step23: for the gap bits still without explicit keys, try all
round keys of rounds 2..r of weight <= 2 inside the pattern v, each combined with
random round-1 keys inside v_1 (the round-1 key acts as the plaintext constant)."""
import itertools, json, random, sys, time
import numpy as np
sys.path.insert(0, ".")
from dipper import fast
from dipper.cipher import encrypt_rk

F = "results/step23_gap_witness_keys.json"
data = json.load(open(F))
pres = {(c["cube"], c["rounds"], c["bit"], tuple(c["active"])): c
        for c in json.load(open("results/step22_gap_presence.json"))["cases"]}
R1 = int(sys.argv[1]) if len(sys.argv) > 1 else 24


def cs_fast(act, rks, j, base):
    s = base
    for rk in rks:
        s = fast.T(s ^ np.uint64(rk))
    return (fast.xor_reduce(s) >> j) & 1


def cs_ref(act, rks, j):
    acc = 0
    for x in range(1 << len(act)):
        acc ^= encrypt_rk(sum(((x >> i) & 1) << b for i, b in enumerate(act)), rks)
    return (acc >> j) & 1


t00 = time.time()
for rec in data["cases"]:
    if rec.get("reference_check"):
        continue
    key = (rec["cube"], rec["rounds"], rec["bit"], tuple(rec["active"]))
    act, r, j = list(key[3]), key[1], key[2]
    v = [int(m, 16) for m in pres[key]["pattern"]]
    later = [(t, i) for t in range(1, r) for i in range(64) if (v[t] >> i) & 1]
    rng = random.Random(99 + j)
    base = fast.cube_plaintexts(act, 0)
    t0, found, tried = time.time(), None, 0
    r1s = [0, v[0]] + [v[0] & (rng.getrandbits(64) if n % 2 else rng.getrandbits(64) & rng.getrandbits(64))
                       for n in range(R1)]
    for w in (0, 1, 2):
        for combo in itertools.combinations(later, w):
            ks = [0] * r
            for t, i in combo:
                ks[t] |= 1 << i
            for k1 in r1s:
                ks[0] = k1
                tried += 1
                if cs_fast(act, ks, j, base):
                    found = list(ks); break
            if found: break
        if found: break
    rec["pass2_tried"] = tried
    rec["pass2_secs"] = round(time.time() - t0, 1)
    if found:
        rec["round_keys"] = [f"{k:016X}" for k in found]
        rec["reference_check"] = bool(cs_ref(act, found, j))
    print(key[:3], "found" if found else "none", tried, rec["pass2_secs"], rec.get("reference_check"), flush=True)
    json.dump(data, open(F, "w"), indent=1)
data["summary"] = {"cases": len(data["cases"]),
                   "with_explicit_key": sum(1 for c in data["cases"] if c.get("reference_check"))}
json.dump(data, open(F, "w"), indent=1)
print(data["summary"], round(time.time() - t00, 1))
