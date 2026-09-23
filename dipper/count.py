"""Exact counting of monomial trails under a fixed key pattern.

For an input mask u, a key pattern v = (v_1,...,v_r) and an output bit j, the
coefficient of x^u k^v in S^(r)_j equals the number of monomial trails with that
key pattern, modulo 2 (Hu et al., ASIACRYPT 2020). An ODD count proves the
monomial is present, hence that the cube sum is not identically zero.

The key pattern is pinned with indicator variables kv[t][i] <-> (y_i & ~x_i) on
each key layer: since the layer enforces x <= y, fixing kv fixes which positions
take the key variable and which pass the state mask through.

Counting is AllSAT with blocking clauses over a projection set. With
projection="masks" the blocking ranges over the layer masks only; every other
variable is a function of those and of the pattern, so the enumeration is
bijective on trails. projection="all" blocks over every variable and is used to
test that claim (scripts/step16_projection_check.py).
"""
from pysat.solvers import Solver
from .models import build


class TrailCounter:
    """active=None leaves the input mask free (variables self.m.inputs), to be fixed by assumptions."""
    def __init__(self, active, rounds, mode="add", solver="cadical153", projection="masks"):
        self.m, self.out = build(None if active is None else set(active), rounds, "mp", mode)
        self.rounds = rounds
        self.kv = []
        extra = []
        for t, (x, y) in enumerate(self.m.keylayers):
            row = []
            for i in range(64):
                v = self.m.pool.id(("kv", t, i))
                extra += [[-v, y[i]], [-v, -x[i]], [v, -y[i], x[i]]]
                row.append(v)
            self.kv.append(row)
        self.proj = sorted(set(self.m.masks)) if projection == "masks" else \
            sorted({abs(l) for c in self.m.cl + extra for l in c})
        self.s = Solver(name=solver, bootstrap_with=self.m.cl + extra)
        self._sel = 0

    # ---- queries -------------------------------------------------------
    def _assumptions(self, pattern, j):
        a = [self.out[i] if i == j else -self.out[i] for i in range(64)]
        for t, mask in enumerate(pattern):
            a += [self.kv[t][i] if (mask >> i) & 1 else -self.kv[t][i] for i in range(64)]
        return a

    def exists(self, pattern, j):
        return self.s.solve(assumptions=self._assumptions(pattern, j))

    def count(self, pattern, j, cap=100000, return_trails=0):
        """Exact number of trails, or (cap, 'capped'). Optionally return the
        first `return_trails` trails as lists of layer masks."""
        assum = self._assumptions(pattern, j)
        self._sel += 1
        sel = self.m.pool.id(("sel", self._sel))
        n, trails = 0, []
        while n < cap and self.s.solve(assumptions=assum + [sel]):
            val = {abs(l): l > 0 for l in self.s.get_model()}
            if len(trails) < return_trails:
                trails.append([sum(1 << i for i, v in enumerate(vs) if val[v])
                               for _, vs in self.m.trace])
            n += 1
            self.s.add_clause([-sel] + [-v if val[v] else v for v in self.proj])
        capped = n >= cap and self.s.solve(assumptions=assum + [sel])
        self.s.add_clause([-sel])                      # retire the blocking clauses
        return (None if capped else n), trails

    def close(self):
        self.s.delete()


def read_pattern(counter, pattern, j):
    """Sanity: after fixing a pattern, read it back from a model."""
    if not counter.exists(pattern, j):
        return None
    val = {abs(l): l > 0 for l in counter.s.get_model()}
    return [sum(1 << i for i, v in enumerate(row) if val[v]) for row in counter.kv]


def greedy_key_pattern(counter, j, rng, forced_zero=(), direction="max"):
    """A key pattern admitting at least one trail to bit j.

    direction="max": greedily take as many key positions as possible, in a random
    order, keeping a choice whenever the instance stays satisfiable. Each key bit
    taken forces the state mask to 0 there and so removes trails, which is what
    makes an odd count reachable. This is the setting used for presence proofs.
    direction="min": the opposite, giving low-weight patterns; used by the ANF
    validation, where the cost of the Moebius sum grows with the pattern weight.

    Rounds listed in `forced_zero` are pinned to the all-zero pattern first
    (valid for cubes of dimension 63, where the only other input monomial is the
    all-ones one, whose coefficient vanishes for a permutation)."""
    base = [counter.out[i] if i == j else -counter.out[i] for i in range(64)]
    fixed = []
    for t in forced_zero:
        fixed += [-v for v in counter.kv[t]]
    if not counter.s.solve(assumptions=base + fixed):
        return None
    order = [(t, i) for t in range(counter.rounds) if t not in forced_zero for i in range(64)]
    rng.shuffle(order)
    sign = 1 if direction == "max" else -1
    for t, i in order:
        trial = fixed + [sign * counter.kv[t][i]]
        if counter.s.solve(assumptions=base + trial):
            fixed = trial
    assert counter.s.solve(assumptions=base + fixed)          # re-solve: last try may have failed
    val = {abs(l): l > 0 for l in counter.s.get_model()}
    return [sum(1 << i for i, v in enumerate(row) if val[v]) for row in counter.kv]


def find_odd_pattern(counter, j, rng, tries=100, cap=100000, forced_zero=(), direction="max"):
    """Search for a key pattern whose trail count is odd (a presence proof)."""
    seen, capped = set(), 0
    for t in range(tries):
        pat = greedy_key_pattern(counter, j, rng, forced_zero, direction)
        if pat is None:
            return {"status": "no trail"}
        key = tuple(pat)
        if key in seen:
            continue
        seen.add(key)
        n, trails = counter.count(pat, j, cap=cap, return_trails=1)
        if n is None:
            capped += 1
            continue
        if n % 2 == 1:
            return {"status": "odd", "pattern": pat, "count": n, "examined": len(seen),
                    "trail": trails[0] if trails else None, "capped": capped}
    return {"status": "even/capped", "examined": len(seen), "capped": capped}


def greedy_key_pattern_fast(counter, j, rng, forced_zero=(), direction="max"):
    """Same result as greedy_key_pattern (same visiting order, same decisions),
    with fewer SAT calls: a position that the current model already assigns the
    desired value is accepted without a new solve, because that model witnesses
    satisfiability of the extended assumption set."""
    base = [counter.out[i] if i == j else -counter.out[i] for i in range(64)]
    fixed = []
    for t in forced_zero:
        fixed += [-v for v in counter.kv[t]]
    if not counter.s.solve(assumptions=base + fixed):
        return None
    model = set(l for l in counter.s.get_model() if l > 0)
    order = [(t, i) for t in range(counter.rounds) if t not in forced_zero for i in range(64)]
    rng.shuffle(order)
    sign = 1 if direction == "max" else -1
    for t, i in order:
        lit = sign * counter.kv[t][i]
        if (lit > 0 and lit in model) or (lit < 0 and -lit not in model):
            fixed = fixed + [lit]
            continue
        trial = fixed + [lit]
        if counter.s.solve(assumptions=base + trial):
            fixed = trial
            model = set(l for l in counter.s.get_model() if l > 0)
    val = model
    return [sum(1 << i for i, v in enumerate(row) if v in val) for row in counter.kv]
