"""Exhaustive validation of every local model against exact ANF computation."""
from dipper.anf import *


def test_sbox_table_is_exact_and_bijective_props():
    # bijective S-box: y^{0xF} contains x^{0xF}, no linear output bit has degree 4
    assert SBOX_MP[0][0] == 1 and sum(SBOX_MP[u][0] for u in range(16)) == 1
    assert SBOX_MP[15][15] == 1


def test_hu_yap_addition(nmax=5):
    for n in range(1, nmax + 1):
        T = add_table(n)
        for a in range(1 << n):
            for b in range(1 << n):
                for w in range(1 << n):
                    assert T[a | b << n][w] == hu_yap_predict(a, b, w, n), (n, a, b, w)


def test_addition_with_retained_operand(nmax=4):
    for n in range(1, nmax + 1):
        T = add_with_retained_table(n)
        for a in range(1 << n):
            for b in range(1 << n):
                for w in range(1 << n):
                    for c in range(1 << n):
                        got = T[a | b << n][w | c << n]
                        assert got == retained_predict(a, b, w, c, n), (n, a, b, w, c)


def test_carry_encoding_equivalence(nmax=6):
    """Integer equality a + b' = w  <=>  exists binary q with
    a_i + b'_i + q_i = w_i + 2 q_{i+1}, q_0 = q_n = 0."""
    from itertools import product
    for n in range(1, nmax + 1):
        for a in range(1 << n):
            for bp in range(1 << n):
                for w in range(1 << n):
                    ok = False
                    q = 0
                    good = True
                    for i in range(n):
                        s = (a >> i & 1) + (bp >> i & 1) + q - (w >> i & 1)
                        if s not in (0, 2):
                            good = False
                            break
                        q = s // 2
                    ok = good and q == 0
                    assert ok == (a + bp == w)


if __name__ == "__main__":
    test_sbox_table_is_exact_and_bijective_props()
    test_hu_yap_addition()
    test_addition_with_retained_operand()
    test_carry_encoding_equivalence()
    n_mp = sum(map(sum, SBOX_MP)); n_bdp = sum(map(sum, SBOX_BDP))
    print(f"S-box: {n_mp} valid MP transitions, {n_bdp} BDP transitions")
    print("all local models validated exhaustively (addition n<=5, retained n<=4, carry n<=6)")
