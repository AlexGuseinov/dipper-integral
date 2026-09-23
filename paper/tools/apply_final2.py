"""Final text updates after exact degree, minimal cube, linear combinations and the
key-schedule probe: abstract, contributions, discussion, limitations, conclusion."""
import re
P = "paper.tex"; s = open(P).read()
def rep(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:90]); s = s.replace(o, n)

a0 = s.index(r"\begin{abstract}") + len(r"\begin{abstract}"); a1 = s.index(r"\end{abstract}")
abstract = r"""
Dipper is a 64-bit lightweight block cipher whose round combines the GIFT S-box and bit permutation with two 16-bit modular additions on half of the state. Its integral resistance was so far supported only by experiments with a few random keys. We replace this evidence by key-independent results. We model monomial trails through reduced-round Dipper as SAT instances with exact local transitions, including a rule for the modular additions derived from the Braeken--Semaev characterisation, and back the results by DRAT proofs and independently validated trails. The published five-round properties hold for all round keys, and six-round properties exist; the smallest certified six-round cube, of size $2^{60}$, is proven minimal. At seven rounds no bit-aligned cube is certified. Presence proofs, i.e.\ key monomials with an odd number of trails, show that this is exact: for independent round keys, no nonzero linear combination of output bits is balanced over any bit-aligned cube. They also show that 46 bits whose sums stayed zero in thousands of random-key trials are not balanced, and they determine the algebraic degree of 1843 of 1856 output bits exactly. Replacing the two modular additions by XOR, or removing them, extends the longest certified property from six to nine and ten rounds. At the six-round boundary every certified bit comes from the two retained words, which pass through the additions unchanged. The model with exact local transitions certifies the same bits as the bit-based division property on all instances examined.
"""
s = s[:a0] + abstract + s[a1:]
t = re.sub(r"\$[^$]*\$", " X ", abstract); t = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", t).replace("~", " ")
print("abstract words:", len(t.split()))

rep(r"""so by Lemma~\ref{lem:monobal} no bit-aligned cube gives a seven-round property on a single output bit, for independent round keys.""",
    r"""so by Lemma~\ref{lem:monobal} no bit-aligned cube gives a seven-round property on a single output bit, for independent round keys. Section~\ref{sec:r7lin} extends this to every nonzero linear combination of output bits.""")
rep(r"""A stronger goal is integral resistance in the sense of~\cite{hebborn2021}, a guarantee that covers all input subspaces of a given dimension and all nonzero linear combinations of output bits.""",
    r"""A stronger goal is integral resistance in the sense of~\cite{hebborn2021}, a guarantee that covers all input subspaces of a given dimension and all nonzero linear combinations of output bits. Section~\ref{sec:r7lin} establishes it for bit-aligned cubes after seven rounds; input subspaces that are not bit-aligned remain open.""")
rep(r"""\item The seven-round statement concerns bit-aligned cubes and single output bits. It says nothing about input sets that are not bit-aligned cubes, or about linear combinations of output bits.""",
    r"""\item The seven-round statement concerns bit-aligned cubes, for which it covers every nonzero linear combination of output bits. It says nothing about input sets that are not bit-aligned cubes. The zero entries of the matrices in Section~\ref{sec:r7lin} rest on the solver's answers, of which we checked a random sample with DRAT proofs.""")
rep(r"""Presence proofs separate ``no certificate'' from ``not balanced'': every bit that the experiments could not decide is unbalanced, and so is every output bit after seven rounds.""",
    r"""Presence proofs separate ``no certificate'' from ``not balanced'': every bit that the experiments could not decide is unbalanced, and after seven rounds so is every nonzero linear combination of output bits over every bit-aligned cube. The smallest certified six-round cube is proven minimal, and the algebraic degree of almost every output bit is known exactly.""")
rep(r"""Behind these results are three technical tools: the exact local rule for Dipper's ARX map (Lemma~\ref{lem:addret}), the standard free-final-round observation (Lemma~\ref{lem:free}), and presence proofs, which count trails under maximal key patterns (Section~\ref{sec:presence}).""",
    r"""Behind these results are four technical tools: the exact local rule for Dipper's ARX map (Lemma~\ref{lem:addret}), the standard free-final-round observation (Lemma~\ref{lem:free}), presence proofs, which count trails under maximal key patterns (Section~\ref{sec:presence}), and a last-round component lemma (Lemma~\ref{lem:component}), which turns the low-degree components of the GIFT S-box from an obstacle for counting into exact matrix entries.""")
open(P, "w").write(s); print("final2 applied")
