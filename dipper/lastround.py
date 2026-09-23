"""Helpers for the last round: which S-box output an output bit of S^(r) is, and ANFs."""
from .cipher import PERM_INV, ROT, SBOX

_WORD_BASE = {3: 48, 2: 32, 1: 16, 0: 0}
_ROT_OF = {3: ROT[0], 2: ROT[1], 1: ROT[2], 0: ROT[3]}


def retained(j):
    """If output bit j of S^(r) comes from a retained word (B or D) of the last ARX layer,
    return (n, i): it is output bit i of S-box n of the last round. Otherwise None."""
    pos = PERM_INV[j]
    w, i = pos // 16, pos % 16
    if w not in (2, 0):
        return None
    q = _WORD_BASE[w] + ((i - _ROT_OF[w]) % 16)
    return q // 4, q % 4


def anf_bits(bits):
    """ANF support (set of monomial masks) of the XOR of the given GIFT S-box output bits."""
    tt = [sum((SBOX[x] >> b) & 1 for b in bits) & 1 for x in range(16)]
    co = list(tt)
    for i in range(4):
        for x in range(16):
            if x >> i & 1:
                co[x] ^= co[x ^ (1 << i)]
    return {u for u in range(16) if co[u]}
