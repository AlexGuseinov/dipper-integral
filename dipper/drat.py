"""DRAT certificates for UNSAT answers and for complete trail enumerations.

An UNSAT answer ("no trail") is certified by re-solving the instance with an external
CaDiCaL binary that writes a DRAT proof, and checking the proof with drat-trim.

A trail COUNT n is certified in the same way. The enumeration found n trails, each of
which is validated by the CNF-independent checker (dipper/witness.py). The instance
extended by one blocking clause per found trail (over the projection variables, i.e.
the layer masks) is UNSAT exactly when no further trail exists, so a checked DRAT proof
of that extended instance shows that the enumeration is complete. Distinct trails have
distinct projections (dipper/count.py), so the count is exactly n.
"""
import os, subprocess, tempfile, time


class Drat:
    def __init__(self, cadical, drattrim, workdir=None):
        self.cad, self.dt = cadical, drattrim
        self.work = workdir or tempfile.mkdtemp(prefix="drat_")
        self._k = 0

    @staticmethod
    def base(clauses):
        """Pre-render the clauses that all instances of one model share."""
        nv = max((abs(l) for c in clauses for l in c), default=0)
        return nv, len(clauses), "".join(" ".join(map(str, c)) + " 0\n" for c in clauses)

    def check(self, base, extra):
        """base: result of Drat.base; extra: additional clauses (units, blocking, ...).
        Returns dict(status, verified, secs)."""
        t0 = time.time()
        nv0, n0, text = base
        nv = max([nv0] + [abs(l) for c in extra for l in c])
        self._k += 1
        cnf = os.path.join(self.work, f"i{os.getpid()}_{self._k}.cnf")
        prf = cnf[:-4] + ".drat"
        with open(cnf, "w") as fh:
            fh.write(f"p cnf {nv} {n0 + len(extra)}\n")
            fh.write(text)
            fh.write("".join(" ".join(map(str, c)) + " 0\n" for c in extra))
        r = subprocess.run([self.cad, "--no-binary", "-q", cnf, prf], capture_output=True, text=True)
        status = {20: "UNSAT", 10: "SAT"}.get(r.returncode, f"rc{r.returncode}")
        ver = None
        if status == "UNSAT":
            chk = subprocess.run([self.dt, cnf, prf, "-w"], capture_output=True, text=True)
            ver = "s VERIFIED" in chk.stdout
        for f in (cnf, prf):
            if os.path.exists(f):
                os.remove(f)
        return {"status": status, "verified": ver, "secs": round(time.time() - t0, 2)}
