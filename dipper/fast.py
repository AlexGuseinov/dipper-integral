"""Vectorised (numpy) Dipper rounds for cube-sum experiments."""
import numpy as np
from .cipher import SBOX, SBOX_INV, PERM, PERM_INV, ROT

U64 = np.uint64
_x = np.arange(1 << 16, dtype=np.uint32)


def _sb16(box):
    t = np.zeros(1 << 16, dtype=np.uint64)
    for j in range(4):
        t |= np.array(box, dtype=np.uint64)[(_x >> (4 * j)) & 0xF] << U64(4 * j)
    return t


SB16, SBI16 = _sb16(SBOX), _sb16(SBOX_INV)


def _perm_tables(table):
    out = np.zeros((8, 256), dtype=np.uint64)
    for byte in range(8):
        for v in range(256):
            acc = 0
            for b in range(8):
                if (v >> b) & 1:
                    acc |= 1 << table[8 * byte + b]
            out[byte, v] = acc
    return out


PT, PTI = _perm_tables(PERM), _perm_tables(PERM_INV)


def sub_cells(s, t=SB16):
    out = np.zeros_like(s)
    for q in range(4):
        out |= t[(s >> U64(16 * q)) & U64(0xFFFF)] << U64(16 * q)
    return out


def bit_perm(s, t=PT):
    out = np.zeros_like(s)
    for byte in range(8):
        out |= t[byte][(s >> U64(8 * byte)) & U64(0xFF)]
    return out


def _rotl(w, r):
    return ((w << U64(r)) | (w >> U64(16 - r))) & U64(0xFFFF)


def _rotr(w, r):
    return _rotl(w, 16 - r)


def mix(s, mode="add"):
    m = U64(0xFFFF)
    a, b, c, d = (s >> U64(48)) & m, (s >> U64(32)) & m, (s >> U64(16)) & m, s & m
    a, b, c, d = _rotl(a, ROT[0]), _rotl(b, ROT[1]), _rotl(c, ROT[2]), _rotl(d, ROT[3])
    if mode == "add":
        a, c = (a + b) & m, (c + d) & m
    elif mode == "xor":
        a, c = a ^ b, c ^ d
    return (a << U64(48)) | (b << U64(32)) | (c << U64(16)) | d


def mix_inv(s, mode="add"):
    m = U64(0xFFFF)
    a, b, c, d = (s >> U64(48)) & m, (s >> U64(32)) & m, (s >> U64(16)) & m, s & m
    if mode == "add":
        a, c = (a - b) & m, (c - d) & m
    elif mode == "xor":
        a, c = a ^ b, c ^ d
    a, b, c, d = _rotr(a, ROT[0]), _rotr(b, ROT[1]), _rotr(c, ROT[2]), _rotr(d, ROT[3])
    return (a << U64(48)) | (b << U64(32)) | (c << U64(16)) | d


def T(s, mode="add"):
    return bit_perm(mix(sub_cells(s), mode))


def T_inv(s, mode="add"):
    return sub_cells(mix_inv(bit_perm(s, PTI), mode), SBI16)


def xor_reduce(s):
    return int(np.bitwise_xor.reduce(s))


def cube_plaintexts(active_bits, const):
    """All 2^d plaintexts with the given active bit positions, others = const."""
    d = len(active_bits)
    idx = np.arange(1 << d, dtype=np.uint64)
    base = U64(const & ~sum(1 << b for b in active_bits) & ((1 << 64) - 1))
    p = np.full(1 << d, base, dtype=np.uint64)
    for j, b in enumerate(active_bits):
        p |= ((idx >> U64(j)) & U64(1)) << U64(b)
    return p
