"""Exact algebraic normal forms and local monomial-prediction tables."""
from itertools import product
from .cipher import SBOX


def moebius(truth):
    """ANF coefficients of a Boolean function given by its truth table (list of 0/1)."""
    a = list(truth)
    n = len(a).bit_length() - 1
    for i in range(n):
        for x in range(len(a)):
            if x >> i & 1:
                a[x] ^= a[x ^ (1 << i)]
    return a


def monomial_table(f, n_in, n_out):
    """T[u][v] = coefficient of x^u in prod_j f_j(x)^{v_j}  (exact MP table)."""
    T = [[0] * (1 << n_out) for _ in range(1 << n_in)]
    for v in range(1 << n_out):
        truth = [int((f(x) & v) == v) for x in range(1 << n_in)]
        coeffs = moebius(truth)
        for u in range(1 << n_in):
            T[u][v] = coeffs[u]
    return T


SBOX_MP = monomial_table(lambda x: SBOX[x], 4, 4)

# Conventional (two-subset) bit-based division property of the S-box:
# k -> k' is a division trail iff some monomial x^u with u >= k appears in y^{k'}.
SBOX_BDP = [[int(any(SBOX_MP[u][v] for u in range(16) if u & k == k))
             for v in range(16)] for k in range(16)]


def add_with_retained_table(n):
    """Exact MP table of (x, y) -> (x + y mod 2^n, y) on 2n bits.
    Input exponent (a, b), output exponent (w, c) packed as a | b<<n, w | c<<n."""
    mask = (1 << n) - 1
    f = lambda xy: ((xy & mask) + (xy >> n) & mask) | ((xy >> n) << n)
    return monomial_table(f, 2 * n, 2 * n)


def add_table(n):
    """Exact MP table of (x, y) -> x + y mod 2^n."""
    mask = (1 << n) - 1
    return monomial_table(lambda xy: ((xy & mask) + (xy >> n)) & mask, 2 * n, n)


def hu_yap_predict(a, b, w, n):
    """Hu-Yap (ToSC 2024): [x^a y^b] (x+y)^w = 1  iff  a + b = w over the integers."""
    return int(a + b == w)


def retained_predict(a, b, w, c, n):
    """Our local rule for (x, y) -> (x+y, y): unique b' = w - a must satisfy
    0 <= b' and (b' | c) == b."""
    bp = w - a
    return int(bp >= 0 and (bp | c) == b)
