"""Independent validation of a monomial trail found by the SAT solver.

A satisfying assignment ("no certificate") is only meaningful if it is a real
monomial trail. This checker re-derives every layer from the cipher
specification and checks each transition against the local coefficient rules,
without using the CNF: key addition u <= w; S-box coefficient table computed
from the ANF; rotations and permutation as wiring; the ARX layer via the
retained-operand rule val(w) >= val(a), b == (w-a) | c (Lemma 1, verified
exhaustively), or the per-bit XOR/identity rules for the variants."""
from .anf import SBOX_MP, monomial_table

XOR1 = monomial_table(lambda xy: ((xy & 1) ^ (xy >> 1)) | (xy & 2), 2, 2)   # (x,y)->(x^y,y), from the ANF
from .cipher import PERM, ROT


def _rotl16(w, r):
    return ((w << r) | (w >> (16 - r))) & 0xFFFF


def _words(x):
    return (x >> 48) & 0xFFFF, (x >> 32) & 0xFFFF, (x >> 16) & 0xFFFF, x & 0xFFFF


def check_trail(masks, active, j, mode="add", final_mask=None, pattern=None):
    """masks: list of 64-bit ints [input, (key, sbox, mix, perm) * r].
    The trail must end in e_j, or in final_mask if it is given (a product of several state bits).
    If `pattern` is given (one key mask per round), the key monomial of the trail, taken bit by bit
    as (key-layer output) AND NOT (key-layer input), must equal it."""
    I = sum(1 << b for b in active)
    if masks[0] != I:
        return False, "input mask != cube"
    r = (len(masks) - 1) // 4
    x = masks[0]
    for t in range(r):
        k, sb, mx, pm = masks[1 + 4 * t: 5 + 4 * t]
        if x & ~k:
            return False, f"round {t+1}: key step violates u <= w"
        if pattern is not None and (k & ~x) != pattern[t]:
            return False, f"round {t+1}: key monomial differs from the pattern"
        for n in range(16):
            if SBOX_MP[(k >> 4 * n) & 15][(sb >> 4 * n) & 15] != 1:
                return False, f"round {t+1}: S-box {n} coefficient zero"
        a, b, c, d = _words(sb)
        a, b, c, d = (_rotl16(a, ROT[0]), _rotl16(b, ROT[1]), _rotl16(c, ROT[2]), _rotl16(d, ROT[3]))
        A, B, C, D = _words(mx)
        for (ai, bi, wo, co) in ((a, b, A, B), (c, d, C, D)):
            if mode == "add":
                if not (wo >= ai and (bi == ((wo - ai) | co))):
                    return False, f"round {t+1}: addition rule violated"
            elif mode == "xor":        # (x, y) -> (x ^ y, y), per bit exact table
                for i in range(16):
                    u = (ai >> i & 1) | (bi >> i & 1) << 1
                    v = (wo >> i & 1) | (co >> i & 1) << 1
                    if XOR1[u][v] != 1:
                        return False, f"round {t+1}: xor rule violated"
            else:
                if (ai, bi) != (wo, co):
                    return False, f"round {t+1}: identity violated"
        y = 0
        for i in range(64):
            if mx >> i & 1:
                y |= 1 << PERM[i]
        if y != pm:
            return False, f"round {t+1}: permutation wiring"
        x = pm
    if x != (1 << j if final_mask is None else final_mask):
        return False, "output mask != e_j" if final_mask is None else "output mask != final_mask"
    return True, "ok"
