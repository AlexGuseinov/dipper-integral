"""SAT models of monomial / division-trail propagation through reduced-round Dipper.

Three propagation models (all sound: infeasibility => the cube sum is zero):
  'mp'   exact local monomial transitions: GIFT S-box coefficient table and the
         exact rule for (x, y) -> (x + y, y) derived from Hu-Yap (ToSC 2024)
  'mpc'  monomial prediction through a gate-level carry circuit (COPY/XOR/AND)
  'bdp'  conventional two-subset bit-based division property: S-box division
         trail table and the same gate-level carry circuit with BDP gate rules
Mode of the ARX layer: 'add' (Dipper), 'xor' (additions replaced by XOR),
'none' (additions removed; rotations kept).

Direction: masks run from the plaintext side (input monomial x^u) to the
output bit (unit vector). A trail with key XOR satisfies u_i <= w_i (MP);
under BDP the key XOR is transparent."""
from itertools import product
from pysat.formula import IDPool
from pysat.solvers import Solver
from .anf import SBOX_MP, SBOX_BDP, monomial_table
from .cipher import PERM, ROT

XOR1_MP = monomial_table(lambda xy: ((xy & 1) ^ (xy >> 1)) | (xy & 2), 2, 2)  # (x,y)->(x^y,y)


class Model:
    def __init__(self):
        self.pool = IDPool()
        self.cl = []
        self.keylayers = []          # list of (x_vars, y_vars) of key-XOR layers
        self.masks = []              # all mask (non-auxiliary) variables

    def var(self):
        return self.pool.id(("v", len(self.pool.obj2id)))

    def vars(self, n):
        return [self.var() for _ in range(n)]

    def add(self, c):
        self.cl.append(c)

    def const0(self, v):
        self.add([-v])

    # --- generic relation from a truth table (forbid invalid assignments) ---
    def table(self, vs, valid):
        """vs: list of variables; valid(bits_tuple) -> bool."""
        for bits in product((0, 1), repeat=len(vs)):
            if not valid(bits):
                self.add([-v if b else v for v, b in zip(vs, bits)])

    def eq(self, a, b):
        self.add([-a, b]); self.add([a, -b])

    def leq(self, a, b):                     # a <= b
        self.add([-a, b])

    def or_of(self, out, ins):               # out = OR(ins)
        for i in ins:
            self.add([-i, out])
        self.add([-out] + list(ins))

    def at_most_one(self, ins):
        for i in range(len(ins)):
            for j in range(i + 1, len(ins)):
                self.add([-ins[i], -ins[j]])

    # --- gate rules ---
    def copy(self, x, outs, rule):
        if rule == "mp":                     # x^u appears in prod x^{v_j}: u = OR v_j
            self.or_of(x, outs)
        else:                                # BDP: u = sum v_j
            self.or_of(x, outs); self.at_most_one(outs)

    def xor(self, ins, out):                 # identical for MP and BDP
        self.or_of(out, ins); self.at_most_one(ins)

    def and_(self, a, b, out, rule):
        if rule == "mp":
            self.eq(a, out); self.eq(b, out)
        else:
            self.or_of(out, [a, b])


def sbox_layer(m, x, table):
    y = m.vars(64)
    m.masks += list(x) + list(y)
    for j in range(16):
        xin = x[4 * j:4 * j + 4]
        yout = y[4 * j:4 * j + 4]
        def ok(bits):
            u = sum(b << i for i, b in enumerate(bits[:4]))
            v = sum(b << i for i, b in enumerate(bits[4:]))
            return table[u][v] == 1
        m.table(xin + yout, ok)
    return y


def rotl_vars(w, r):                         # w[i] = bit i; left rotate by r
    return [w[(i - r) % 16] for i in range(16)]


def add_exact(m, a, b):
    """(x, y) -> (x + y, y) exact MP: exists b' with a + b' = w, b = b' | c."""
    w, c, bp, q = m.vars(16), m.vars(16), m.vars(16), m.vars(17)
    m.const0(q[0]); m.const0(q[16])
    for i in range(16):
        m.table([a[i], bp[i], q[i], w[i], q[i + 1]],
                lambda t: t[0] + t[1] + t[2] == t[3] + 2 * t[4])
        m.or_of(b[i], [bp[i], c[i]])
    return w, c


def add_circuit(m, a, b, rule):
    """Ripple-carry circuit for (x, y) -> (x + y, y) with gate-level rules."""
    w, c = m.vars(16), m.vars(16)
    carry = None
    for i in range(16):
        last = i == 15
        nx = 1 if (last or i == 0 and False) else 2
        xs = m.vars(1 if last else 2)
        ys = m.vars(2 if last else 3)
        m.copy(a[i], xs, rule)
        m.copy(b[i], ys, rule)
        m.eq(ys[-1], c[i])                   # retained operand bit
        t = m.var()
        m.xor([xs[0], ys[0]], t)
        if carry is None:
            ts = [t] if last else m.vars(2)
            if not last:
                m.copy(t, ts, rule)
            m.eq(ts[0], w[i])
            if not last:
                g = m.var(); m.and_(xs[1], ys[1], g, rule)
                # no incoming carry: c_1 = g_0 ; t copy for carry unused
                m.const0(ts[1])
                carry = g
        else:
            if last:
                m.xor([t, carry], w[i])
            else:
                ts, cs = m.vars(2), m.vars(2)
                m.copy(t, ts, rule); m.copy(carry, cs, rule)
                m.xor([ts[0], cs[0]], w[i])
                g, h = m.var(), m.var()
                m.and_(xs[1], ys[1], g, rule)
                m.and_(ts[1], cs[1], h, rule)
                nc = m.var(); m.xor([g, h], nc)
                carry = nc
    return w, c


def xor_exact(m, a, b, rule):
    w, c = m.vars(16), m.vars(16)
    for i in range(16):
        if rule == "bdp":                    # COPY y -> (y1, y2); x ^ y1
            y1, y2 = m.vars(2)
            m.copy(b[i], [y1, y2], "bdp"); m.xor([a[i], y1], w[i]); m.eq(y2, c[i])
        else:
            def ok(bits):
                u = bits[0] | bits[1] << 1; v = bits[2] | bits[3] << 1
                return XOR1_MP[u][v] == 1
            m.table([a[i], b[i], w[i], c[i]], ok)
    return w, c


def mix_layer(m, x, model, mode):
    A, B, C, D = x[48:64], x[32:48], x[16:32], x[0:16]
    A, B, C, D = (rotl_vars(A, ROT[0]), rotl_vars(B, ROT[1]),
                  rotl_vars(C, ROT[2]), rotl_vars(D, ROT[3]))
    for (hi, lo) in ((0, 1), (2, 3)):
        pass
    if mode == "add":
        f = add_exact if model == "mp" else (lambda m_, a_, b_: add_circuit(m_, a_, b_, "mp" if model == "mpc" else "bdp"))
        A, B = f(m, A, B); C, D = f(m, C, D)
    elif mode == "xor":
        rule = "bdp" if model == "bdp" else "mp"
        A, B = xor_exact(m, A, B, rule); C, D = xor_exact(m, C, D, rule)
    return D + C + B + A


def perm_layer(x):
    y = [None] * 64
    for i in range(64):
        y[PERM[i]] = x[i]
    return y


def key_layer(m, x, model):
    if model == "bdp":
        return x
    y = m.vars(64)
    for i in range(64):
        m.leq(x[i], y[i])
    m.keylayers.append((list(x), list(y)))
    return y


def build(active, rounds, model="mp", mode="add"):
    """Returns (Model, output_vars). Input mask = indicator of `active`;
    active=None leaves the input mask free (m.inputs holds its variables)."""
    m = Model()
    x = m.vars(64)
    m.inputs = list(x)
    if active is not None:
        for i in range(64):
            m.add([x[i]] if i in active else [-x[i]])
    table = SBOX_BDP if model == "bdp" else SBOX_MP
    m.masks += list(x)
    for _ in range(rounds):
        x = key_layer(m, x, model)
        x = sbox_layer(m, x, table)
        x = mix_layer(m, x, model, mode)
        x = perm_layer(x)
    m.masks += list(x)
    m.masks = sorted(set(m.masks))
    return m, x


class Checker:
    """Incremental solver: which output bits of S^(r) are certified balanced."""
    def __init__(self, active, rounds, model="mp", mode="add", solver="cadical153"):
        self.m, self.out = build(set(active), rounds, model, mode)
        self.s = Solver(name=solver, bootstrap_with=self.m.cl)

    def trail_exists(self, j, conflict_budget=None):
        assum = [self.out[i] if i == j else -self.out[i] for i in range(64)]
        if conflict_budget:
            self.s.conf_budget(conflict_budget)
            r = self.s.solve_limited(assumptions=assum)
        else:
            r = self.s.solve(assumptions=assum)
        return r                              # True / False / None (budget)

    def balanced_bits(self, conflict_budget=None):
        res = {}
        for j in range(64):
            r = self.trail_exists(j, conflict_budget)
            res[j] = "balanced" if r is False else ("unknown" if r is True else "timeout")
        return res

    def close(self):
        self.s.delete()
