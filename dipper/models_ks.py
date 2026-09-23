"""Monomial-trail model of reduced-round Dipper WITH the key schedule.

The key variables are the master-key bits. Each round key RK_r = K^(r)[63:0] is a
COPY of the low half of the key state; the key update is wiring (word permutation,
rotations), four GIFT S-boxes on key nibbles, and the round-constant XOR. A trail
now carries a master-key mask; the coefficient of x^u K^w in S^(r)_j equals the
number of trails with input mask u, master-key mask w and output e_j, mod 2.
Local rules: COPY x -> (y1, y2): x = y1 OR y2 (MP); XOR (state, round-key bit) ->
out: out = OR, at most one input; XOR with a constant 1: u <= v, with 0: u = v."""
from pysat.solvers import Solver
from .models import Model, sbox_layer, mix_layer, perm_layer, rotl_vars
from .anf import SBOX_MP
from .cipher import round_constants

M = 16


def _rotr(w, r):
    return rotl_vars(w, (16 - r) % 16)


def _key_sbox(m, nib):
    out = m.vars(4)
    def ok(bits):
        u = sum(b << i for i, b in enumerate(bits[:4])); v = sum(b << i for i, b in enumerate(bits[4:]))
        return SBOX_MP[u][v] == 1
    m.table(list(nib) + out, ok)
    return out


def _const_xor(m, x, c):
    y = m.var()
    if c:
        m.leq(x, y)
    else:
        m.eq(x, y)
    return y


def key_update(m, K, keysize, rc):
    """K: list of key-state mask variables (bit 0 = LSB). Returns the updated list."""
    words = [K[16 * i:16 * i + 16] for i in range(keysize // 16)]
    if keysize == 128:
        k0, k1, k2, k3, k4, k5, k6, k7 = words
        w = [_rotr(k0, 12), _rotr(k1, 2), k4, k5, k6, k7, k2, k3]
        for i in (1, 3, 7):
            w[i] = w[i][:12] + _key_sbox(m, w[i][12:16])
        w[4] = [_const_xor(m, w[4][b], (rc >> b) & 1) if b < 5 else w[4][b] for b in range(16)]
        return [v for word in w for v in word]
    k0, k1, k2, k3, k4, k5 = words
    w = [k4, k5, _rotr(k0, 12), _rotr(k1, 2), k2, k3]
    Kn = [v for word in w for v in word]
    for pos in (92, 68, 44, 20):
        Kn[pos:pos + 4] = _key_sbox(m, Kn[pos:pos + 4])
    for b in range(5):
        Kn[48 + b] = _const_xor(m, Kn[48 + b], (rc >> b) & 1)
    return Kn


def build_ks(active, rounds, keysize=128, mode="add"):
    m = Model()
    x = m.vars(64)
    m.inputs = list(x)
    for i in range(64):
        m.add([x[i]] if i in active else [-x[i]])
    K = m.vars(keysize)
    m.master = list(K)
    m.masks += list(x)
    m.ksvars = list(K)
    m.trace = [("input", list(x))]
    rcs = round_constants(rounds)
    for r in range(rounds):
        rk, Kc = m.vars(64), m.vars(64)          # COPY of the low half: round key and next state
        for i in range(64):
            m.or_of(K[i], [rk[i], Kc[i]])
        m.ksvars += rk + Kc
        K = Kc + K[64:]
        y = m.vars(64)                           # state XOR round key
        for i in range(64):
            m.or_of(y[i], [x[i], rk[i]]); m.at_most_one([x[i], rk[i]])
        m.trace.append(("key", list(y)))
        x = sbox_layer(m, y, SBOX_MP); m.trace.append(("sbox", list(x)))
        x = mix_layer(m, x, "mp", mode); m.trace.append(("mix", list(x)))
        x = perm_layer(x); m.trace.append(("perm", list(x)))
        if r < rounds - 1:
            before = len(m.pool.obj2id)
            K = key_update(m, K, keysize, rcs[r])
            m.ksvars += list(K)
    for v in K:                                  # unused key state after the last round key
        m.const0(v)
    m.masks += list(x)
    m.masks = sorted(set(m.masks))
    return m, x


class TrailCounterKS:
    def __init__(self, active, rounds, keysize=128, mode="add", solver="cadical153"):
        self.m, self.out = build_ks(set(active), rounds, keysize, mode)
        self.rounds, self.keysize = rounds, keysize
        self.proj = sorted(set(self.m.masks) | set(self.m.ksvars))
        self.s = Solver(name=solver, bootstrap_with=self.m.cl)
        self._sel = 0

    def _assumptions(self, w, j):
        a = [self.out[i] if i == j else -self.out[i] for i in range(64)]
        a += [v if (w >> i) & 1 else -v for i, v in enumerate(self.m.master)]
        return a

    def exists(self, w, j):
        return self.s.solve(assumptions=self._assumptions(w, j))

    def count(self, w, j, cap=100000):
        assum = self._assumptions(w, j)
        self._sel += 1
        sel = self.m.pool.id(("sel", self._sel))
        n = 0
        while n < cap and self.s.solve(assumptions=assum + [sel]):
            val = {abs(l): l > 0 for l in self.s.get_model()}
            n += 1
            self.s.add_clause([-sel] + [-v if val[v] else v for v in self.proj])
        capped = n >= cap and self.s.solve(assumptions=assum + [sel])
        self.s.add_clause([-sel])
        return None if capped else n

    def greedy(self, j, rng, direction="max"):
        base = [self.out[i] if i == j else -self.out[i] for i in range(64)]
        if not self.s.solve(assumptions=base):
            return None
        model = set(l for l in self.s.get_model() if l > 0)
        fixed = []
        order = list(range(self.keysize)); rng.shuffle(order)
        sign = 1 if direction == "max" else -1
        for i in order:
            lit = sign * self.m.master[i]
            if (lit > 0 and lit in model) or (lit < 0 and -lit not in model):
                fixed.append(lit); continue
            if self.s.solve(assumptions=base + fixed + [lit]):
                fixed.append(lit); model = set(l for l in self.s.get_model() if l > 0)
        return sum(1 << i for i, v in enumerate(self.m.master) if v in model)
