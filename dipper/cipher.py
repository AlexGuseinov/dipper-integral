"""Reference implementation of the Dipper block cipher (Huseynli, Imamverdiyev,
Alizadeh, Cryptography 10(4):52, 2026). Bit 0 = LSB; state S = A||B||C||D with
A = S[63:48]. Each round: AddRoundKey, SubCells, WordRotations, half-state
modular addition, GIFT-64 bit permutation. No final whitening."""

SBOX = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9,
        0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]      # GIFT S-box
SBOX_INV = [SBOX.index(i) for i in range(16)]
ROT = (1, 4, 7, 11)                                   # left rotations of A,B,C,D
M16 = 0xFFFF
ROUNDS = 28


def perm_index(i):
    """GIFT-64 bit permutation: bit i of the input moves to bit P(i)."""
    return 4 * (i // 16) + 16 * ((3 * ((i % 16) // 4) + (i % 4)) % 4) + (i % 4)


PERM = [perm_index(i) for i in range(64)]
PERM_INV = [0] * 64
for _i, _p in enumerate(PERM):
    PERM_INV[_p] = _i
assert sorted(PERM) == list(range(64))


def rotl16(x, s):
    s %= 16
    return ((x << s) | (x >> (16 - s))) & M16


def rotr16(x, s):
    return rotl16(x, 16 - (s % 16))


def words(s):
    return (s >> 48) & M16, (s >> 32) & M16, (s >> 16) & M16, s & M16


def join(a, b, c, d):
    return (a << 48) | (b << 32) | (c << 16) | d


def sub_cells(s, box=SBOX):
    out = 0
    for j in range(16):
        out |= box[(s >> (4 * j)) & 0xF] << (4 * j)
    return out


def bit_perm(s, table=PERM):
    out = 0
    for i in range(64):
        if (s >> i) & 1:
            out |= 1 << table[i]
    return out


def mix(s, mode="add"):
    """Word rotations followed by the half-state ARX layer.
    mode: 'add' (Dipper), 'xor' (additions replaced by XOR), 'none' (removed)."""
    a, b, c, d = words(s)
    a, b, c, d = rotl16(a, ROT[0]), rotl16(b, ROT[1]), rotl16(c, ROT[2]), rotl16(d, ROT[3])
    if mode == "add":
        a, c = (a + b) & M16, (c + d) & M16
    elif mode == "xor":
        a, c = a ^ b, c ^ d
    elif mode != "none":
        raise ValueError(mode)
    return join(a, b, c, d)


def mix_inv(s, mode="add"):
    a, b, c, d = words(s)
    if mode == "add":
        a, c = (a - b) & M16, (c - d) & M16
    elif mode == "xor":
        a, c = a ^ b, c ^ d
    return join(rotr16(a, ROT[0]), rotr16(b, ROT[1]), rotr16(c, ROT[2]), rotr16(d, ROT[3]))


def T(s, mode="add"):
    """Keyless part of a round: SubCells, rotations, additions, permutation."""
    return bit_perm(mix(sub_cells(s), mode))


def T_inv(s, mode="add"):
    return sub_cells(mix_inv(bit_perm(s, PERM_INV), mode), SBOX_INV)


def round_function(s, rk, mode="add"):
    return T(s ^ rk, mode)


# ---------------------------------------------------------------- key schedule
def round_constants(n=ROUNDS):
    rc, l = [], 0x01
    for _ in range(n):
        rc.append(l)
        b = ((l >> 4) ^ (l >> 1)) & 1
        l = ((l << 1) | b) & 0x1F
    return rc


def _kwords(k, n):
    return [(k >> (16 * i)) & M16 for i in range(n)]      # index 0 = k0 (LSW)


def _kjoin(w):
    return sum(x << (16 * i) for i, x in enumerate(w))


def _sbox_top(w):
    return (SBOX[w >> 12] << 12) | (w & 0x0FFF)


def key_update_96(k, rc):
    k0, k1, k2, k3, k4, k5 = _kwords(k, 6)
    # (k5',k4',k3',k2',k1',k0') = (k3, k2, k1>>>2, k0>>>12, k5, k4)
    w = [k4, k5, rotr16(k0, 12), rotr16(k1, 2), k2, k3]
    for i in (1, 2, 4, 5):
        w[i] = _sbox_top(w[i])
    w[3] ^= rc                                             # K[52:48] ^= RC
    return _kjoin(w)


def key_update_128(k, rc):
    k0, k1, k2, k3, k4, k5, k6, k7 = _kwords(k, 8)
    # (k7',...,k0') = (k3, k2, k7, k6, k5, k4, k1>>>2, k0>>>12)
    w = [rotr16(k0, 12), rotr16(k1, 2), k4, k5, k6, k7, k2, k3]
    for i in (1, 3, 7):
        w[i] = _sbox_top(w[i])
    w[4] ^= rc                                             # K[68:64] ^= RC
    return _kjoin(w)


def expand_key(key, keysize, rounds=ROUNDS, window128="vectors"):
    """Round-key expansion.

    Dipper-64/128: Eq. (7) of the paper extracts RK_r = K^(r)[127:64], but the
    published test vectors (Table 3) are reproduced only when RK_r = K^(r)[63:0].
    window128="vectors" (default) follows the test vectors, "text" follows Eq. (7).

    Dipper-64/96: implemented exactly as Eqs. (7)-(10). The published 96-bit
    test vectors are NOT reproduced by this text-faithful implementation (see
    results/step1_spec_check.md). None of the integral results in this
    repository depend on the key schedule: all certificates hold for arbitrary
    independent round keys.
    """
    rks, k = [], key
    for rc in round_constants(rounds):
        if keysize == 96:
            rks.append(k & ((1 << 64) - 1))
            k = key_update_96(k, rc)
        elif keysize == 128:
            rks.append(k & ((1 << 64) - 1) if window128 == "vectors" else k >> 64)
            k = key_update_128(k, rc)
        else:
            raise ValueError(keysize)
    return rks


def encrypt_rk(p, rks, mode="add"):
    s = p
    for rk in rks:
        s = round_function(s, rk, mode)
    return s


def decrypt_rk(c, rks, mode="add"):
    s = c
    for rk in reversed(rks):
        s = T_inv(s, mode) ^ rk
    return s


def encrypt(p, key, keysize, rounds=ROUNDS):
    return encrypt_rk(p, expand_key(key, keysize, rounds))


def decrypt(c, key, keysize, rounds=ROUNDS):
    return decrypt_rk(c, expand_key(key, keysize, rounds))
