import random
from dipper.cipher import *

VECTORS = [  # Table 3 of the Dipper paper
    (96,  0x0123456789ABCDEF, 0x00112233445566778899AABB, 0x5F189202D3152B8F),
    (96,  0x0000000000000000, 0x000000000000000000000000, 0xD873355EC63B1B4B),
    (128, 0x0123456789ABCDEF, 0x000102030405060708090A0B0C0D0E0F, 0x4B46284387969060),
    (128, 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0x6ABB4518063706B0),
]

def test_vectors():
    for ks, p, k, c in VECTORS:
        got = encrypt(p, k, ks)
        assert got == c, f"{ks}: got {got:016X} want {c:016X}"
        assert decrypt(c, k, ks) == p

def test_inverse_layers():
    rng = random.Random(1)
    for mode in ("add", "xor", "none"):
        for _ in range(2000):
            x, k = rng.getrandbits(64), rng.getrandbits(64)
            assert T_inv(T(x, mode), mode) == x
            assert T_inv(round_function(x, k, mode), mode) == x ^ k

def test_constants():
    rc = round_constants(31)
    assert len(set(rc)) == 31 and rc[0] == 1

if __name__ == "__main__":
    test_vectors(); test_inverse_layers(); test_constants(); print("all tests passed (96- and 128-bit vectors, inverses, constants)")
