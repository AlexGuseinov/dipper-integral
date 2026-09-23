"""No nonzero linear combination of output bits is balanced after seven rounds
over any bit-aligned cube (independent round keys).

For the cube I_p choose for every output bit l a key pattern v_l with an odd
number of trails to bit l. M[l][j] = parity of the number of trails to bit j with
pattern v_l. For beta != 0 the coefficient of x^{1_I} k^{v_l} in <beta, S^(7)> is
(M beta)_l; M invertible => <beta, S^(7)> not balanced over I_p, and by
monotonicity over no sub-cube either.
Structure used: G has an edge l -> j (j != l) iff v_l has a trail to j. M is
block-triangular along the strongly connected components (SCCs) of G, so M is
invertible iff every SCC block is. Patterns of bits on cycles are replaced by
other presence proofs until every SCC is a single node (then M is triangular with
unit diagonal) or its block is counted exactly and found invertible.
Candidates for bit l: random maximal patterns and "partial seeds" (rounds 3..7
of patterns that proved bit l at other constant-bit positions).
Checks: every trail of every odd diagonal entry and of every counted block entry
is validated by the CNF-independent checker; zero entries are "no trail" answers
(UNSAT) of the solver.
Usage: step27_linear_combinations.py <p-list> <outfile>
"""
import glob, json, os, random, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter, greedy_key_pattern_fast
from dipper.witness import check_trail

ps = [int(x) for x in sys.argv[1].split(",")]
OUT = sys.argv[2]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
SAMPLES = int(os.environ.get("SAMPLES", "120"))   # candidates per cyclic bit and sweep
BCAP = 5000              # cap for exact block entries

pats = {0: {int(j): [int(m, 16) for m in v["pattern"]] for j, v in
            json.load(open("results/step20_presence_r7_complete.json"))["per_bit"].items()}}
for f in glob.glob("results/step21_presence_*_p.json"):
    for p, rec in json.load(open(f)).items():
        if rec.get("done"):
            pats[int(p)] = {int(j): [int(m, 16) for m in b["pattern"]] for j, b in rec["bits"].items()}



from dipper.cipher import PERM_INV, ROT
WORD_BASE = {3: 48, 2: 32, 1: 16, 0: 0}                 # word index (A=3,B=2,C=1,D=0) -> first state bit
ROT_OF = {3: ROT[0], 2: ROT[1], 1: ROT[2], 0: ROT[3]}


def last_round_nibbles(j):
    """S-box indices of the last round that output bit j of S^(7) depends on linearly
    (retained word: one S-box; added word bit 0: the two S-boxes of its operands)."""
    pos = PERM_INV[j]; w, i = pos // 16, pos % 16
    src = lambda word, bit: (WORD_BASE[word] + ((bit - ROT_OF[word]) % 16)) // 4
    if w in (2, 0):
        return [src(w, i)]
    return [src(w, i), src(w - 1, i)]        # linear part of (X + Y)_i is X_i xor Y_i


def retained_sbox_bit(j):
    """(nibble, S-box output bit) if output bit j of S^(7) is a rotated S-box output bit of the
    last round (retained word), else None."""
    pos = PERM_INV[j]; w, i = pos // 16, pos % 16
    if w not in (2, 0):
        return None
    q = WORD_BASE[w] + ((i - ROT_OF[w]) % 16)
    return q // 4, q % 4


def component_anf(bits):
    from dipper.cipher import SBOX
    tt = [0] * 16
    for x in range(16):
        tt[x] = sum((SBOX[x] >> b) & 1 for b in bits) & 1
    co = list(tt)
    for i in range(4):
        for x in range(16):
            if x >> i & 1:
                co[x] ^= co[x ^ (1 << i)]
    return {u for u in range(16) if co[u]}


def check_trail_mask(trail, act, n_, u):
    """validate a six-round trail that ends in the state mask u on nibble n_ (possibly several bits)"""
    return check_trail(trail, act, 0, "add", final_mask=u << (4 * n_))[0]


def all_last_round_nibbles(j):
    pos = PERM_INV[j]; w, i = pos // 16, pos % 16
    src = lambda word, bit: (WORD_BASE[word] + ((bit - ROT_OF[word]) % 16)) // 4
    if w in (2, 0):
        return [src(w, i)]
    return sorted({src(w, b) for b in range(i + 1)} | {src(w - 1, b) for b in range(i + 1)})


def greedy_extra(c, j, rng, extra):
    base = [c.out[i] if i == j else -c.out[i] for i in range(64)] + extra
    fixed = [-v for v in c.kv[0]]
    if not c.s.solve(assumptions=base + fixed):
        return None
    model = set(x for x in c.s.get_model() if x > 0)
    order = [(t, i) for t in range(1, c.rounds) for i in range(64)]
    rng.shuffle(order)
    for t, i in order:
        lit = c.kv[t][i]
        if lit in model:
            fixed.append(lit); continue
        if c.s.solve(assumptions=base + fixed + [lit]):
            fixed.append(lit); model = set(x for x in c.s.get_model() if x > 0)
    return [sum(1 << i for i, x in enumerate(row) if x in model) for row in c.kv]


def kernel_gf2(rows, cols):
    """basis of {beta subset of cols : sum over rows of <row, beta> ... } = right kernel of the block."""
    n = len(cols); idx = {c_: k for k, c_ in enumerate(cols)}
    A = [[(r >> c_) & 1 for c_ in cols] for r in rows]
    piv_cols, rix = [], 0
    for col in range(n):
        pr = next((i for i in range(rix, len(A)) if A[i][col]), None)
        if pr is None:
            continue
        A[rix], A[pr] = A[pr], A[rix]
        for i in range(len(A)):
            if i != rix and A[i][col]:
                A[i] = [a ^ b for a, b in zip(A[i], A[rix])]
        piv_cols.append(col); rix += 1
    free = [c_ for c_ in range(n) if c_ not in piv_cols]
    basis = []
    for f in free:
        beta = [0] * n; beta[f] = 1
        for k, pc in enumerate(piv_cols):
            beta[pc] = A[k][f]
        basis.append([cols[k] for k in range(n) if beta[k]])
    return basis

def sccs(G):
    idx, low, st, on, comps, k = {}, {}, [], set(), [], [0]
    sys.setrecursionlimit(10000)

    def sc(v):
        idx[v] = low[v] = k[0]; k[0] += 1; st.append(v); on.add(v)
        for w in G[v]:
            if w not in idx:
                sc(w); low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v:
                    break
            comps.append(sorted(comp))
    for v in G:
        if v not in idx:
            sc(v)
    return comps


def rank_gf2(rows, cols):
    rows = list(rows); rank = 0
    for b in cols:
        piv = next((i for i in range(rank, len(rows)) if (rows[i] >> b) & 1), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(len(rows)):
            if i != rank and (rows[i] >> b) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


for p in ps:
    if str(p) in res and res[str(p)].get("invertible"):
        continue
    t0 = time.time()
    act = sorted(set(range(64)) - {p})
    c = TrailCounter(act, 7)
    rng = random.Random(5150 + p)
    P = dict(pats[p])
    reach = lambda v, l, among=range(64): [j for j in among if j != l and c.exists(v, j)]
    G = {l: reach(P[l], l) for l in range(64)}
    cyc0 = sum(len(s_) for s_ in sccs(G) if len(s_) > 1)
    base_fixed0 = lambda l: [c.out[i] if i == l else -c.out[i] for i in range(64)]

    def candidates(l):
        """random maximal patterns and partial seeds for bit l, odd count only"""
        pool = [pats[q][l] for q in pats if q != p]
        rng.shuffle(pool)
        for n in range(SAMPLES):
            if n % 2 == 0 or not pool:
                v = greedy_key_pattern_fast(c, l, rng, forced_zero=(0,))
            else:
                seed = pool.pop()
                base = base_fixed0(l)
                fixed = [-x for x in c.kv[0]]
                for t in range(2, 7):
                    fixed += [c.kv[t][i] if (seed[t] >> i) & 1 else -c.kv[t][i] for i in range(64)]
                if not c.s.solve(assumptions=base + fixed):
                    continue
                model = set(x for x in c.s.get_model() if x > 0)
                free = list(range(64)); rng.shuffle(free)
                for i in free:
                    lit = c.kv[1][i]
                    if lit in model:
                        fixed.append(lit); continue
                    if c.s.solve(assumptions=base + fixed + [lit]):
                        fixed.append(lit); model = set(x for x in c.s.get_model() if x > 0)
                v = [sum(1 << i for i, x in enumerate(row) if x in model) for row in c.kv]
            if v is None:
                continue
            k_, _ = c.count(v, l, cap=40)
            if k_ is not None and k_ % 2 == 1:
                yield v

    cache6 = {}

    def pres6(bit):
        if bit in cache6:
            return cache6[bit]
        if "_counter" not in cache6:
            cache6["_counter"] = TrailCounter(act, 6)
        c6_ = cache6["_counter"]
        found6 = None
        r6 = random.Random(77 + bit + 64 * p)
        for cap6, tries6 in ((40, 900), (400, 300), (3000, 100)):
            for k6 in range(tries6):
                v6 = greedy_key_pattern_fast(c6_, bit, r6, forced_zero=(0,) if k6 % 2 == 0 else ())
                if v6 is None:
                    break
                n6, _ = c6_.count(v6, bit, cap=cap6)
                if n6 is not None and n6 % 2:
                    found6 = v6; break
            if found6 is not None:
                break
        cache6[bit] = found6
        return found6

    replaced = 0
    fixed_rows = set()
    lemma_rows = {}                                   # frozenset(block) -> info

    def break_cycles(max_sweeps=4):
        global G, replaced
        for _ in range(max_sweeps):
            comps = [s_ for s_ in sccs(G) if len(s_) > 1 and frozenset(s_) not in lemma_rows]
            if not comps:
                return
            progress = False
            for comp in comps:
                for l in sorted(comp, key=lambda x: -len(G[x])):
                    if l in fixed_rows:
                        continue
                    cur = [s_ for s_ in sccs(G) if l in s_][0]
                    if len(cur) == 1 or frozenset(cur) in lemma_rows:
                        continue
                    for v in candidates(l):
                        if not reach(v, l, cur):
                            G2 = dict(G); G2[l] = reach(v, l)
                            if sum(len(s_) for s_ in sccs(G2) if len(s_) > 1) < sum(len(s_) for s_ in sccs(G) if len(s_) > 1):
                                P[l], G = v, G2; replaced += 1; progress = True
                                break
            if not progress:
                return

    break_cycles()
    print(f"p={p} after cycle breaking: blocks {[s_ for s_ in sccs(G) if len(s_) > 1]} ({time.time()-t0:.0f}s)", flush=True)
    # remaining blocks: exact counts; repair singular blocks through their kernel
    def block_rows(comp):
        rows, unknown = [], []
        for l in comp:
            row = 0
            for j in comp:
                if j != l and j not in G[l]:
                    continue
                n, _ = c.count(P[l], j, cap=BCAP)
                if n is None:
                    unknown.append([l, j]); continue
                row |= (n % 2) << j
            rows.append(row)
        return rows, unknown

    def row_of(v, comp):
        row = 0
        for j in comp:
            if not c.exists(v, j):
                continue
            n, _ = c.count(v, j, cap=BCAP)
            if n is None:
                return None
            row |= (n % 2) << j
        return row

    blocks, inv, repairs = [], True, 0
    lemma_blocks = []
    for _it in range(4):
        n_lemma_before, blocks, inv = len(lemma_rows), [], True
        for comp in [s_ for s_ in sccs(G) if len(s_) > 1]:
            if frozenset(comp) in lemma_rows:
                continue
            info = [retained_sbox_bit(j) for j in comp]
            same_nibble = 2 <= len(comp) <= 4 and None not in info and len({x[0] for x in info}) == 1
            rows, unknown, rk = None, None, None
            if same_nibble:
                # Lemma (last-round component), exact entries: for pattern (V, k7_t), the entry of output bit j
                # (S-box output bit b) is sum over monomials z^{u+t} of ANF(b), u != 0, of the parity of the number of
                # six-round trails with pattern V to the state mask u of nibble n. Rows are chosen to be invertible.
                n_ = info[0][0]
                anfs = [component_anf([x[1]]) for x in info]
                c6_ = cache6.get("_counter") or TrailCounter(act, 6)
                cache6["_counter"] = c6_

                def n6_mask(V, u, cap=20000):
                    a_ = [c6_.out[i] if (i >= 4 * n_ and i < 4 * n_ + 4 and (u >> (i - 4 * n_)) & 1) else -c6_.out[i] for i in range(64)]
                    for tt, mk in enumerate(V):
                        a_ += [c6_.kv[tt][i] if (mk >> i) & 1 else -c6_.kv[tt][i] for i in range(64)]
                    if not c6_.s.solve(assumptions=a_):
                        return 0, []
                    c6_._sel += 1
                    sel = c6_.m.pool.id(("sel", c6_._sel)); nn = 0; trs = []
                    while nn < cap and c6_.s.solve(assumptions=a_ + [sel]):
                        val = {abs(l_): l_ > 0 for l_ in c6_.s.get_model()}
                        trs.append([sum(1 << i for i, v_ in enumerate(vs) if val[v_]) for _, vs in c6_.m.trace]); nn += 1
                        c6_.s.add_clause([-sel] + [-v_ if val[v_] else v_ for v_ in c6_.proj])
                    capped = nn >= cap and c6_.s.solve(assumptions=a_ + [sel])
                    c6_.s.add_clause([-sel])
                    return (None if capped else nn), trs

                cand_rows = []
                for a in range(4):
                    V = pres6(4 * n_ + a)
                    if V is None:
                        continue
                    for t in range(4):
                        ent, ok, used = [], True, {}
                        for A in anfs:
                            e = 0
                            for mono in A:
                                if not (mono >> t) & 1 or mono == (1 << t):
                                    continue
                                u = mono ^ (1 << t)
                                if u not in used:
                                    used[u] = n6_mask(V, u)
                                if used[u][0] is None:
                                    ok = False; break
                                e ^= used[u][0] & 1
                            if not ok:
                                break
                            ent.append(e)
                        if ok and any(ent):
                            cand_rows.append((t, a, V, tuple(ent), used))
                # choose len(comp) rows with full rank
                chosen, basis = [], []
                for cr in cand_rows:
                    vec = sum(e << i for i, e in enumerate(cr[3]))
                    if rank_gf2(basis + [vec], list(range(len(comp)))) > len(basis):
                        basis.append(vec); chosen.append(cr)
                    if len(chosen) == len(comp):
                        break
                if len(chosen) == len(comp):
                    ntr6 = bad6 = 0
                    for (t, a, V, ent, used) in chosen:            # validate every six-round trail used
                        for u, (cnt, trs) in used.items():
                            for tr in trs:
                                ntr6 += 1
                                masks_ok = check_trail_mask(tr, act, n_, u)
                                bad6 += (not masks_ok)
                    import itertools
                    labels = None                           # assign rows to labels with an all-ones diagonal
                    for perm in itertools.permutations(range(len(comp))):
                        if all(chosen[perm[i]][3][i] for i in range(len(comp))):
                            labels = [None] * len(comp)
                            for i in range(len(comp)):
                                labels[perm[i]] = comp[i]
                            break
                    assert labels is not None, "invertible block must admit an all-ones diagonal"
                    rows_info = []
                    for (t, a, V, ent, used), l in zip(chosen, labels):
                        v = list(V) + [1 << (4 * n_ + t)]
                        P[l], G[l] = v, reach(v, l); fixed_rows.add(l)
                        rows_info.append({"label": l, "t": t, "a": a, "entries": list(ent), "V": [f"{m:016X}" for m in V]})
                    repairs += len(comp)
                    done = {"nodes": comp, "rank": len(comp), "unknown": [], "by_lemma": {"nibble": n_, "rows": rows_info,
                            "six_round_trails": ntr6, "six_round_trails_failed": bad6}}
                    lemma_rows[frozenset(comp)] = done
                    print(f"   block {comp}: all rows by the last-round component lemma (nibble {n_}, rows {[(r_['t'], r_['a'], r_['entries']) for r_ in rows_info]}, 6-round trails {ntr6}, failed {bad6})", flush=True)
                    continue
            rows, unknown = block_rows(comp)
            rk = None if unknown else rank_gf2(rows, comp)
            attempts = 0
            while (unknown or rk != len(comp)) and attempts < 3:
                attempts += 1
                if unknown:                                   # replace exactly the rows with uncountable entries
                    for l in sorted({l_ for l_, _ in unknown}):
                        if l in fixed_rows:
                            continue
                        for v in candidates(l):
                            R = reach(v, l)
                            if any(c.count(v, j, cap=BCAP)[0] is None for j in comp if j != l and j in R):
                                continue
                            G2 = dict(G); G2[l] = R
                            if all(set(x) <= set(comp) or len(x) == 1 for x in sccs(G2) if set(x) & set(comp)):
                                P[l], G[l] = v, R; repairs += 1
                                print(f"   block {comp}: row {l} replaced by a countable presence proof", flush=True)
                                break
                    rows, unknown = block_rows(comp)
                    rk = None if unknown else rank_gf2(rows, comp)
                    if unknown or rk == len(comp):
                        continue
                targets = kernel_gf2(rows, comp) if not unknown else [[l] for l, _ in unknown]
                for beta in targets:
                    nibs = sorted({n_ for j in beta for n_ in last_round_nibbles(j)})
                    found = None
                    for n_ in sorted({n2 for j in beta for n2 in all_last_round_nibbles(j)}, key=lambda z: z not in nibs):
                        for a in range(4):
                            V = pres6(4 * n_ + a)
                            if V is None:
                                continue
                            for t in range(4):
                                if t == a:
                                    continue
                                v = list(V) + [1 << (4 * n_ + t)]
                                r_ = row_of(v, comp)
                                if r_ is None or sum((r_ >> j) & 1 for j in beta) % 2 == 0:
                                    continue
                                for li, l in enumerate(comp):
                                    trial = rows[:li] + [r_] + rows[li + 1:]
                                    if (r_ >> l) & 1 and rank_gf2(trial, comp) > (rk or 0):
                                        G2 = dict(G); G2[l] = reach(v, l)
                                        if all(set(x) <= set(comp) or len(x) == 1 for x in sccs(G2) if set(x) & set(comp)):
                                            found = (li, l, v, G2[l]); break
                                if found:
                                    break
                            if found:
                                break
                        if found:
                            break
                    if found:
                        li, l, v, R = found
                        P[l], G[l] = v, R; repairs += 1
                        print(f"   block {comp} beta {beta}: repaired by free last round (nibble {n_}, a={a}, t={t})", flush=True)
                        rows, unknown = block_rows(comp)
                        rk = None if unknown else rank_gf2(rows, comp)
                        if not unknown and rk == len(comp):
                            break
                        continue
                    y7 = c.m.keylayers[6][1]
                    found = None
                    for k in range(SAMPLES):
                        extra = []
                        if nibs and k % 2 == 0:
                            for n_ in nibs:                       # low-weight last-round S-box input
                                w = rng.choice([1, 2, 4, 8, 3, 5, 6, 9, 10, 12])
                                extra += [y7[4 * n_ + b] if (w >> b) & 1 else -y7[4 * n_ + b] for b in range(4)]
                        v = greedy_extra(c, rng.choice(beta), rng, extra)
                        if v is None:
                            continue
                        r_ = row_of(v, comp)
                        if r_ is None or not any((r_ >> j) & 1 for j in beta) or bin(sum(((r_ >> j) & 1) << j for j in beta)).count("1") % 2 == 0:
                            continue
                        for li, l in enumerate(comp):            # replace a row so that the rank grows
                            trial = rows[:li] + [r_] + rows[li + 1:]
                            if (r_ >> l) & 1 and rank_gf2(trial, comp) > (rk or 0):
                                G2 = dict(G); G2[l] = reach(v, l)
                                if all(set(x) <= set(comp) or len(x) == 1 for x in sccs(G2) if set(x) & set(comp)):
                                    found = (li, l, v, G2[l]); break
                        if found:
                            break
                    print(f"   block {comp} beta {beta}: {'repaired' if found else 'no pattern'} after {k + 1} samples", flush=True)
                    if found:
                        li, l, v, R = found
                        P[l], G[l] = v, R; repairs += 1
                        rows, unknown = block_rows(comp)
                        rk = None if unknown else rank_gf2(rows, comp)
                        if not unknown and rk == len(comp):
                            break
            blocks.append({"nodes": comp, "rank": rk, "unknown": unknown})
            inv &= (rk == len(comp))
        if len(lemma_rows) == n_lemma_before and inv:
            break
        break_cycles(6)
    if lemma_rows:
        break_cycles(6)
    # final evaluation over the current strongly connected components
    blocks, inv = [], True
    for comp in [s_ for s_ in sccs(G) if len(s_) > 1]:
        if frozenset(comp) in lemma_rows:
            blocks.append(lemma_rows[frozenset(comp)]); continue
        if any(set(comp) & set(k) for k in lemma_rows):          # a lemma row inside a larger cycle: count exactly
            pass
        rows_, unknown_ = block_rows(comp)
        rk_ = None if unknown_ else rank_gf2(rows_, comp)
        blocks.append({"nodes": comp, "rank": rk_, "unknown": unknown_}); inv &= (rk_ == len(comp))
    rec = {"invertible": inv, "cyclic_nodes_start": cyc0, "patterns_replaced": replaced, "block_repairs": repairs,
           "blocks": blocks, "lemma_blocks": [b["by_lemma"] | {"nodes": b["nodes"]} for b in lemma_rows.values()]}
    if inv:
        ntr = bad = 0
        in_block = {l for b in blocks for l in b["nodes"]}
        lemma_diag = {}
        for lb in lemma_rows.values():
            for r_ in lb["by_lemma"].get("rows", []):
                if P[r_["label"]] == [int(m, 16) for m in r_["V"]] + [1 << (4 * lb["by_lemma"]["nibble"] + r_["t"])]:
                    lemma_diag[r_["label"]] = r_["entries"][lb["nodes"].index(r_["label"])]
        for l in range(64):                                   # singleton rows: odd diagonal, all trails valid
            if l in in_block:
                continue
            if l in lemma_diag:                               # diagonal known exactly from the lemma
                bad += (lemma_diag[l] != 1)
                continue
            n, _ = c.count(P[l], l, cap=BCAP)
            _, trails = c.count(P[l], l, cap=(n or 0) + 1, return_trails=(n or 0) + 1)
            ntr += len(trails); bad += sum(not check_trail(t, act, l, "add")[0] for t in trails) + (n is None or n % 2 == 0)
        for b in blocks:
            if b.get("by_lemma"):                             # six-round presence proofs: all trails valid
                c6_ = cache6["_counter"]
                for row in b["by_lemma"]["rows"]:
                    V = [int(m, 16) for m in row["V"]]; a6 = 4 * b["by_lemma"]["nibble"] + row["a"]
                    n6, _ = c6_.count(V, a6, cap=40)
                    _, tr6 = c6_.count(V, a6, cap=(n6 or 0) + 1, return_trails=(n6 or 0) + 1)
                    ntr += len(tr6); bad += sum(not check_trail(t_, act, a6, "add")[0] for t_ in tr6) + (n6 is None or n6 % 2 == 0)
        for b in blocks:                                      # counted block entries: all trails valid
            if b.get("by_lemma"):
                continue
            for l in b["nodes"]:
                for j in b["nodes"]:
                    if j == l or j in G[l]:
                        _, trails = c.count(P[l], j, cap=BCAP, return_trails=BCAP)
                        ntr += len(trails); bad += sum(not check_trail(t, act, j, "add")[0] for t in trails)
        inv = inv and bad == 0
        rec["invertible"] = inv
        rec.update(trails_checked=ntr, failures=bad,
                   patterns={l: [f"{m:016X}" for m in P[l]] for l in range(64)},
                   graph={l: G[l] for l in range(64)})
    c.close()
    if "_counter" in cache6:
        cache6["_counter"].close()
    rec["secs"] = round(time.time() - t0, 1)
    res[str(p)] = rec
    print(f"p={p} invertible={inv} cyc0={cyc0} replaced={replaced} blocks={[(len(b['nodes']), b['rank'], len(b['unknown'])) for b in blocks]} "
          f"trails={rec.get('trails_checked')} fail={rec.get('failures')} {rec['secs']}s", flush=True)
    json.dump(res, open(OUT + ".tmp", "w"), indent=1); os.replace(OUT + ".tmp", OUT)
