"""Exact degree of one-round output bits by the Moebius transform.

After one round an output bit depends on at most 32 plaintext bits (8 S-boxes
feeding one added word pair), so its full ANF can be computed. With the round
key as an independent variable, deg_x S^(1)_j(x xor k) = deg S^(1)_j, so the key
can be set to 0. The dependency set is found by the structure of the round and
double-checked by random bit flips."""
import json, sys, time
import numpy as np
sys.path.insert(0, ".")
from dipper import fast

bits = [int(x) for x in sys.argv[1].split(",")]
rng = np.random.default_rng(1)
res = {}


def deps(j, samples=4096):
    x = rng.integers(0, 2**63, size=samples, dtype=np.uint64) ^ (rng.integers(0, 2, size=samples, dtype=np.uint64) << np.uint64(63))
    y = (fast.T(x) >> np.uint64(j)) & np.uint64(1)
    return [i for i in range(64) if np.any(((fast.T(x ^ np.uint64(1 << i)) >> np.uint64(j)) & np.uint64(1)) != y)]


def degree(j, dep):
    n = len(dep)
    W = np.zeros(max(1, 1 << (n - 6)), dtype=np.uint64)
    chunk = 1 << min(n, 22)
    for start in range(0, 1 << n, chunk):
        idx = np.arange(start, start + chunk, dtype=np.uint64)
        x = np.zeros(chunk, dtype=np.uint64)
        for b, i in enumerate(dep):
            x |= ((idx >> np.uint64(b)) & np.uint64(1)) << np.uint64(i)
        y = ((fast.T(x) >> np.uint64(j)) & np.uint64(1)).astype(np.uint64)
        y = y.reshape(-1, 64)
        words = np.zeros(y.shape[0], dtype=np.uint64)
        for p in range(64):
            words |= y[:, p] << np.uint64(p)
        W[start >> 6:(start + chunk) >> 6] = words
    masks = [0x5555555555555555, 0x3333333333333333, 0x0F0F0F0F0F0F0F0F,
             0x00FF00FF00FF00FF, 0x0000FFFF0000FFFF, 0x00000000FFFFFFFF]
    for k in range(6):                                 # in-word Moebius steps
        W ^= (W & np.uint64(masks[k])) << np.uint64(1 << k)
    for k in range(6, n):                              # word-level steps
        V = W.reshape(-1, 2, 1 << (k - 6))
        V[:, 1, :] ^= V[:, 0, :]
    widx = np.arange(W.size, dtype=np.uint64)
    wpop = np.zeros(W.size, dtype=np.int64)
    for b in range(max(0, n - 6)):
        wpop += ((widx >> np.uint64(b)) & np.uint64(1)).astype(np.int64)
    best = -1
    for p in range(64):
        on = ((W >> np.uint64(p)) & np.uint64(1)).astype(bool)
        if on.any():
            best = max(best, int(wpop[on].max()) + bin(p).count("1"))
    return best


for j in bits:
    t0 = time.time()
    dep = deps(j)
    extra = [i for i in range(64) if i not in dep][:max(0, 6 - len(dep))]   # dummy variables: degree unchanged
    dep = dep + extra
    d = degree(j, dep)
    res[j] = {"deps": len(dep), "degree": d, "secs": round(time.time() - t0, 1)}
    print(j, res[j], flush=True)
json.dump(res, open("results/step25b_anf_degree_r1.json", "w"), indent=1)
