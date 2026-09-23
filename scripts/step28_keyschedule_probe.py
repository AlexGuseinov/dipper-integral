"""Feasibility probe: presence proofs with the real key schedule.

Model: dipper/models_ks.py (master-key variables, COPY into round keys, key-schedule
S-boxes and round constants). For the 63-dimensional cube with constant bit 0 and
several output bits, sample master-key monomials (greedy maximal and minimal) and
count their trails. Records how many counts are odd, even, or above the cap."""
import json, random, sys, time
sys.path.insert(0, ".")
from dipper.models_ks import TrailCounterKS

BITS = [0, 3, 17, 40, 21, 55]
SAMPLES = 20
CAP = 2000
out = {}
for ks in (128, 96):
    for R in (6, 7):
        t0 = time.time()
        c = TrailCounterKS(range(1, 64), R, ks)
        rng = random.Random(1000 * R + ks)
        st = {"odd": 0, "even": 0, "capped": 0, "no_trail": 0, "odd_examples": []}
        for j in BITS:
            for k in range(SAMPLES):
                w = c.greedy(j, rng, "max" if k % 2 == 0 else "min")
                if w is None:
                    st["no_trail"] += 1; break
                n = c.count(w, j, cap=CAP)
                if n is None:
                    st["capped"] += 1
                elif n % 2:
                    st["odd"] += 1; st["odd_examples"].append({"bit": j, "count": n, "weight": bin(w).count("1")})
                else:
                    st["even"] += 1
        st["secs"] = round(time.time() - t0, 1)
        out[f"{ks}|{R}"] = st
        print(ks, R, {k: v for k, v in st.items() if k != "odd_examples"}, flush=True)
json.dump(out, open("results/step28_keyschedule_probe.json", "w"), indent=1)
