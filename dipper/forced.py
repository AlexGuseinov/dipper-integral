"""Forced positions of the state mask entering the second key addition.

For the 63-dimensional cube with cleared bit i', consider all monomial trails
through round 1 (the round-1 key pattern is pinned to zero, which is exact for
dimension 63: the only other input monomial is the all-ones one, whose
coefficient vanishes for a permutation). Position q is FORCED if every reachable
mask after round 1 has a 1 at q. A round-2 key monomial whose support meets the
forced set annihilates every trail from that input pattern, because the key-XOR
rule needs the state mask and the key pattern to be disjoint.

This is the ingredient the block-diagonalisation of the SPN integral-resistance
methods relies on; `separable` and `finest_partition` test whether it yields a
block structure for Dipper."""
from itertools import combinations
from pysat.solvers import Solver
from .models import build

WORD = "DCBA"


def forced_set(iprime, mode="add", rounds=1):
    """64-bit mask of positions forced to 1 after `rounds` rounds."""
    m, out = build(set(range(64)) - {iprime}, rounds, "mp", mode)
    s = Solver(name="cadical153", bootstrap_with=m.cl)
    forced = 0
    for q in range(64):
        if not s.solve(assumptions=[-out[q]]):          # no trail leaves q at 0
            forced |= 1 << q
    s.delete()
    return forced


def separable(classes, F, positions=range(64)):
    """A support S of a key monomial with S disjoint from F(n) for every nibble
    n in `classes` and meeting F(m) for every nibble m outside. Returns the
    support (as a list of positions) or None."""
    inside = set(classes)
    allowed = [p for p in positions if all(not (F[n] >> p) & 1 for n in inside)]
    support = []
    for m in range(16):
        if m in inside:
            continue
        hit = [p for p in allowed if (F[m] >> p) & 1]
        if not hit:
            return None
        if not any((F[m] >> p) & 1 for p in support):
            support.append(hit[0])
    return sorted(set(support))


def finest_partition(F):
    """All singleton nibble classes that are separable, and whether the full
    nibble partition works."""
    single = {n: separable([n], F) for n in range(16)}
    return {n: s for n, s in single.items() if s is not None}
