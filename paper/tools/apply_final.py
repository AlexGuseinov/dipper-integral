"""Update paper.tex with the final seven-round presence results (step21) and the
explicit gap-bit keys (step23). Uses the 'all cubes' wording only if every one
of the 64 x 64 (cube, bit) cases has a validated presence proof."""
import glob, json, statistics, sys, re

P = "paper.tex"
s = open(P).read()

def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)

# ------------------------------------------------------------------ data
p0 = json.load(open("../results/step20_presence_r7_complete.json"))["per_bit"]
cases = {0: {int(j): dict(v, how="search") for j, v in p0.items()}}
secs = {0: 1211.0 + 670.0}                         # step17 + step18 wall time for p = 0
for f in glob.glob("../results/step21_presence_*_p.json"):
    for p, rec in json.load(open(f)).items():
        if rec.get("done"):
            cases[int(p)] = {int(j): b for j, b in rec["bits"].items()}
            secs[int(p)] = rec.get("secs", 0)
full = len(cases) == 64 and all(
    len(b) == 64 and all(x.get("witness_ok") for x in b.values()) for b in cases.values())
allb = [x for b in cases.values() for x in b.values() if x.get("witness_ok")]
cnts = [x["count"] for x in allb]
assert all(c % 2 == 1 for c in cnts)
v24 = json.load(open("../results/step24_all_trails_verified.json"))
n24p = sum(v["n_proofs"] for v in v24.values()); n24t = sum(v["n_trails"] for v in v24.values())
assert sum(len(v["failures"]) for v in v24.values()) == 0
print("step24: proofs", n24p, "trails", n24t)
nseed = sum(1 for x in allb if x.get("how") == "seed")
npart = sum(1 for x in allb if str(x.get("how", "")).startswith("partial"))
nsearch = len(allb) - nseed - npart
core_h = float(sys.argv[1]) if len(sys.argv) > 1 else sum(secs.values()) / 3600   # measured total, passed explicitly
print("positions done:", len(cases), "full:", full, "proofs:", len(allb),
      "count range:", min(cnts), max(cnts), "median:", statistics.median(cnts),
      "seed:", nseed, "core-hours: %.1f" % core_h, "partial:", npart, "search:", nsearch)

try:
    w = json.load(open("../results/step23_gap_witness_keys.json"))
    nkeys = sum(1 for c in w["cases"] if c.get("reference_check"))
except FileNotFoundError:
    nkeys = 0
print("gap bits with explicit keys:", nkeys)

# ------------------------------------------------------------------ abstract
a0 = s.index(r"\begin{abstract}") + len(r"\begin{abstract}")
a1 = s.index(r"\end{abstract}")
seven = (r"At seven rounds no bit-aligned cube is certified, and presence proofs, i.e.\ key monomials with an odd number of trails, show that this is exact: for independent round keys, no bit-aligned cube yields a balanced output bit after seven rounds."
         if full else
         r"At seven rounds no bit-aligned cube is certified; for the cubes that keep bit~0 constant, presence proofs, i.e.\ key monomials with an odd number of trails, show that every output bit is unbalanced.")
abstract = (r"""
Dipper is a 64-bit lightweight block cipher whose round combines the GIFT S-box and bit permutation with two 16-bit modular additions on half of the state. Its integral resistance was so far supported only by experiments with a few random keys. We replace this evidence by key-independent results. We model monomial trails through reduced-round Dipper as SAT instances with exact local transitions, including a rule for the modular additions derived from the Braeken--Semaev characterisation. Certificates at the round boundaries are backed by DRAT proofs checked with \texttt{drat-trim}, and every trail behind a missing certificate is validated independently of the SAT encoding. The published five-round properties hold for all round keys, and six-round properties exist. """
    + seven + r""" They also show that all 46 bits whose sums stayed zero in thousands of random-key trials without being certified are unbalanced. An ablation isolates the effect of the two modular additions: replacing them by XOR, or removing them, extends the longest certified property from six to nine and ten rounds. At the six-round boundary every certified bit comes from the two retained words, which pass through the additions unchanged. On all instances examined, the model with exact local transitions certifies the same bits as the bit-based division property.
""")
s = s[:a0] + abstract + s[a1:]
nw = len(re.sub(r"\\[a-zA-Z]+|[{}$]", " ", abstract).split())
print("abstract words (approx.):", nw)

rep(r"\noindent\textbf{Keywords:} integral cryptanalysis; division property; monomial prediction; modular addition; SAT; DRAT; lightweight block cipher; Dipper",
    r"\noindent\textbf{Keywords:} integral cryptanalysis; monomial prediction; division property; modular addition; SAT; lightweight block cipher")

# ------------------------------------------------------------------ gap-bit keys
if nkeys:
    rep(r"None of these bits is balanced. Each of their cube sums is a nonzero polynomial in the round keys that vanished in all 3200 trials. This is the failure mode of the 80-trial experiment of Section~\ref{sec:results} in a stronger form: sampling keys cannot detect it, and only an algebraic argument decides it.",
        r"None of these bits is balanced. Each of their cube sums is a nonzero polynomial in the round keys that vanished in all 3200 trials. This is the failure mode of the 80-trial experiment of Section~\ref{sec:results} in a stronger form: uniformly random keys almost never reveal it, and an algebraic argument is needed to decide it. The presence proof also shows where to look. If $v$ is the key pattern of a proof, some round key whose bits lie inside $v$ gives the cube sum~1, because the sum of the cube sum over all such keys equals the coefficient of $k^v$. Sampling sparse keys inside $v$ found such round keys for " + str(nkeys) + r" of the 46 bits, and each was confirmed with the reference implementation. For these bits the claim can be checked without the SAT model.")

rep(r"The 110 trails behind the presence proofs of Sections~\ref{sec:results} and~\ref{sec:tightness} passed the same check.",
    r"For every presence proof of Sections~\ref{sec:results} and~\ref{sec:tightness} (" + str(n24p) + r" proofs), all trails were enumerated again, each of the " + f"{n24t:,}".replace(",", r"\,") + r" trails passed the same check, and each count was confirmed to be odd.")
if full:
    N = len(allb)
    rep(r"For the cubes that keep bit~0 constant, presence proofs (Section~\ref{sec:presence}) show that the answer is exact: after seven rounds every output bit is unbalanced.",
        r"Presence proofs (Section~\ref{sec:presence}) show that this answer is exact: for each of the 64 cubes of dimension~63, every output bit is unbalanced after seven rounds, so by Lemma~\ref{lem:monobal} no bit-aligned cube gives a seven-round property on a single output bit, for independent round keys.")
    rep(r"Our seven-round statement is therefore, in general, a statement about the model, not a proof that Dipper has no seven-round integral distinguisher. The exceptions are presence proofs: an odd number of trails for one key monomial proves that the cube sum is a nonzero polynomial in the round keys, so that the bit is not balanced. We state such results only for the cubes for which we have them, and only for independent round keys.",
        r"Where we claim more, we use presence proofs: an odd number of trails for one key monomial proves that the cube sum is a nonzero polynomial in the round keys, so that the bit is not balanced. With presence proofs for all 64 cubes of dimension~63, our seven-round statement holds for Dipper with independent round keys, not only within the model. We do not claim it for round keys produced by the key schedule.")
    rep(r"and many random restarts are made. For the 63-dimensional cubes",
        r"and many random restarts are made. A pattern that proved a bit for one cube is tried first for the same bit of the other cubes, as a whole and then with only its rounds 3--7 (or 4--7) kept and the earlier rounds searched afresh. For the 63-dimensional cubes")
    i0 = s.index(r"The seven-round entries of Table~\ref{tab:maximal} say only that the model has a trail.")
    i1 = s.index(r"\subsection{Where the balanced bits come from}")
    s = s[:i0] + (r"The seven-round entries of Table~\ref{tab:maximal} say only that the model has a trail. For each of the 64 cubes of dimension~63 and each of the 64 output bits of $S^{(7)}$ we searched for a presence proof (Lemma~\ref{lem:presence}), and found one in all 4096 cases. The trail counts of the key patterns found range from " + str(min(cnts)) + " to " + str(max(cnts)) + r", and " + str(sum(1 for c in cnts if c == 1)) + r" of them equal~1. For every proof all trails were enumerated again and passed the independent check (Section~\ref{sec:validation}). The search took about " + ("%.0f" % core_h) + r" core-hours in total. Reusing patterns across positions of the constant bit (Section~\ref{sec:presence}) was decisive: whole patterns gave " + str(nseed) + r" of the 4096 proofs and partial patterns " + str(npart) + r", and the random search gave the remaining " + str(nsearch) + r". Every bit-aligned cube of dimension at most 63 lies in one of the 64 cubes, so by Lemma~\ref{lem:monobal} no bit-aligned cube has a balanced output bit after seven rounds, for independent round keys. Since the sum of $T^{-1}(S^{(8)})$ over a cube equals that of $S^{(7)}$ (proof of Lemma~\ref{lem:free}), the same holds for $T^{-1}(S^{(8)})$. The seven-round answer of the model is therefore exact. Over bit-aligned cubes and single output bits, the six-round properties of Table~\ref{tab:maximal}, and their extension to $T^{-1}(C)$ by Lemma~\ref{lem:free}, are the longest key-independent integral properties of Dipper with independent round keys. This does not exclude probabilistic or weak-key distinguishers.") + "\n\n" + s[i1:]
    rep(r"for all 46 persistent gap bits and for every output bit of the seven-round cubes that keep bit~0 constant.",
        r"for all 46 persistent gap bits and for every output bit of all 64 seven-round cubes of dimension~63.")
    rep(r"The same search over the other 63 positions of the constant bit would turn the seven-round statement into a statement about the cipher for all bit-aligned cubes.",
        r"With them the seven-round statement becomes a statement about the cipher for all bit-aligned cubes; the search took about " + ("%.0f" % core_h) + r" core-hours.")
    rep(r"\item The seven-round statement is exact only for the cubes that keep bit~0 constant. For the other cubes it holds within an existence-based model and does not exclude a seven-round property that depends on trail cancellation. It also says nothing about input sets that are not bit-aligned cubes, or about output functions other than single bits.",
        r"\item The seven-round statement concerns bit-aligned cubes and single output bits. It says nothing about input sets that are not bit-aligned cubes, or about linear combinations of output bits.")
    rep(r"Within the existence-based model, no bit-aligned cube reaches seven rounds, and every trail behind this statement has been validated independently.",
        r"No bit-aligned cube gives a balanced bit of $S^{(7)}$: the model has no certificate there, and presence proofs show that every output bit is unbalanced over every such cube, for independent round keys.")
    rep(r"Presence proofs separate ``no certificate'' from ``not balanced'' where they apply. Every bit that the experiments could not decide is unbalanced, and after seven rounds every output bit is unbalanced for every cube that keeps bit~0 constant. Extending this to all positions of the constant bit, and ultimately to integral resistance in the sense of~\cite{hebborn2021}, is the natural next step.",
        r"Presence proofs separate ``no certificate'' from ``not balanced'': every bit that the experiments could not decide is unbalanced, and so is every output bit after seven rounds. Integral resistance in the sense of~\cite{hebborn2021}, which also covers other input subspaces and linear combinations of output bits, is the natural next step.")

open(P, "w").write(s)
print("paper.tex updated; full =", full)
