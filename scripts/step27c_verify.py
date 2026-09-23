"""Independent verification of the seven-round linear-combination result.

Input: the final key patterns (one per output bit) for every cube of dimension 63,
results/step27_linear_combinations_final.json. How they were found does not matter.
For each cube the script
  1. builds G: edge l -> j (j != l) iff pattern v_l has a trail to bit j (solver);
  2. orders the strongly connected components of G so that every edge goes to an
     earlier component; M is then block lower-triangular, rows and columns in the
     same order, and M is invertible iff every diagonal block is;
  3. decides every diagonal block:
       - entries by exact trail counting (cap 2e4), every trail validated by the
         independent checker, including its key pattern;
       - otherwise, for retained output bits of one last-round S-box n and a row whose
         last-round key pattern is a single bit t of that S-box, by the last-round
         component lemma: entry(b) = sum over monomials z^{u+t} of ANF(S_b), u != 0, of
         c_V(u), the parity of six-round trails with pattern V to the mask u on S-box n
         (counted and validated);
       - otherwise, for a 2x2 block of two such bits whose other row is (1,1), by the
         lemma applied to the sum of the two bits (determinant = row sum);
  4. records the zero entries the argument uses (edges absent from a row to a later
     component), which rest on UNSAT answers of the solver.
Usage: step27c_verify.py <p-list> <outfile>
"""
import itertools, json, os, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter
from dipper.witness import check_trail
from dipper.cipher import PERM_INV, ROT, SBOX

CAP, CAP6 = 20000, 20000
WORD_BASE = {3: 48, 2: 32, 1: 16, 0: 0}
ROT_OF = {3: ROT[0], 2: ROT[1], 1: ROT[2], 0: ROT[3]}
ps = [int(x) for x in sys.argv[1].split(",")]
OUT = sys.argv[2]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
final = json.load(open("results/step27_linear_combinations_final.json"))


def retained(j):
    pos = PERM_INV[j]; w, i = pos // 16, pos % 16
    if w not in (2, 0):
        return None
    q = WORD_BASE[w] + ((i - ROT_OF[w]) % 16)
    return q // 4, q % 4


def anf_bits(bits):
    tt = [sum((SBOX[x] >> b) & 1 for b in bits) & 1 for x in range(16)]
    co = list(tt)
    for i in range(4):
        for x in range(16):
            if x >> i & 1:
                co[x] ^= co[x ^ (1 << i)]
    return {u for u in range(16) if co[u]}


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
    for v in sorted(G):
        if v not in idx:
            sc(v)
    return comps          # Tarjan emits components in reverse topological order: sinks first


def rank_gf2(rows, n):
    rows = list(rows); r = 0
    for b in range(n):
        piv = next((i for i in range(r, len(rows)) if (rows[i] >> b) & 1), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and (rows[i] >> b) & 1:
                rows[i] ^= rows[r]
        r += 1
    return r


for p in ps:
    if str(p) in res:
        continue
    t0 = time.time()
    act = sorted(set(range(64)) - {p})
    P = {int(l): [int(m, 16) for m in v] for l, v in final[str(p)]["patterns"].items()}
    c = TrailCounter(act, 7)
    c6 = None
    stats = {"trails7": 0, "trails6": 0, "failures": 0}

    def count7(l, j):
        n, trs = c.count(P[l], j, cap=CAP, return_trails=CAP)
        if n is None:
            return None
        for t in trs:
            stats["trails7"] += 1
            stats["failures"] += not check_trail(t, act, j, "add", pattern=P[l])[0]
        return n & 1

    def c6_mask(V, n_, u):
        global c6
        if c6 is None:
            c6 = TrailCounter(act, 6)
        mask = u << (4 * n_)
        a = [c6.out[i] if (mask >> i) & 1 else -c6.out[i] for i in range(64)]
        for tt, mk in enumerate(V):
            a += [c6.kv[tt][i] if (mk >> i) & 1 else -c6.kv[tt][i] for i in range(64)]
        if not c6.s.solve(assumptions=a):
            return 0
        c6._sel += 1; sel = c6.m.pool.id(("sel", c6._sel)); n = 0; trs = []
        while n < CAP6 and c6.s.solve(assumptions=a + [sel]):
            val = {abs(x): x > 0 for x in c6.s.get_model()}
            trs.append([sum(1 << i for i, v in enumerate(vs) if val[v]) for _, vs in c6.m.trace]); n += 1
            c6.s.add_clause([-sel] + [-v if val[v] else v for v in c6.proj])
        capped = n >= CAP6 and c6.s.solve(assumptions=a + [sel]); c6.s.add_clause([-sel])
        if capped:
            return None
        for t in trs:
            stats["trails6"] += 1
            stats["failures"] += not check_trail(t, act, 0, "add", final_mask=mask, pattern=V)[0]
        return n & 1

    def lemma_entry(l, bits):
        """entry of row l for the XOR of the retained output bits `bits` (same S-box), or None"""
        v7 = P[l][6]
        if bin(v7).count("1") != 1:
            return None
        q = v7.bit_length() - 1; n_, t = q // 4, q % 4
        info = [retained(j) for j in bits]
        if None in info or any(x[0] != n_ for x in info):
            return None
        g = anf_bits([x[1] for x in info])
        e = 0
        for mono in g:
            if (mono >> t) & 1 and mono != (1 << t):
                cv = c6_mask(P[l][:6], n_, mono ^ (1 << t))
                if cv is None:
                    return None
                e ^= cv
        return e

    G = {l: [j for j in range(64) if j != l and c.exists(P[l], j)] for l in range(64)}
    comps = sccs(G)
    pos = {l: k for k, comp in enumerate(comps) for l in comp}
    assert all(pos[j] <= pos[l] for l in G for j in G[l]), "edges must go to earlier or equal components"
    blocks, single_ok, how = [], 0, {"count": 0, "lemma": 0, "sum": 0, "single_count": 0, "single_lemma": 0}
    ok_all = True
    for comp in comps:
        if len(comp) == 1:
            l = comp[0]
            d = count7(l, l)
            if d is None:
                d = lemma_entry(l, [l]); how["single_lemma"] += d is not None
            else:
                how["single_count"] += 1
            ok_all &= d == 1
            continue
        k = len(comp)
        M = [[None] * k for _ in range(k)]
        lemma_used = False
        for a, l in enumerate(comp):
            for b, j in enumerate(comp):
                if j != l and j not in G[l]:
                    M[a][b] = 0
                    continue
                e = count7(l, j)
                if e is None:
                    e = lemma_entry(l, [j]); lemma_used |= e is not None
                M[a][b] = e
        unknown = [(a, b) for a in range(k) for b in range(k) if M[a][b] is None]
        rec = {"nodes": comp}
        if not unknown:
            rk = rank_gf2([sum(M[a][b] << b for b in range(k)) for a in range(k)], k)
            rec.update(rank=rk, by="lemma entries" if lemma_used else "counted entries"); inv = rk == k
            how["lemma" if lemma_used else "count"] += inv
        elif k == 2 and len({a for a, _ in unknown}) == 1:
            a = unknown[0][0]; other = 1 - a
            if M[other] == [1, 1]:
                s_ = lemma_entry(comp[a], comp)       # lemma on the XOR of both bits = row sum
                inv = s_ == 1
                rec.update(rank=2 if inv else None, by="sum")
                how["sum"] += inv
            else:
                inv = False; rec.update(rank=None, by="unknown")
        else:
            inv = False; rec.update(rank=None, by="unknown", unknown=unknown)
        rec["matrix"] = M
        blocks.append(rec); ok_all &= inv
    # zero entries used by the argument: row l, column j in a later component, no edge
    used_zeros = [(l, j) for l in range(64) for j in range(64) if j != l and pos[j] > pos[l]]
    ok_all &= stats["failures"] == 0
    res[str(p)] = {"verified": ok_all, "components": len(comps), "blocks": blocks, "how": how,
                   **stats, "used_zero_entries": len(used_zeros),
                   "used_zero_sample_seed_list": used_zeros, "secs": round(time.time() - t0, 1)}
    c.close()
    if c6 is not None:
        c6.close(); c6 = None
    print(f"p={p} verified={ok_all} blocks={[(len(b['nodes']), b['by'], b.get('rank')) for b in blocks]} "
          f"trails7={stats['trails7']} trails6={stats['trails6']} fail={stats['failures']} zeros={len(used_zeros)} {res[str(p)]['secs']}s", flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
