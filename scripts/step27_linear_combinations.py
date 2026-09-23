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
SAMPLES = 120            # candidates per cyclic bit and sweep
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
    for comp in [s_ for s_ in sccs(G) if len(s_) > 1]:
        info = [retained_sbox_bit(j) for j in comp]
        same_sbox_pair = len(comp) == 2 and None not in info and info[0][0] == info[1][0]
        if same_sbox_pair:
            rows, unknown, rk = None, None, None
        else:
            rows, unknown = block_rows(comp)
            rk = None if unknown else rank_gf2(rows, comp)
        if same_sbox_pair:
            # Lemma (last-round component), applied to each output bit separately: for pattern (V, k7_t)
            # the entry of output bit j with S-box bit b is 0 if z_t occurs in ANF(b) only alone, and the
            # six-round coefficient of s_a if it occurs only alone and in z_a z_t. Choose two such rows
            # with a common partner a (V = six-round presence proof for s_a) and determinant 1.
            n_ = info[0][0]
            anfs = [component_anf([info[0][1]]), component_anf([info[1][1]])]
            opts = []
            for t in range(4):
                ent, a_star, ok = [], None, True
                for A in anfs:
                    mons = [u for u in A if (u >> t) & 1]
                    parts = [u ^ (1 << t) for u in mons if u != (1 << t)]
                    if any(bin(q).count("1") != 1 for q in parts) or len(parts) > 1:
                        ok = False; break
                    if parts:
                        a_ = parts[0].bit_length() - 1
                        if a_star not in (None, a_):
                            ok = False; break
                        a_star = a_; ent.append(1)
                    else:
                        ent.append(0)
                if ok and a_star is not None and any(ent):
                    opts.append((t, a_star, tuple(ent)))
            done = None
            for (t1, a1, e1) in opts:
                for (t2, a2, e2) in opts:
                    if (e1[0] * e2[1] + e1[1] * e2[0]) % 2 != 1:
                        continue
                    V1, V2 = pres6(4 * n_ + a1), pres6(4 * n_ + a2)
                    if V1 is None or V2 is None:
                        continue
                    # assign rows to labels with a nonzero diagonal where possible
                    l1, l2 = (comp[0], comp[1]) if e1[0] and e2[1] else (comp[1], comp[0])
                    v1 = list(V1) + [1 << (4 * n_ + t1)]; v2 = list(V2) + [1 << (4 * n_ + t2)]
                    P[l1], G[l1] = v1, reach(v1, l1); P[l2], G[l2] = v2, reach(v2, l2)
                    fixed_rows.update((l1, l2)); repairs += 2
                    done = {"nodes": comp, "rank": 2, "unknown": [], "by_lemma": {"nibble": n_,
                            "rows": [{"label": l1, "t": t1, "a": a1, "entries": list(e1), "V": [f"{m:016X}" for m in V1]},
                                     {"label": l2, "t": t2, "a": a2, "entries": list(e2), "V": [f"{m:016X}" for m in V2]}]}}
                    lemma_rows[frozenset(comp)] = done
                    print(f"   block {comp}: both rows by the last-round component lemma (nibble {n_}, rows t={t1}:{e1}, t={t2}:{e2})", flush=True)
                    break
                if done:
                    break
            if done:
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
                                if rank_gf2(trial, comp) > (rk or 0):
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
                        if rank_gf2(trial, comp) > (rk or 0):
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
    if lemma_rows:
        break_cycles(6)
        blocks, inv = [], True
        for comp in [s_ for s_ in sccs(G) if len(s_) > 1]:
            if frozenset(comp) in lemma_rows:
                blocks.append(lemma_rows[frozenset(comp)])        # determinant 1 by the lemma entries
                continue
            rows, unknown = block_rows(comp)
            rk = None if unknown else rank_gf2(rows, comp)
            blocks.append({"nodes": comp, "rank": rk, "unknown": unknown}); inv &= (rk == len(comp))
    # sanity: block structure must still hold after repairs
    inv &= all(len(x) == 1 or any(set(x) == set(b["nodes"]) for b in blocks) for x in sccs(G))
    rec = {"invertible": inv, "cyclic_nodes_start": cyc0, "patterns_replaced": replaced, "block_repairs": repairs,
           "blocks": blocks, "lemma_blocks": [b["by_lemma"] | {"nodes": b["nodes"]} for b in lemma_rows.values()]}
    if inv:
        ntr = bad = 0
        in_block = {l for b in blocks for l in b["nodes"]}
        for l in range(64):                                   # singleton rows: odd diagonal, all trails valid
            if l in in_block:
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
