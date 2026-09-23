"""DRAT certificates for every solver answer behind the seven-round linear-combination result.

Input: the final key patterns (results/step27_linear_combinations_final.json) and the block
structure found by the independent verifier (results/step27c_verify.json). For each cube:
  zero entries  - for every row l, the set Z_l of bits without a trail for pattern v_l is
                  certified at once: the instance "pattern v_l, output mask e_j for some
                  j in Z_l" (exactly-one constraint over Z_l) must be UNSAT, with a checked
                  DRAT proof. This covers every zero entry of M, inside and outside blocks.
                  The zeros that the verifier used (outside and inside the blocks) must be
                  among these certified zeros.
  counted entries - every entry that the verifier obtained by counting (all singleton
                  diagonals and the counted entries of the blocks) is enumerated again; every
                  trail is validated by the CNF-independent checker, including its key
                  pattern; the trails must be pairwise distinct; and the instance (input,
                  output and key pattern fixed by unit clauses) with one blocking clause per
                  trail over the layer masks must be UNSAT with a checked DRAT proof (the
                  enumeration is complete). Masks and pattern determine a trail, so each
                  blocking clause excludes exactly one trail.
  sum blocks    - the six-round counts c_V(u) of the last-round component lemma are
                  certified in the same way (count > 0: blocked instance; count 0: UNSAT).
The parities are recomputed and compared with the verifier's matrix.
Usage: step30_drat_lincomb.py <cadical> <drat-trim> <p-list> <outfile>"""
import json, os, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter
from dipper.drat import Drat
from dipper.witness import check_trail
from dipper.lastround import retained, anf_bits

CAD, DT, ps, OUT = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")], sys.argv[4]
D = Drat(CAD, DT)
final = json.load(open("results/step27_linear_combinations_final.json"))
ver = json.load(open("results/step27c_verify.json"))["cubes"]
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
CAP = 20000


def with_kv(c):
    extra = []
    for t, (x, y) in enumerate(c.m.keylayers):
        for i in range(64):
            kv = c.kv[t][i]
            extra += [[-kv, y[i]], [-kv, -x[i]], [kv, -y[i], x[i]]]
    return Drat.base(c.m.cl + extra)


def pattern_units(c, V):
    return [[c.kv[t][i] if (m >> i) & 1 else -c.kv[t][i]] for t, m in enumerate(V) for i in range(64)]


def enumerate_certify(c, base, V, out_units, act, check_kw, st):
    """Enumerate all trails for pattern V and the output given by out_units; validate each;
    certify completeness by DRAT. Returns the count, or None if above CAP."""
    assum = [u[0] for u in pattern_units(c, V)] + [u[0] for u in out_units]
    c._sel += 1
    sel = c.m.pool.id(("sel", c._sel))
    blocks, n, seen = [], 0, set()
    while n < CAP and c.s.solve(assumptions=assum + [sel]):
        val = {abs(l): l > 0 for l in c.s.get_model()}
        tr = [sum(1 << i for i, v in enumerate(vs) if val[v]) for _, vs in c.m.trace]
        if tuple(tr) in seen:                  # the n trails must be pairwise distinct
            st["duplicates"] += 1
        seen.add(tuple(tr))
        ok, why = check_trail(tr, act, pattern=V, **check_kw)
        st["trails"] += 1
        if not ok:
            st["fail"].append(why)
        cl = [-v if val[v] else v for v in c.proj]
        blocks.append(cl)
        c.s.add_clause([-sel] + cl)
        n += 1
    capped = n >= CAP and c.s.solve(assumptions=assum + [sel])
    c.s.add_clause([-sel])
    if capped:
        return None
    r = D.check(base, pattern_units(c, V) + out_units + blocks)
    st["drat"] += 1
    st["drat_ok"] += r["status"] == "UNSAT" and bool(r["verified"])
    return n


for p in ps:
    if str(p) in res:
        continue
    t0 = time.time()
    act = sorted(set(range(64)) - {p})
    P = {int(l): [int(m, 16) for m in v] for l, v in final[str(p)]["patterns"].items()}
    vrec = ver[str(p)]
    c = TrailCounter(act, 7)
    base = with_kv(c)
    st = {"trails": 0, "trails6": 0, "fail": [], "drat": 0, "drat_ok": 0, "duplicates": 0,
          "zero_rows": 0, "zero_entries": 0, "counted_entries": 0, "parity_mismatch": [],
          "zero_inconsistent": []}
    # ---- zero entries, one certificate per row
    edges = {}
    for l in range(64):
        Z = [j for j in range(64) if not c.exists(P[l], j)]
        edges[l] = set(range(64)) - set(Z)
        if not Z:
            continue
        cls = pattern_units(c, P[l]) + [[-c.out[i]] for i in range(64) if i not in Z]
        cls += [[c.out[j] for j in Z]]
        cls += [[-c.out[a], -c.out[b]] for k, a in enumerate(Z) for b in Z[k + 1:]]
        r = D.check(base, cls)
        st["drat"] += 1; st["zero_rows"] += 1; st["zero_entries"] += len(Z)
        st["drat_ok"] += r["status"] == "UNSAT" and bool(r["verified"])
    # ---- the zeros used by the verifier must be among the certified ones
    for l, j in vrec["used_zero_sample_seed_list"]:
        if j in edges[l]:
            st["zero_inconsistent"].append(["used", l, j])
    for b in vrec["blocks"]:
        for a, l in enumerate(b["nodes"]):
            for bb, j in enumerate(b["nodes"]):
                if j not in edges[l] and b["matrix"][a][bb] != 0:
                    st["zero_inconsistent"].append(["block", l, j, b["matrix"][a][bb]])
    # ---- counted entries
    in_block = {l for b in vrec["blocks"] for l in b["nodes"]}
    todo = [(l, l, 1) for l in range(64) if l not in in_block]
    for b in vrec["blocks"]:
        for a, l in enumerate(b["nodes"]):
            for bb, j in enumerate(b["nodes"]):
                if b["matrix"][a][bb] is not None and j in edges[l]:
                    todo.append((l, j, b["matrix"][a][bb]))
    for l, j, expect in todo:
        outu = [[c.out[i] if i == j else -c.out[i]] for i in range(64)]
        n = enumerate_certify(c, base, P[l], outu, act, {"j": j, "mode": "add"}, st)
        st["counted_entries"] += 1
        if n is None or n % 2 != expect:
            st["parity_mismatch"].append([l, j, n, expect])
    # ---- sum blocks: six-round counts of the component lemma
    c6 = None
    for b in vrec["blocks"]:
        if b["by"] != "sum":
            continue
        a = next(k for k in range(2) if None in b["matrix"][k])
        l = b["nodes"][a]
        assert bin(P[l][6]).count("1") == 1, "component lemma needs a single last-round key bit"
        q = P[l][6].bit_length() - 1; n_, t = q // 4, q % 4
        info = [retained(j) for j in b["nodes"]]
        assert all(x is not None and x[0] == n_ for x in info)
        g = anf_bits([x[1] for x in info])
        if c6 is None:
            c6 = TrailCounter(act, 6); base6 = with_kv(c6)
        e = 0
        for mono in sorted(g):
            if (mono >> t) & 1 and mono != (1 << t):
                u = mono ^ (1 << t); mask = u << (4 * n_)
                outu = [[c6.out[i] if (mask >> i) & 1 else -c6.out[i]] for i in range(64)]
                before = st["trails"]
                cnt = enumerate_certify(c6, base6, P[l][:6], outu, act, {"j": 0, "mode": "add", "final_mask": mask}, st)
                st["trails6"] += st["trails"] - before
                if cnt is None:
                    st["parity_mismatch"].append(["six", l, mono, None]); continue
                e ^= cnt & 1
        if e != 1:
            st["parity_mismatch"].append(["sum", b["nodes"], e])
    c.close()
    if c6 is not None:
        c6.close()
    st["trails7"] = st["trails"] - st["trails6"]
    st["certified"] = (not st["fail"] and not st["parity_mismatch"] and not st["zero_inconsistent"]
                       and st["duplicates"] == 0 and st["drat"] == st["drat_ok"])
    st["secs"] = round(time.time() - t0, 1)
    res[str(p)] = st
    print(f"p={p} certified={st['certified']} drat={st['drat_ok']}/{st['drat']} zeros={st['zero_entries']} "
          f"counted={st['counted_entries']} trails7={st['trails7']} trails6={st['trails6']} "
          f"fail={len(st['fail'])} dup={st['duplicates']} mismatch={st['parity_mismatch']} "
          f"zero_inconsistent={len(st['zero_inconsistent'])} {st['secs']}s", flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
