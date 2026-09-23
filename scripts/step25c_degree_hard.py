"""Third pass for the degree cases not settled by step25: try the bound D with
many candidate monomials (small budget each); if that fails, prove degree >= D-1.
The result for each case is a certified interval [lower, upper]."""
import json, os, random, sys, time
sys.path.insert(0, ".")
from pysat.solvers import Solver
from pysat.card import ITotalizer
from dipper.models import build
import importlib.util
spec = importlib.util.spec_from_file_location("s25", "scripts/step25_exact_degree.py")

cases = []
exact_any = set()
for f in ("results/step25_degree_part1.json", "results/step25_degree_part2.json",
          "results/step25_degree_add.json", "results/step25_degree_xor_lo.json"):
    if os.path.exists(f):
        for k, v in json.load(open(f)).items():
            exact_any |= {(k, j) for j, x in v.items() if x["exact"]}
for f in ("results/step25_degree_add.json", "results/step25_degree_xor_lo.json", "results/step25_degree_part1.json"):
    if not os.path.exists(f):
        continue
    for k, v in json.load(open(f)).items():
        mode, r = k.split("|")
        for j, x in v.items():
            if not x["exact"] and (k, j) not in exact_any and (mode, int(r), int(j), x["upper"]) not in cases:
                cases.append((mode, int(r), int(j), x["upper"]))
OUT = "results/step25c_degree_hard.json"
res = json.load(open(OUT)) if os.path.exists(OUT) else {}

# reuse prove() from step25 with a small budget per candidate monomial
os.environ["REDO"] = "1"
src = open("scripts/step25_exact_degree.py").read()
ns = {}
exec(src[:src.index("for mode, rounds in jobs:")].replace("jobs = [(m, [int(r) for r in rs.split(\",\")]) for m, rs in (x.split(\":\") for x in sys.argv[1].split(\";\"))]", "jobs = []").replace("OUT = sys.argv[2]", "OUT = '/dev/null'").replace("res = json.load(open(OUT)) if os.path.exists(OUT) else {}", "res = {}"), ns)
prove = ns["prove"]
ns["STAGES"][:] = [(45, 40), (15, 400)]

for mode, r, j, D in cases:
    key = f"{mode}|{r}|{j}"
    if key in res and (res[key]["lower"] is not None or os.environ.get("DEEP") is None):
        continue
    t0 = time.time()
    m, out = build(None, r, "mp", mode)
    tot = ITotalizer(lits=[-v for v in m.inputs], ubound=64, top_id=m.pool.top)
    s = Solver(name="cadical153", bootstrap_with=m.cl + tot.cnf.clauses)
    base = [out[i] if i == j else -out[i] for i in range(64)]
    lower, proof = None, None
    levels = ((D, 300), (D - 1, 60)) if not os.environ.get("DEEP") else tuple((D - d, 40) for d in range(int(os.environ.get("DEEP_FROM", "2")), int(os.environ.get("DEEP_TO", "5"))))
    for w, maxu in levels:
        tried = 0
        fresh = max(tot.top_id, m.pool.top) + 1 + w
        while tried < maxu and s.solve(assumptions=base + [-tot.rhs[64 - w], fresh]):
            model = set(l for l in s.get_model() if l > 0)
            u = [i for i, v in enumerate(m.inputs) if v in model]
            tried += 1
            s.add_clause([-fresh] + [-v if v in model else v for v in m.inputs])
            if len(u) < w:
                continue
            pr = prove(u, r, mode, j, 99991 * tried + w)
            if pr and pr["all_trails_ok"]:
                lower, proof = len(u), dict(pr, u=u); break
        if lower is not None:
            break
    s.delete()
    res[key] = {"upper": D, "lower": lower, "secs": round(time.time() - t0, 1), **({} if not proof else proof)}
    print(key, "upper", D, "lower", lower, res[key]["secs"], "s", flush=True)
    json.dump(res, open(OUT, "w"), indent=1)
