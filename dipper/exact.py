"""Cancellation-aware check (exact MP model only).

The cube sum of output bit j is g(k) = sum_v c_v k^v, where k collects the
(constant XOR first round key) and all later round-key bits as independent
variables, and c_v = parity of the number of monomial trails whose key
monomial is v. For the 'mp' model every trail is uniquely determined by its
layer masks (auxiliary variables are functionally determined), so enumerating
solutions projected on the masks enumerates trails. If every c_v is even,
g == 0 identically: the bit is balanced although trails exist."""
from collections import Counter
from pysat.solvers import Solver
from .models import build


def trail_parities(active, rounds, j, mode="add", cap=2_000_000, solver="cadical153"):
    m, out = build(set(active), rounds, "mp", mode)
    s = Solver(name=solver, bootstrap_with=m.cl)
    assum = [out[i] if i == j else -out[i] for i in range(64)]
    proj = m.masks
    parity = Counter()
    n = 0
    while s.solve(assumptions=assum):
        model = s.get_model()
        val = {abs(l): l > 0 for l in model}
        key = tuple(tuple(i for i in range(64) if val[y[i]] and not val[x[i]])
                    for x, y in m.keylayers)
        parity[key] ^= 1
        n += 1
        if n >= cap:
            s.delete()
            return {"status": "cap", "trails": n}
        s.add_clause([-v if val[v] else v for v in proj])
    s.delete()
    odd = [k for k, p in parity.items() if p]
    return {"status": "done", "trails": n, "key_monomials": len(parity),
            "odd_key_monomials": len(odd), "balanced_exactly": len(odd) == 0}
