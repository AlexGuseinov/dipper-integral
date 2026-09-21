"""Experimental soundness check of every frontier cube of dimension <= 16:
the certified bits must have zero cube sum for every trial (random constants,
independent random round keys)."""
import json, random, sys, zlib
import numpy as np
sys.path.insert(0, ".")
from dipper import fast as F

TRIALS = 400
out = []
for mode in ("add", "xor", "none"):
    try:
        fr = json.load(open(f"results/step3_frontier_{mode}_mp.json"))
    except FileNotFoundError:
        continue
    for r, v in fr.items():
        if v["dim"] > 16:
            continue
        rng = random.Random(zlib.crc32(f"{mode}|{r}".encode()))
        mask = sum(1 << j for j in v["balanced"])
        bad = 0
        for _ in range(TRIALS):
            s = F.cube_plaintexts(v["active"], rng.getrandbits(64))
            for _ in range(int(r)):
                s = F.T(s ^ np.uint64(rng.getrandbits(64)), mode)
            bad |= F.xor_reduce(s) & mask
        row = dict(mode=mode, rounds=int(r), dim=v["dim"], certified_bits=v["balanced"],
                   trials=TRIALS, contradictions=[j for j in range(64) if bad >> j & 1])
        out.append(row); print(row); sys.stdout.flush()
        assert not row["contradictions"]
json.dump(out, open("results/step3_frontier_empirical.json", "w"), indent=1)
