"""DRAT certificates for the trail counts behind all other presence proofs.

Covers
  - the 4096 seven-round presence proofs of step20/step21 (one per cube of dimension 63
    and output bit),
  - the 46 gap-bit presence proofs of step22,
  - the presence proofs behind the degree lower bounds of step25/step25c, i.e. exactly
    the records that step25d_degree_summary.py uses (Dipper at seven rounds uses step21;
    a one-round bit whose presence proof is weaker than its full ANF, step25b, is skipped).
For each proof the trails are enumerated again; every trail is validated by the
CNF-independent checker, including its key pattern; the trails must be pairwise distinct;
the count must equal the recorded odd count; and the instance (input, output and key
pattern fixed by unit clauses) extended by one blocking clause per trail over the layer
masks must be UNSAT, with a DRAT proof checked by drat-trim (the enumeration is complete).
Usage: step31_drat_presence.py <cadical> <drat-trim> <part: r7|gap|degree> <outfile> [k/K]
       step31_drat_presence.py - - summary results/step31_drat_summary.json   (merge all outputs)"""
import glob, json, os, sys, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter
from dipper.drat import Drat
from dipper.witness import check_trail

CAD, DT, PART, OUT = sys.argv[1:5]
SHARD = tuple(map(int, sys.argv[5].split("/"))) if len(sys.argv) > 5 else (0, 1)   # "k/K": every K-th group
D = Drat(CAD, DT)
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
CAP = 20000


def with_kv(c):
    extra = []
    for t, (x, y) in enumerate(c.m.keylayers):
        for i in range(64):
            kv = c.kv[t][i]
            extra += [[-kv, y[i]], [-kv, -x[i]], [kv, -y[i], x[i]]]
    return Drat.base(c.m.cl + extra)


def certify(c, base, units, act, j, mode, V, recorded, st):
    assum = [u[0] for u in units]
    c._sel += 1
    sel = c.m.pool.id(("sel", c._sel))
    blocks, n, seen = [], 0, set()
    while n < CAP and c.s.solve(assumptions=assum + [sel]):
        val = {abs(l): l > 0 for l in c.s.get_model()}
        tr = [sum(1 << i for i, v in enumerate(vs) if val[v]) for _, vs in c.m.trace]
        if tuple(tr) in seen:                  # the n trails must be pairwise distinct
            st["duplicates"] += 1
        seen.add(tuple(tr))
        ok, why = check_trail(tr, act, j, mode, pattern=V)
        st["trails"] += 1
        if not ok:
            st["fail"].append([j, why])
        cl = [-v if val[v] else v for v in c.proj]
        blocks.append(cl)
        c.s.add_clause([-sel] + cl)
        n += 1
    capped = n >= CAP and c.s.solve(assumptions=assum + [sel])
    c.s.add_clause([-sel])
    st["proofs"] += 1
    if capped or n != recorded or n % 2 == 0:
        st["count_mismatch"].append([j, recorded, None if capped else n])
        return
    r = D.check(base, units + blocks)
    st["drat"] += 1
    st["drat_ok"] += r["status"] == "UNSAT" and bool(r["verified"])


def units_for(c, V, j, inputs=None):
    u = [[c.out[i] if i == j else -c.out[i]] for i in range(64)]
    u += [[c.kv[t][i] if (m >> i) & 1 else -c.kv[t][i]] for t, m in enumerate(V) for i in range(64)]
    if inputs is not None:
        u += [[c.m.inputs[i] if i in inputs else -c.m.inputs[i]] for i in range(64)]
    return u


def new_stats():
    return {"proofs": 0, "trails": 0, "drat": 0, "drat_ok": 0, "duplicates": 0, "fail": [], "count_mismatch": []}


def finish(key, st, t0):
    st["certified"] = (not st["fail"] and not st["count_mismatch"] and st["duplicates"] == 0
                       and st["drat"] == st["drat_ok"] == st["proofs"])
    st["secs"] = round(time.time() - t0, 1)
    res[key] = st
    print(key, {k: (v if not isinstance(v, list) else len(v)) for k, v in st.items()}, flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)


if PART in ("r7", "gap"):                  # same job list as step24_verify_all_trails.py
    jobs = {}
    if PART == "r7":
        p0 = json.load(open("results/step20_presence_r7_complete.json"))["per_bit"]
        jobs[("p=0", tuple(sorted(set(range(64)) - {0})), 7)] = [(int(j), v["pattern"], v["count"]) for j, v in p0.items()]
        for f in glob.glob("results/step21_presence_*_p.json"):
            for p, rec in json.load(open(f)).items():
                if rec.get("done"):
                    jobs[(f"p={p}", tuple(sorted(set(range(64)) - {int(p)})), 7)] = [
                        (int(j), b["pattern"], b["count"]) for j, b in rec["bits"].items()]
    else:
        for cs in json.load(open("results/step22_gap_presence.json"))["cases"]:
            jobs.setdefault((f"gap {cs['cube']} r={cs['rounds']}", tuple(cs["active"]), cs["rounds"]), []).append(
                (cs["bit"], cs["pattern"], cs["count"]))
    for gi, ((label, act, r), items) in enumerate(sorted(jobs.items())):
        key = f"{label}|{r}|{','.join(map(str, act))}"
        if key in res or gi % SHARD[1] != SHARD[0]:
            continue
        t0 = time.time(); st = new_stats()
        c = TrailCounter(list(act), r); base = with_kv(c)
        for j, pat, cnt in items:
            V = [int(m, 16) for m in pat]
            certify(c, base, units_for(c, V, j), list(act), j, "add", V, cnt, st)
        c.close()
        finish(key, st, t0)

elif PART == "degree":                     # the records used by step25d_degree_summary.py
    use = {}
    for f in ("results/step25_degree_part1.json", "results/step25_degree_part2.json",
              "results/step25_degree_add.json", "results/step25_degree_xor_lo.json"):
        if os.path.exists(f):
            for k, v in json.load(open(f)).items():
                for j, x in v.items():
                    if x["exact"]:
                        use[(k, int(j))] = (x["upper"], x)
    for k, x in json.load(open("results/step25c_degree_hard.json")).items():
        mode, r, j = k.split("|")
        if x.get("lower") is not None:
            kk = (f"{mode}|{r}", int(j))
            if kk not in use or use[kk][0] < x["lower"]:
                use[kk] = (x["lower"], x)
    anf = {int(j): x["degree"] for j, x in json.load(open("results/step25b_anf_degree_r1.json")).items()}
    for kk in [kk for kk in use if kk[0] == "add|1" and kk[1] in anf and use[kk][0] < anf[kk[1]]]:
        del use[kk]                        # lower bound from the full ANF only (step25b)
    groups = {}
    for (k, j), (deg, x) in use.items():
        groups.setdefault(k, []).append((j, deg, x))
    for gi, k in enumerate(sorted(groups, key=lambda s: (s.split("|")[0], int(s.split("|")[1])))):
        if k in res or gi % SHARD[1] != SHARD[0]:
            continue
        mode, r = k.split("|"); r = int(r)
        t0 = time.time(); st = new_stats(); st["weight_mismatch"] = []
        c = TrailCounter(None, r, mode=mode); base = with_kv(c)
        for j, deg, x in sorted(groups[k], key=lambda t: t[0]):
            u = set(x["u"])
            if len(u) < deg:
                st["weight_mismatch"].append([j, len(u), deg])
            V = [int(m, 16) for m in x["pattern"]]
            certify(c, base, units_for(c, V, j, inputs=u), sorted(u), j, mode, V, x["count"], st)
        c.close()
        if st["weight_mismatch"]:
            st["fail"].append("weight")
        finish(k, st, t0)
elif PART == "summary":
    out = {}
    for f in sorted(glob.glob("results/step31_drat_*.json")):
        if f.endswith("_summary.json"):
            continue
        part = os.path.basename(f)[len("step31_drat_"):-5].split("_")[0]
        for k, v in json.load(open(f)).items():
            out.setdefault(part, {})[k] = v
    S = {}
    for part, R in out.items():
        S[part] = {f: sum(v[f] for v in R.values()) for f in ("proofs", "trails", "drat", "drat_ok", "duplicates")}
        S[part]["groups"] = len(R); S[part]["certified_groups"] = sum(v["certified"] for v in R.values())
    json.dump({"summary": S, "groups": out}, open(OUT, "w"), indent=0)
    print(json.dumps(S, indent=1))
    sys.exit()
tot = {f: sum(v[f] for v in res.values()) for f in ("proofs", "trails", "drat", "drat_ok", "duplicates")}
tot["certified_groups"] = sum(v["certified"] for v in res.values()); tot["groups"] = len(res)
print("TOTAL", tot)
