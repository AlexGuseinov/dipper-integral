"""Insert the linear-combination result (step27, step29) and the key-schedule
probe (step28) into paper.tex, with numbers computed from the result files."""
import glob, json, sys
P = "paper.tex"; s = open(P).read()
def rep(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:90]); s = s.replace(o, n)

recs = {}
for f in ["../results/step27_linear_combinations_final.json"]:
    for p, r in json.load(open(f)).items():
        good = r.get("invertible") and r.get("failures", 1) == 0
        if int(p) not in recs or (good and not (recs[int(p)].get("invertible") and recs[int(p)].get("failures", 1) == 0)):
            recs[int(p)] = r
inv = [p for p, r in recs.items() if r.get("invertible") and r.get("failures", 1) == 0]
allinv = len(inv) == 64
nblocks = sum(len(r["blocks"]) for r in recs.values() if r.get("invertible"))
maxblock = max((len(b["nodes"]) for r in recs.values() for b in r["blocks"]), default=1)
nrep = sum(r.get("block_repairs", 0) for r in recs.values() if r.get("invertible"))
nlem = sum(len(r.get("lemma_blocks") or [b for b in r["blocks"] if b.get("by_lemma")]) for r in recs.values() if r.get("invertible"))
ntr = sum(r.get("trails_checked", 0) for r in recs.values() if r.get("invertible"))
fails = sum(r.get("failures", 0) for r in recs.values() if r.get("invertible"))
assert fails == 0
d29 = json.load(open("../results/step29_drat_zero_entries.json"))["summary"]
assert d29["verified"] == d29["sampled"]
ks = json.load(open("../results/step28_keyschedule_probe.json"))
print("cubes invertible:", len(inv), "blocks:", nblocks, "max block:", maxblock, "repairs:", nrep, "trails:", ntr, "drat:", d29)

lemma = r"""
\begin{lemma}[Linear combinations]\label{lem:lincomb}
Let $v^{(0)},\dots,v^{(63)}$ be key patterns, and let $M$ be the $64\times64$ matrix over $\F$ whose entry $M_{l,j}$ is the number of monomial trails from $\mathbf 1_I$ to $e_j$ with key pattern $v^{(l)}$, modulo 2. If $M$ is invertible, then for every $\beta\neq0$ the function $\langle\beta,S^{(r)}\rangle$ is not balanced over $I$, nor over any $I'\subseteq I$, for independent round keys.
\end{lemma}
\begin{proof}
By Proposition~\ref{prop:mp} and linearity, the coefficient of $x^{\mathbf 1_I}k^{v^{(l)}}$ in $\langle\beta,S^{(r)}\rangle$ is $\sum_j M_{l,j}\beta_j=(M\beta)_l$. Since $M$ is invertible and $\beta\neq0$, some $(M\beta)_l$ equals~1, and the argument of Lemma~\ref{lem:presence} shows that the cube sum is not identically zero. The proof of Lemma~\ref{lem:monobal} applies to any output function.
\end{proof}

\begin{lemma}[Last-round component]\label{lem:component}
Let $f=g(z)$ depend on the state after $r$ rounds only through the input $z=S^{(r-1)}_{[n]}\oplus RK_{r,[n]}$ of one S-box $n$ of round $r$, and let $g_w$ denote the ANF coefficients of $g$. For a key pattern $V$ of the first $r-1$ rounds and a mask $u$ on the four input bits, let $c_V(u)$ be the coefficient of $x^{\mathbf 1_I}k^V$ in $\prod_{i\in u}S^{(r-1)}_{n,i}$. Then for every input position $t$ of the S-box, the coefficient of $x^{\mathbf 1_I}k^{V}k_{r,t}$ in $f$ is $\bigoplus_{u\neq0,\,t\notin u}g_{u\cup\{t\}}\,c_V(u)$.
\end{lemma}
\begin{proof}
Write $z_i=s_i\oplus k_{r,i}$ and expand $g(s\oplus k_r)=\bigoplus_w g_w\prod_{i\in w}(s_i\oplus k_{r,i})$. The terms whose only last-round key factor is $k_{r,t}$ arise from $w\ni t$ by choosing $k_{r,t}$ in the factor $i=t$ and $s_i$ in all others, which gives $s^{w\setminus\{t\}}k_{r,t}$. For $w=\{t\}$ this is $k_{r,t}$ alone, which does not contain $x^{\mathbf 1_I}$ because $|I|\ge1$.
\end{proof}
By Proposition~\ref{prop:mp}, $c_V(u)$ is the parity of the number of $(r-1)$-round trails with key pattern $V$ that end in the mask $u$ on S-box $n$.
"""
rep(r"""Lemma~\ref{lem:monobal} is the cipher-level counterpart of Lemma~\ref{lem:mono}.""",
    lemma.strip() + "\n" + r"""Lemma~\ref{lem:monobal} is the cipher-level counterpart of Lemma~\ref{lem:mono}.""")

sec = r"""\subsection{Seven rounds: linear combinations of output bits}\label{sec:r7lin}
An attacker may also sum a linear combination $\langle\beta,S^{(7)}\rangle$ of output bits. We show with Lemma~\ref{lem:lincomb} that no nonzero combination is balanced after seven rounds over any bit-aligned cube.

The matrix $M$ need not be computed in full. Let $G$ be the graph on the output bits with an edge $l\to j$ ($j\neq l$) whenever pattern $v^{(l)}$ has at least one trail to bit $j$. In a topological order of the strongly connected components of $G$, $M$ is block triangular, so $M$ is invertible if and only if every diagonal block is. A component with a single bit has the diagonal entry~1 of a presence proof. For each of the 64 cubes of dimension~63 we started from the 64 presence proofs of Section~\ref{sec:r7presence}. We then replaced the patterns of bits that lie on cycles of $G$ by other presence proofs with no trail to the rest of their cycle.

For the cube with constant bit~0, almost every pattern has trails to a common set of twelve output bits, all high bits of the two added words, and the cycles that remain are small. Their blocks were often singular, or their entries could not be counted, for a structural reason. Output bits 0 and~1 of the GIFT S-box sum to the component $1\oplus z_1\oplus z_0z_2$ of degree two in the S-box input $z$. Maximal patterns route the trails through last-round S-box inputs of weight three or four, where the two bits have equal coefficients, so the trail counts for the two bits always have the same parity. The added words cause the same effect, because bit $i$ of $X\add Y$ and the retained bit $Y_i$ share the linear term $Y_i$. Such a pair is separated by a pattern that uses the last round: a six-round presence proof for one bit $s_a$ of $S^{(6)}$, extended by a single last-round key bit $t$ such that $z_a$ is the only variable that forms a monomial with $z_t$ in the component in question. Where the trails of the new pattern to the block could be counted, we counted them. Where they could not, all bits of the block were output bits of one S-box of a retained word. For such a block Lemma~\ref{lem:component}, applied to each bit, gives every entry exactly from the ANF of the GIFT S-box and a few six-round trail counts $c_V(u)$, which are small because $V$ is a maximal pattern; we counted them and validated every trail. For output bits 0 and~1 and $V$ a six-round presence proof for $s_0$, for instance, the last-round key bit $t=1$ gives the row $(1,1)$ and $t=2$ gives the row $(0,1)$, since $z_1$ occurs in both bits only in $z_1$ and $z_0z_1$, while $z_2$ occurs in bit~0 only alone and in bit~1 in $z_2$ and $z_0z_2$. These two rows have determinant~1, whatever the old rows were. """ + (
    (r"""With these patterns every block became invertible for all 64 cubes. Over the 64 cubes, """ + str(nrep) + r""" rows inside blocks were replaced and """ + str(nlem) + r""" blocks were closed with Lemma~\ref{lem:component}; the final matrices have """ + str(nblocks) + r""" diagonal blocks of two to """ + str(maxblock) + r""" bits, all invertible.""") if allinv else
    (r"""With these patterns the matrix became invertible for """ + str(len(inv)) + r""" of the 64 cubes.""")) + r"""

The diagonal entries and the entries inside the blocks rest on trail counts, directly or through Lemma~\ref{lem:component}, and each of their """ + f"{ntr:,}".replace(",", r"\,") + r""" trails passed the independent check. The zero entries outside the blocks rest on ``no trail'' answers of the solver. For a random sample of """ + f"{d29['sampled']:,}".replace(",", r"\,") + r""" of these """ + f"{d29['pool']:,}".replace(",", r"\,") + r""" answers we re-solved the instance with an external CaDiCaL, produced a DRAT proof and verified it with \texttt{drat-trim}. All were verified. """ + (
    r"""By Lemma~\ref{lem:lincomb}, no nonzero linear combination of the output bits of $S^{(7)}$ is balanced over any bit-aligned cube, for independent round keys, and by Lemma~\ref{lem:free} the same holds for $T^{-1}(S^{(8)})$. This is the integral-resistance property of~\cite{hebborn2021} after seven rounds, restricted to bit-aligned cubes."""
    if allinv else
    r"""For these cubes, by Lemma~\ref{lem:lincomb}, no nonzero linear combination of the output bits of $S^{(7)}$ is balanced over any sub-cube.""") + "\n\n"
rep(r"""\subsection{Where the balanced bits come from}""", sec + r"""\subsection{Where the balanced bits come from}""")

odd6 = ks["128|6"]["odd"]; even6 = ks["128|6"]["even"]; cap6 = ks["128|6"]["capped"]
odd7 = ks["128|7"]["odd"] + ks["96|7"]["odd"]; cnt7 = sum(ks[k]["odd"] + ks[k]["even"] for k in ("128|7", "96|7"))
tot7 = sum(ks[k]["odd"] + ks[k]["even"] + ks[k]["capped"] for k in ("128|7", "96|7"))
ksp = r"""\paragraph{The real key schedule.} All presence results assume independent round keys. To test whether they carry over to the key schedules, we extended \MPEL{} by the key schedule: the master-key bits are variables, each round key is a COPY of the low half of the key state, and the key update is modelled by wiring, the key-schedule S-boxes and the round constants. A trail then carries a master-key monomial. For the cube with constant bit~0 and six output bits we sampled master-key monomials and counted their trails. With the 128-bit key at six rounds, """ + str(odd6) + r""" of the countable coefficients were odd and """ + str(even6) + r""" even, and """ + str(cap6) + r""" exceeded the cap of 2000 trails. At seven rounds, """ + str(tot7 - cnt7) + r""" of """ + str(tot7) + r""" samples for the two key sizes exceeded the cap, and none of the others was odd. Each master-key bit enters several round keys, so trails appear in pairs that differ only in where a key bit is used, and they cancel. Proving presence with the key schedule needs a different technique, such as the divide-and-conquer monomial prediction used in cube attacks~\cite{hu2020mp}. We leave it open.

"""
rep(r"""\paragraph{Limitations.}""", ksp + r"""\paragraph{Limitations.}""")
open(P, "w").write(s)
print("inserted")
