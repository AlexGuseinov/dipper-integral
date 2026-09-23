"""DRAT-check a random sample of the zero entries used in step27.

A zero entry M[l][j] = 0 (j outside the block of l) rests on the solver's answer
"no trail from the cube monomial to bit j with key pattern v_l" (UNSAT). For a
random sample of such entries the instance is written as a CNF (model clauses,
key-pattern indicator clauses, and the pattern/output as unit clauses), re-solved
by an external CaDiCaL with a DRAT proof, and the proof is checked by drat-trim.
Usage: step29_drat_zero_entries.py <cadical> <drat-trim> <n_samples>"""
import glob, json, os, random, subprocess, sys, tempfile, time
sys.path.insert(0, ".")
from dipper.count import TrailCounter

CAD, DT, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
recs = {}
for f in glob.glob("results/step27_lc_*.json"):
    recs.update({int(p): r for p, r in json.load(open(f)).items() if r.get("invertible")})
rng = random.Random(2026)
pool = []
for p, r in recs.items():
    G = {int(l): set(v) for l, v in r["graph"].items()}
    for l in range(64):
        for j in range(64):
            if j != l and j not in G[l]:
                pool.append((p, l, j))
sample = rng.sample(pool, min(N, len(pool)))
out, t00 = [], time.time()
work = tempfile.mkdtemp(prefix="drat27_")
for p, l, j in sorted(sample):
    act = sorted(set(range(64)) - {p})
    c = TrailCounter(act, 7)
    v = [int(m, 16) for m in recs[p]["patterns"][str(l)]]
    units = [[a] for a in c._assumptions(v, j)]
    extra = []
    for t, (x, y) in enumerate(c.m.keylayers):
        for i in range(64):
            kv = c.kv[t][i]
            extra += [[-kv, y[i]], [-kv, -x[i]], [kv, -y[i], x[i]]]
    cls = c.m.cl + extra + units
    nv = max(abs(l_) for cl in cls for l_ in cl)
    cnf = os.path.join(work, f"p{p}_l{l}_j{j}.cnf"); prf = cnf[:-4] + ".drat"
    with open(cnf, "w") as fh:
        fh.write(f"p cnf {nv} {len(cls)}\n")
        for cl in cls:
            fh.write(" ".join(map(str, cl)) + " 0\n")
    res = subprocess.run([CAD, "--no-binary", "-q", cnf, prf], capture_output=True, text=True)
    status = "UNSAT" if res.returncode == 20 else ("SAT" if res.returncode == 10 else f"rc{res.returncode}")
    ver = None
    if status == "UNSAT":
        chk = subprocess.run([DT, cnf, prf, "-w"], capture_output=True, text=True)
        ver = "s VERIFIED" in chk.stdout
    c.close()
    os.remove(cnf); os.remove(prf) if os.path.exists(prf) else None
    out.append({"p": p, "l": l, "j": j, "status": status, "drat_verified": ver})
    print(p, l, j, status, ver, flush=True)
summ = {"sampled": len(out), "unsat": sum(o["status"] == "UNSAT" for o in out),
        "verified": sum(bool(o["drat_verified"]) for o in out), "pool": len(pool),
        "seconds": round(time.time() - t00, 1)}
print(summ)
json.dump({"summary": summ, "entries": out}, open("results/step29_drat_zero_entries.json", "w"), indent=1)
