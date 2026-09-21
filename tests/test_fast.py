import random, numpy as np
from dipper import cipher as C, fast as F

def test_fast_matches_reference():
    rng = random.Random(7)
    xs = [rng.getrandbits(64) for _ in range(300)]
    arr = np.array(xs, dtype=np.uint64)
    for mode in ("add", "xor", "none"):
        got = F.T(arr, mode)
        assert [int(v) for v in got] == [C.T(x, mode) for x in xs]
        assert [int(v) for v in F.T_inv(got, mode)] == xs

if __name__ == "__main__":
    test_fast_matches_reference(); print("fast implementation matches reference")
