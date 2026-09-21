"""Export certificates as checkable artifacts.

UNSAT (certificate): write the CNF with the query assumptions as unit clauses,
run an external CaDiCaL binary with DRAT proof output, and check the proof with
drat-trim. SAT (no certificate): extract the trail and validate it with the
independent checker in witness.py."""
import gzip, hashlib, os, subprocess, time
from pysat.solvers import Solver
from .models import build
from .witness import check_trail


def write_cnf(path, clauses, nvars):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")


def unsat_proof(active, r, j, mode, workdir, cadical, drat_trim, keep=True):
    m, out = build(set(active), r, "mp", mode)
    cl = m.cl + [[out[i]] if i == j else [-out[i]] for i in range(64)]
    nv = max(abs(l) for c in cl for l in c)
    base = os.path.join(workdir, f"{mode}_r{r}_d{len(active)}_{hashlib.sha1(str(sorted(active)).encode()).hexdigest()[:8]}_b{j}")
    cnf, prf = base + ".cnf", base + ".drat"
    write_cnf(cnf, cl, nv)
    t0 = time.time()
    res = subprocess.run([cadical, "--no-binary", "-q", cnf, prf], capture_output=True, text=True)
    t1 = time.time()
    status = "UNSAT" if res.returncode == 20 else ("SAT" if res.returncode == 10 else f"rc{res.returncode}")
    chk = subprocess.run([drat_trim, cnf, prf, "-w"], capture_output=True, text=True) if status == "UNSAT" else None
    t2 = time.time()
    verified = chk is not None and "s VERIFIED" in chk.stdout
    row = {"mode": mode, "rounds": r, "dim": len(active), "bit": j, "solver": status,
           "drat_trim": "VERIFIED" if verified else "FAILED",
           "cnf_sha256": hashlib.sha256(open(cnf, "rb").read()).hexdigest(),
           "vars": nv, "clauses": len(cl), "proof_bytes": os.path.getsize(prf),
           "solve_s": round(t1 - t0, 2), "check_s": round(t2 - t1, 2)}
    for fn in (cnf, prf):                       # keep gzipped copies
        if keep:
            with open(fn, "rb") as a, gzip.open(fn + ".gz", "wb") as b:
                b.write(a.read())
        os.remove(fn)
    return row


def sat_witness(active, r, j, mode):
    m, out = build(set(active), r, "mp", mode)
    s = Solver(name="cadical153", bootstrap_with=m.cl)
    if not s.solve(assumptions=[out[i] if i == j else -out[i] for i in range(64)]):
        s.delete(); return {"status": "UNSAT"}
    val = {abs(l): l > 0 for l in s.get_model()}
    s.delete()
    masks = [sum(1 << i for i, v in enumerate(vs) if val[v]) for _, vs in m.trace]
    ok, why = check_trail(masks, active, j, mode)
    return {"status": "SAT", "trail_valid": ok, "why": why, "masks": [f"{x:016x}" for x in masks]}
