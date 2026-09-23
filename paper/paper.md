---
abstract: |
  Dipper is a 64-bit lightweight block cipher whose round combines the
  GIFT S-box and bit permutation with two 16-bit modular additions on
  half of the state. Its integral resistance was supported only by
  experiments with a few random keys, which we replace by
  key-independent results. We model monomial trails through
  reduced-round Dipper as SAT instances with exact local transitions,
  including a rule for the modular additions derived from the
  Braeken--Semaev characterisation, and back the results by DRAT proofs
  and independently checked trails. The published five-round properties
  hold for all round keys, and six-round properties exist; the smallest
  certified six-round cube, of size $2^{60}$, is minimal within the
  model. At seven rounds no bit-aligned cube is certified. Presence
  proofs, i.e. key monomials with an odd number of trails, show that
  this is exact for independent round keys and, more strongly, that no
  nonzero linear combination of output bits is balanced after seven
  rounds over any bit-aligned cube. They also show that 46 bits whose
  sums stayed zero in thousands of random-key trials are not balanced,
  and they determine the algebraic degree exactly in 1843 of 1856
  (cipher, round, bit) cases. Replacing the two modular additions by
  XOR, or removing them, extends the longest certified property from six
  to nine and ten rounds. At the six-round boundary every certified bit
  comes from the two retained words, which pass through the additions
  unchanged. On all instances examined, the exact model certifies the
  same bits as the bit-based division property.
author:
- |
  Ali Huseynli[^1]\
  [`ali.huseynli@student.aztu.edu.az`](mailto:ali.huseynli@student.aztu.edu.az)
- |
  Yadigar Imamverdiyev\
  [`yadigar.imamverdiyev@aztu.edu.az`](mailto:yadigar.imamverdiyev@aztu.edu.az)
- |
  Jalal Alizadeh\
  [`jalal.alizadeh@aztu.edu.az`](mailto:jalal.alizadeh@aztu.edu.az)
bibliography: refs.bib
date: |
  Department of Cybersecurity, Faculty of Information Technologies and
  Telecommunications,\
  Azerbaijan Technical University, Baku AZ1073, Azerbaijan
title: |
  Certified Integral Properties of the Dipper Block Cipher:\
  Monomial-Trail Analysis and the Role of the Half-State Modular
  Addition
---

**Keywords:** integral cryptanalysis; monomial prediction; division
property; modular addition; SAT; lightweight block cipher

# Introduction

Integral (square, saturation) cryptanalysis [@knudsen2002integral] looks
for a set of chosen plaintexts, typically an affine subspace called a
*cube*, over which some output bit sums to zero independently of the
key. The division property [@todo2015] and its bit-based
versions [@todo2016bit; @xiang2016milp] turned the search for such
properties into a propagation problem for MILP or SAT solvers. Monomial
prediction [@hu2020mp], which Hu et al. proved equivalent to the
three-subset division property without unknown subset [@hao2020], gives
the exact algebraic view: a cube sum vanishes if and only if certain
monomial coefficients are zero.

Modular addition is well understood in isolation. Its differential and
linear behaviour is described exactly by Lipmaa and Moriai [@lipmaa2001]
and by Wallén [@wallen2003], and its algebraic normal form by Braeken
and Semaev [@braeken2005]. Integral analysis of ciphers that mix modular
addition with S-boxes is less developed. Division-property models for
ARX designs [@sun2016arx; @sun2017sat] target pure ARX ciphers such as
SPECK [@simonspeck2015], in which the addition is the only nonlinear
operation. In a hybrid round the addition interacts with a small S-box
and a bit permutation. It is then not obvious how much the addition
contributes to integral resistance, or which part of the state keeps an
integral property longest.

Dipper [@dipper2026] is a 64-bit hybrid SPN--ARX cipher with 96- and
128-bit keys and 28 rounds, proposed in our previous work. Each round
applies a full-state key addition, sixteen GIFT S-boxes [@gift2017],
four word rotations, two 16-bit modular additions over half of the state
and the GIFT-64 bit permutation. The design paper evaluates
differential, linear and impossible-differential resistance with MILP
and CP-SAT models. Its integral evaluation, however, is *experimental*:
one 16-bit word is saturated, the sums are tested for a few random keys,
and distinguishers are reported for up to five rounds. Such an
evaluation has two weaknesses. A sum that is zero for a few random keys
need not be zero for all keys, and a search limited to word-saturated
cubes says nothing about other cubes.
Section [6](#sec:results){reference-type="ref" reference="sec:results"}
shows that the first weakness is not hypothetical for Dipper: with 80
trials, two bits look balanced that are not.

#### Research questions.

We ask three questions. (Q1) Which integral properties of reduced-round
Dipper hold for *all* round keys, and how far do they extend over *all*
bit-aligned cubes? (Q2) What exactly do the two half-state additions
contribute, and why do some parts of the state stay balanced longer than
others? (Q3) Does an exact treatment of the modular addition, made
possible by the Hu--Yap characterisation [@huyap2024], certify more than
the conventional division property?

#### Contributions.

1.  **Key-independent certificates and a complete search within the
    model (Q1).** We certify the published five-round properties for all
    round keys, find six-round properties (nine balanced bits with a
    $2^{63}$ cube; six bits with a cube of size $2^{60}$, the smallest
    cube that the model certifies), and show that no bit-aligned cube
    certifies a single output bit at seven rounds in the model. The
    monotonicity lemma (Lemma [3](#lem:mono){reference-type="ref"
    reference="lem:mono"}) reduces this statement to the 64 cubes of
    dimension 63. Presence proofs
    (Section [4.3](#sec:presence){reference-type="ref"
    reference="sec:presence"}) show that this answer is exact for
    independent round keys: for each of the 64 cubes of dimension 63,
    every output bit is unbalanced after seven rounds, so by
    Lemma [6](#lem:monobal){reference-type="ref"
    reference="lem:monobal"} no bit-aligned cube gives a seven-round
    property on a single output bit, for independent round keys.
    Section [6.4](#sec:r7lin){reference-type="ref"
    reference="sec:r7lin"} extends this to every nonzero linear
    combination of output bits. The boundary results come with checkable
    artifacts (Section [5](#sec:validation){reference-type="ref"
    reference="sec:validation"}): DRAT proofs verified by `drat-trim`
    for the certificates, the degree bounds and every solver answer
    behind the presence proofs, including proofs that each trail
    enumeration is complete, and monomial trails validated by a checker
    that does not use the SAT encoding. The artifacts check the solver,
    not the CNF generator, whose local rules we verified exhaustively
    for small word sizes.

2.  **The role of the modular addition (Q2).** In a controlled ablation,
    replacing the two additions by XOR or removing them extends the
    longest certified property from six to nine and ten rounds. At the
    six-round boundary every certified bit comes from the retained
    operands, the two words that feed the additions but pass through
    them unchanged. We relate this to
    Lemma [2](#lem:deg){reference-type="ref" reference="lem:deg"}, which
    states that output bit $i$ of an addition has degree exactly $i+1$,
    and to the algebraic degree of every output bit and round. We
    determine it exactly in 1843 of 1856 cases, by matching presence
    proofs to the certified upper bounds.

3.  **Model comparison and tightness (Q3).** The monomial-trail
    existence model with exact local transitions ([MP-EL]{.sans-serif}),
    a gate-level monomial model and the conventional bit-based division
    property certify the same bits on every instance we examined. We
    explain part of this structurally. We then compare certificates with
    experiment on 112 (cube, round) instances and use presence proofs to
    decide every bit that experiment leaves open. The 46 bits that
    stayed zero in every trial without being certified are all
    unbalanced. On these instances the certificates are therefore
    exactly the balanced bits, and a model that counts trails could not
    certify more.

Behind these results are four technical tools: the exact local rule for
Dipper's ARX map (Lemma [1](#lem:addret){reference-type="ref"
reference="lem:addret"}), the standard free-final-round observation
(Lemma [4](#lem:free){reference-type="ref" reference="lem:free"}),
presence proofs, which count trails under maximal key patterns
(Section [4.3](#sec:presence){reference-type="ref"
reference="sec:presence"}), and a last-round component lemma
(Lemma [8](#lem:component){reference-type="ref"
reference="lem:component"}). The lemma formalises, for Dipper, the
last-round choice of key monomials of Hebborn et al. [@hebborn2021]; we
use it to turn the low-degree components of the GIFT S-box from an
obstacle for counting into exact matrix entries.
Sections [9](#sec:keyrec){reference-type="ref" reference="sec:keyrec"}
and [10](#sec:erratum){reference-type="ref" reference="sec:erratum"}
contain secondary material: a partial-key filtering procedure and two
corrections to the key-schedule description of [@dipper2026]. Code,
data, proofs and scripts are available at
<https://github.com/AlexGuseinov/dipper-integral>.

#### Scope of the claims.

A certificate proves that a cube sum is zero for all round keys. The
absence of a certificate proves nothing about the cipher: it only means
that the model contains a trail. Where we claim more, we use presence
proofs: an odd number of trails for one key monomial proves that the
cube sum is a nonzero polynomial in the round keys, so that the bit is
not balanced. With presence proofs for all 64 cubes of dimension 63, our
seven-round statement holds for Dipper with independent round keys, not
only within the model. We do not claim it for round keys produced by the
key schedule. For cipher outputs we call a degree exact only when a
presence proof matches the certified upper bound, and otherwise report
the interval between the two.

#### Organisation.

Section [2](#sec:related){reference-type="ref" reference="sec:related"}
reviews related work and Section [3](#sec:prelim){reference-type="ref"
reference="sec:prelim"} introduces the notation and background.
Section [4](#sec:models){reference-type="ref" reference="sec:models"}
gives the local rules and the structural lemmas, and
Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"} validates them.
Section [6](#sec:results){reference-type="ref" reference="sec:results"}
reports the certified properties of Dipper, and
Section [7](#sec:ablation){reference-type="ref"
reference="sec:ablation"} studies the role of the addition.
Section [8](#sec:tightness){reference-type="ref"
reference="sec:tightness"} compares models and experiment.
Sections [9](#sec:keyrec){reference-type="ref" reference="sec:keyrec"}
and [10](#sec:erratum){reference-type="ref" reference="sec:erratum"}
cover key filtering and the key-schedule corrections.
Section [11](#sec:discussion){reference-type="ref"
reference="sec:discussion"} discusses implications and limitations.

# Related work {#sec:related}

#### Integral and higher-order differential cryptanalysis.

Integral attacks go back to the Square attack [@square1997]. They were
formalised as integral cryptanalysis by Knudsen and
Wagner [@knudsen2002integral] and as the saturation attack by
Lucks [@lucks2001], and extended to bit-oriented ciphers by Z'aba et
al. [@zaba2008]. The underlying algebra is that of higher-order
derivatives [@lai1994; @knudsen1994]: a cube sum is a derivative whose
order is the cube dimension, and it vanishes whenever the algebraic
degree is smaller than that order. Canteaut and Videau [@canteaut2002]
and Boura, Canteaut and De Cannière [@boura2011] bounded the degree of
iterated constructions. The cube attack of Dinur and Shamir [@dinur2009]
applies the same algebra to key recovery.

#### Division property and monomial prediction.

Todo introduced the division property [@todo2015] and used it to break
full MISTY1 [@todo2015misty]. The bit-based division
property [@todo2016bit] and its MILP modelling [@xiang2016milp] made
automated search practical, and Eskandari et al. [@eskandari2018]
provide a SAT-based tool and a table of results that we use as a
benchmark. In stream ciphers the division property underlies modern cube
attacks [@todo2017cube; @wang2018cube]. The three-subset division
property [@huwang2019] and its variant without unknown subset [@hao2020]
remove the imprecision of the two-subset version; Hu et al. [@hu2020mp]
showed that the latter is equivalent to monomial prediction. Complex
linear layers need dedicated models [@hu2020linear; @zhang2019], and the
precision of the division property can be increased by propagating
through larger S-box layers [@derbez2020]. Hebborn, Leander and Udovenko
give a mathematical treatment of the conventional and the perfect
division property [@hebborn2023math].

#### Modular addition.

Sun, Wang and Wang [@sun2016arx] gave the first MILP model of the
bit-based division property for ARX ciphers, based on a gate-level
decomposition of the carry chain, and Sun et al. [@sun2017sat] moved it
to SAT. Hu and Yap [@huyap2024] observed that the characterisation of
Braeken and Semaev [@braeken2005] yields a perfect local
monomial-prediction model for modular addition.
CLAASP-MP [@bellini2026claaspmp] integrates such models into a general
MILP framework. We use this characterisation for the specific map
$(x,y)\mapsto(x\boxplus y,y)$ of Dipper and derive from it a degree
statement.

#### Security guarantees and degree lower bounds.

Finding an integral distinguisher answers an upper-bound question.
Proving that *no* integral distinguisher exists requires exact
information, such as lower bounds on the degree. Hebborn et
al. developed degree lower bounds [@hebborn2020] and strong security
guarantees against integral distinguishers [@hebborn2021] for ciphers in
which a key is added to the full state; Dipper adds a full-state key
before every S-box layer and meets this assumption, but its round also
contains a nonlinear ARX layer
(Section [11](#sec:discussion){reference-type="ref"
reference="sec:discussion"}). Zeng and Tian [@zeng2024] extended the
guarantees to ciphers without such a whitening key, such as SIMON and
Simeck. Peng et al. [@peng2026] identified *interfering monomials*,
which make trail counts even for badly chosen key monomials, and avoided
them by a careful choice of the key monomials. Wang, Hadipour and
Gerhalter [@wang2026split] search for key-independent and weak-key
integral combinations beyond single output bits. Beierle et
al. [@beierle2025] treated key whitening by modular addition, and
Gerhalter and Eichlseder [@gerhalter2026] complex linear layers. In all
these works the proof of *presence* of a monomial, by an odd number of
trails, is the basic step;
Section [4.3](#sec:presence){reference-type="ref"
reference="sec:presence"} applies it to Dipper.

#### Integral key recovery.

Hadipour and Eichlseder [@hadipour2022], for example, study key recovery
built on monomial prediction.

#### Positioning.

We do not propose a new general framework. Our contribution is the
analysis of one hybrid cipher, which consists of exact rules for its
particular ARX shape, key-independent certificates with checkable
artifacts, a search over all bit-aligned cubes within the model, a model
comparison, an ablation, and a degree-based explanation.

# Preliminaries {#sec:prelim}

This section fixes notation and recalls the algebraic facts on which the
analysis rests. The material is standard, but we state it in the form in
which we use it, because the difference between what a model *proves*
and what it merely *fails to exclude* runs through the whole paper.

## Notation

Vectors in $\mathbb{F}_2^n$ are written $u=(u_0,\dots,u_{n-1})$ with
$u_0$ the least significant bit. We identify $u$ with the integer
$\operatorname{val}(u)=\sum_i u_i2^i$ whenever we do arithmetic with it.
The Hamming weight is $\operatorname{wt}(u)=\#\{i:u_i=1\}$, and $e_i$ is
the $i$-th unit vector. We write $u\preceq v$ if $u_i\le v_i$ for all
$i$, so that $u$ is a sub-mask of $v$; $u\vee v$ and $u\wedge v$ are the
bitwise OR and AND. For a set $I\subseteq\{0,\dots,n-1\}$, $\mathbf 1_I$
is its indicator vector. The symbol $\oplus$ denotes XOR, and $\boxplus$
addition modulo $2^n$, where $n$ is clear from the context. $x\lll s$ is
a left rotation of an $n$-bit word.

## Boolean functions, ANF and degree

Every Boolean function $f:\mathbb{F}_2^n\to\mathbb{F}_2$ has a unique
algebraic normal form (ANF)
$$f(x)=\bigoplus_{u\in\mathbb{F}_2^n} a_u\,x^u,\qquad x^u=\prod_{i:u_i=1}x_i,\qquad a_u\in\mathbb{F}_2.$$
The coefficients follow from the truth table by the Möbius transform
$a_u=\bigoplus_{v\preceq u}f(v)$, which costs $n2^n$ operations. The
*algebraic degree* $\deg f$ is the largest $\operatorname{wt}(u)$ with
$a_u=1$. For a vectorial function $F=(f_0,\dots,f_{m-1})$ and
$v\in\mathbb{F}_2^m$ we write $F^v=\prod_{j:v_j=1}f_j$, which is again a
Boolean function. Two facts are used repeatedly: $x_i^2=x_i$, so
products of monomials are monomials of the union of their supports; and
a nonconstant component of a permutation of $\mathbb{F}_2^n$ has degree
at most $n-1$, since $\bigoplus_x f(x)$ equals the coefficient
$a_{\mathbf 1}$ and is zero for a balanced function.

## The Dipper cipher

Figure [1](#fig:round){reference-type="ref" reference="fig:round"} shows
one round.

<figure id="fig:round">

<figcaption>One Dipper round. The shaded boxes are the <em>added</em>
words; <span class="math inline"><em>B</em></span> and <span
class="math inline"><em>D</em></span> are the <em>retained</em> words,
used as addends and passed on unchanged. The ARX layer <span
class="math inline"><em>M</em></span> consists of the rotations and the
two additions. There is no key addition after the last
round.</figcaption>
</figure>

The state is $S=A\|B\|C\|D$ with 16-bit words, $A=S[63{:}48]$,
$D=S[15{:}0]$ and bit 0 the least significant. For $r=1,\dots,28$,
$$S^{(r)} = T\big(S^{(r-1)}\oplus RK_r\big),\qquad T = P\circ M\circ \mathrm{SC},$$
with $S^{(0)}$ the plaintext and $S^{(28)}$ the ciphertext.
$\mathrm{SC}$ applies the GIFT S-box to the sixteen nibbles. $M$ first
rotates $A,B,C,D$ left by $1,4,7,11$ and then sets
$$A\gets A\boxplus B,\qquad C\gets C\boxplus D,$$ so $B$ and $D$ are
used as addends and pass through the additions unchanged (after their
rotation). We call $A,C$ the *added* words and $B,D$ the *retained*
words of the ARX layer. $P$ is the GIFT-64 bit permutation
$P(i)=4\lfloor i/16\rfloor+16\big((3\lfloor (i\bmod 16)/4\rfloor+(i\bmod4))\bmod4\big)+(i\bmod4)$,
which moves bit $i$ to position $P(i)$. Three structural features matter
for integral analysis. The key is added to the *full* state at the start
of every round. $T$ is a public permutation. There is no key addition
after the last round.

For the ablation we define two analysis variants, which are not ciphers
anyone proposes. $\mathrm{Dipper}^{\oplus}$ replaces both additions by
XOR, and $\mathrm{Dipper}^{\varnothing}$ removes them while keeping the
rotations. Throughout, the round keys $RK_1,\dots,RK_r$ are treated as
*independent* variables; a statement that holds for all such sequences
holds in particular for the sequences produced by either key schedule.

## Cubes and integral properties

::: definition
**Definition 1** (Cube, balanced bit). Let $I\subseteq\{0,\dots,63\}$
and $c\in\mathbb{F}_2^{64}$ with $c_i=0$ for $i\in I$. The *cube*
$\mathcal C_I(c)$ is the set of the $2^{|I|}$ plaintexts that take all
values on the positions in $I$ (the active bits) and agree with $c$
elsewhere (the constant bits). For an $r$-round state bit $S^{(r)}_j$,
the *cube sum* is $\bigoplus_{x\in\mathcal C_I(c)}S^{(r)}_j(x)$. The bit
is *balanced over $I$ after $r$ rounds* if the cube sum is zero for
every constant $c$ and every sequence of round keys.
:::

All cubes in this paper are *bit-aligned*: they are spanned by unit
vectors. Affine subspaces in other bases, non-affine input sets and
output functions other than a single bit are outside the scope of our
search.

Viewing $S^{(r)}_j$ as a polynomial in the plaintext bits $x$ and the
key bits $k$, and substituting the constants $c_i$ for the plaintext
bits outside $I$ after summation, $$\label{eq:cubesum}
\bigoplus_{x_I\in\mathbb{F}_2^{|I|}} S^{(r)}_j(x,k)\;=\;\bigoplus_{u\succeq \mathbf 1_I,\;v} a_{u,v}\,x^{u\oplus\mathbf 1_I}\,k^{v},$$
because summing a monomial $x^u$ over the cube leaves
$x^{u\oplus\mathbf 1_I}$ if $u\succeq\mathbf 1_I$ and zero otherwise.
Hence the bit is balanced over $I$ *if and only if* every coefficient
$a_{u,v}$ with $u\succeq\mathbf 1_I$ vanishes. A cube sum is a
derivative of order $|I|$ [@lai1994]. In particular, if
$\deg_x S^{(r)}_j<|I|$ the bit is balanced over every cube of dimension
$|I|$, which links integral properties to degree bounds
(Section [7.2](#sec:degree){reference-type="ref"
reference="sec:degree"}). The 64-dimensional cube, i.e. the full
codebook, is balanced for every bit of every permutation. It is trivial
and excluded.

## Monomial trails

Let $F=F_r\circ\dots\circ F_1$ be a composition of vectorial functions.
For a single function $G$ and masks $u,v$, write $G[u\to v]=1$ if $x^u$
occurs in the ANF of $G^v$ and $0$ otherwise. A *monomial trail* from
$u_0$ to $u_r$ is a sequence $u_0\to u_1\to\dots\to u_r$ with
$F_t[u_{t-1}\to u_t]=1$ for all $t$.

::: {#prop:mp .proposition}
**Proposition 1** (Hu et al. [@hu2020mp]). *The coefficient of $x^{u_0}$
in $F^{u_r}$ equals the number of monomial trails from $u_0$ to $u_r$
modulo 2.*
:::

The proposition gives two sound tests of opposite strength. If *no*
trail exists, the coefficient is zero; this is the test we use, and it
only needs a satisfiability check. If trails exist, the coefficient is
their parity. Deciding it requires counting, and trails can cancel in
pairs. The following toy example shows the gap between the two tests.

::: {#ex:cancel .example}
**Example 1** (Cancellation). Let $F_1(x_1,x_2)=(x_1x_2,\;x_1x_2)$ and
$F_2(y_1,y_2)=y_1\oplus y_2$. Then $F=F_2\circ F_1=0$, so the sum over
the cube $\{x_1,x_2\}$ is zero. From $x^{11}=x_1x_2$ to the output there
are two trails, $11\to10\to1$ and $11\to01\to1$, because $x_1x_2$ occurs
in both $y_1$ and $y_2$ and both occur in $F_2$. An existence test finds
a trail and cannot certify the property. The parity test counts two
trails and certifies it.
:::

For keyed functions we treat each key bit as a variable. The
key-addition layer $s'=s\oplus k$ satisfies
$s'^w=\bigoplus_{u\preceq w}s^uk^{w\oplus u}$. A trail step $u\to w$ is
therefore possible exactly when $u\preceq w$, and different steps attach
different key monomials $k^{w\oplus u}$. Trails with different key
monomials never cancel each other; only trails with the same key
monomial can.

## The bit-based division property

The conventional (two-subset) bit-based division property [@todo2016bit]
describes a multiset $\mathbb X\subseteq\mathbb{F}_2^n$ by a set
$\mathbb K$ of vectors: $\mathbb X$ has property
$\mathcal D^n_{\mathbb K}$ if $\bigoplus_{x\in\mathbb X}x^u=0$ for every
$u$ such that $u\not\succeq k$ for all $k\in\mathbb K$. A cube with
active set $I$ has $\mathbb K=\{\mathbf 1_I\}$. Propagation rules map
$\mathbb K$ through each operation, and bit $j$ is balanced if $e_j$ is
not reachable. Key addition leaves the property unchanged. For an S-box,
$k\to v$ is a *division trail* if some $u\succeq k$ has $S[u\to v]=1$.
The rules for COPY, AND and XOR gates are those
of [@todo2016bit; @xiang2016milp]. BDP is sound in the same direction as
the existence test above. Like that test, it cannot see cancellations,
and it can be less precise still. Precision is improved by the
three-subset division property [@huwang2019] and made exact by its
variant without unknown subset [@hao2020], which is equivalent to
monomial prediction [@hu2020mp].

## SAT encodings and checkable answers

Both tests become satisfiability problems once every mask bit is a
Boolean variable and every local relation is written as clauses. Each
clause excludes one forbidden assignment of the variables of a small
component. The solver then answers one of two ways. If the formula is
*unsatisfiable* (UNSAT), no trail exists and the bit is certified; a
DRAT proof [@drattrim2014] records the solver's reasoning, and an
independent checker such as `drat-trim` can replay it. If the formula is
*satisfiable* (SAT), the solver returns an assignment, from which we
read off a candidate trail and verify it layer by layer against the
local rules, without using the clauses. We use
CaDiCaL [@cadical2020; @cadical2024] through PySAT [@pysat2018] for the
search and an external CaDiCaL binary for proof generation.

# Models {#sec:models}

## Local propagation rules

#### Key addition.

A step $u\to w$ is allowed iff $u\preceq w$. Under BDP the key addition
is transparent.

#### S-box.

For the GIFT S-box we compute $S[u\to v]$ for all $u,v\in\mathbb{F}_2^4$
by the Möbius transform. Of the 256 pairs, 68 are nonzero. The BDP table
has 170 transitions.

#### Modular addition with retained operand.

Braeken and Semaev [@braeken2005], and Hu and Yap [@huyap2024] in the
cryptanalytic setting, show that for $z=x\boxplus y$ on $n$ bits the
monomial $x^ay^b$ occurs in $z^w$ if and only if
$\operatorname{val}(a)+\operatorname{val}(b)=\operatorname{val}(w)$ over
the integers. Dipper's ARX map also outputs the addend. The following
lemma gives the exact rule for that shape.

::: {#lem:addret .lemma}
**Lemma 1**. *Let $F(x,y)=(x\boxplus y,\,y)$ on $n$-bit words. Then
$[x^a y^b]\,(x\boxplus y)^w y^c = 1$ if and only if
$\operatorname{val}(w)\ge\operatorname{val}(a)$ and $b = b'\vee c$,
where $b'$ is the word with
$\operatorname{val}(b')=\operatorname{val}(w)-\operatorname{val}(a)$.*
:::

::: proof
*Proof.* By the Braeken--Semaev characterisation,
$(x\boxplus y)^w=\sum_{\operatorname{val}(a')+\operatorname{val}(b')=\operatorname{val}(w)}x^{a'}y^{b'}$.
Multiplying by $y^c$ and using $y_i^2=y_i$ gives
$\sum x^{a'}y^{b'\vee c}$. The coefficient of $x^ay^b$ is the parity of
$\#\{b' : \operatorname{val}(a)+\operatorname{val}(b')=\operatorname{val}(w),\ b'\vee c=b\}$.
The equation determines $b'$ uniquely, and $b'$ exists iff
$\operatorname{val}(w)\ge\operatorname{val}(a)$. ◻
:::

::: {#ex:add .example}
**Example 2**. For $n=2$, the high output bit of $z=x\boxplus y$ is
$z_1=x_1\oplus y_1\oplus x_0y_0$. Its monomials correspond to the pairs
$(\operatorname{val}(a),\operatorname{val}(b))\in\{(2,0),(0,2),(1,1)\}$,
which are exactly the solutions of
$\operatorname{val}(a)+\operatorname{val}(b)=2=\operatorname{val}(e_1)$.
The monomial $x_0y_0$ comes from the carry, and its degree $2=i+1$
anticipates Lemma [2](#lem:deg){reference-type="ref"
reference="lem:deg"} below. For the retained version,
$z_1y_0=x_1y_0\oplus y_1y_0\oplus x_0y_0$. With $w=e_1$ and $c=e_0$,
Lemma [1](#lem:addret){reference-type="ref" reference="lem:addret"}
predicts the monomials $x^ay^{b'\vee e_0}$ for the same three pairs,
i.e. $x_1y_0$, $y_1y_0$ and $x_0y_0$, in agreement with the direct
computation.
:::

The same characterisation gives the exact degree of each output bit of
the addition. Lemma [2](#lem:deg){reference-type="ref"
reference="lem:deg"} is an elementary consequence of [@braeken2005]. We
state it because it drives the mechanism of
Section [7.2](#sec:degree){reference-type="ref" reference="sec:degree"}.

::: {#lem:deg .lemma}
**Lemma 2** (Degree of an addition bit). *Let $z=x\boxplus y$ on $n$-bit
words. For $0\le i<n$, the output bit $z_i$ has algebraic degree exactly
$i+1$ as a Boolean function of the $2n$ input bits.*
:::

::: proof
*Proof.* Take $w=e_i$, i.e. $\operatorname{val}(w)=2^i$. The monomial
$x^ay^b$ occurs in $z_i$ iff
$\operatorname{val}(a)+\operatorname{val}(b)=2^i$, and it has degree
$\operatorname{wt}(a)+\operatorname{wt}(b)$. Every carry in the binary
addition of $a$ and $b$ turns two ones into a single one in the next
position, so
$\operatorname{wt}(a)+\operatorname{wt}(b)=\operatorname{wt}(a+b)+c(a,b)$,
where $c(a,b)$ is the number of carries (equivalently, by Kummer's
theorem [@kummer1852], $c(a,b)$ is the 2-adic valuation of
$\binom{a+b}{a}$). Here $\operatorname{wt}(a+b)=1$, and carries can
occur only at positions $0,\dots,i-1$, so the degree is at most $i+1$.
The pair $a=1$, $b=2^i-1$ produces $i$ carries and attains $i+1$. ◻
:::

::: {#cor:round .corollary}
**Corollary 1**. *In one Dipper round, let $d$ be an upper bound on the
degree of the round input. Every bit of the retained words after the ARX
layer is an S-box output bit and has degree at most $3d$. Bit $i$ of an
added word is a polynomial of degree $i+1$ in S-box output bits, so its
degree is at most $\min\{3d(i+1),63\}$. Only bit 0 of an added word is
linear in the S-box outputs.*
:::

Corollary [1](#cor:round){reference-type="ref" reference="cor:round"}
gives upper bounds; it does not state which degrees are attained.

#### Encoding.

In the SAT model the equation
$\operatorname{val}(a)+\operatorname{val}(b')=\operatorname{val}(w)$ is
encoded bitwise with auxiliary carries, $a_i+b'_i+q_i=w_i+2q_{i+1}$,
$q_0=q_n=0$. These are carries of the exponent integers, not the
cipher's data carries. The pair $(a,w)$ determines $b'$ and $q$, so each
trail has exactly one extension to the auxiliary variables.

#### The three models.

[MP-EL]{.sans-serif} (monomial-trail existence model with exact local
transitions) uses the S-box table and
Lemma [1](#lem:addret){reference-type="ref" reference="lem:addret"}. Its
local relations are exact, but its global test is trail *existence*, not
trail parity, so it cannot see cancellations of the kind in
Example [1](#ex:cancel){reference-type="ref" reference="ex:cancel"}. For
comparison, [MP-circuit]{.sans-serif} models the addition as a
ripple-carry circuit, $s_i=x_i\oplus y_i\oplus c_i$ and
$c_{i+1}=x_iy_i\oplus(x_i\oplus y_i)c_i$, with explicit COPY gates,
including the copy of $y$ that forms the retained output. It uses the
monomial gate rules (COPY: $u=\bigvee v_j$; AND: $u_1=u_2=v$; XOR:
$v=u_1+u_2$). [BDP]{.sans-serif} uses the same circuit with the
division-property rules (COPY: $u=\sum v_j$; AND: $v=u_1\vee u_2$) and
the BDP S-box table.

## Round model, soundness and structural lemmas

One round is modelled as the key addition, sixteen S-box relations, the
word rotations (wiring), the two addition relations and the bit
permutation (wiring). The input mask is fixed to $\mathbf 1_I$ and the
output mask after $r$ rounds to $e_j$. Each output bit is an incremental
query under assumptions.

::: {#prop:sound .proposition}
**Proposition 2** (Soundness). *If [MP-EL]{.sans-serif} (or
[BDP]{.sans-serif}) is unsatisfiable for $(I,r,j)$, then bit $j$ of
$S^{(r)}$ is balanced over $I$: the cube sum is zero for every constant
and every sequence of round keys, and in particular under both Dipper
key schedules.*
:::

::: proof
*Proof.* Every local relation contains all transitions with nonzero
coefficient. By Proposition [1](#prop:mp){reference-type="ref"
reference="prop:mp"}, every nonzero coefficient $a_{u,v}$ with
$u\succeq\mathbf 1_I$
in [\[eq:cubesum\]](#eq:cubesum){reference-type="eqref"
reference="eq:cubesum"} therefore has at least one trail starting from
$u$. Such a trail first passes the key addition to some
$w\succeq u\succeq\mathbf 1_I$. Since $\mathbf 1_I\preceq w$ is also a
valid key-addition step, the model, whose input mask is exactly
$\mathbf 1_I$, contains a trail too. For [BDP]{.sans-serif} the
statement is the standard soundness of division-property
propagation [@todo2016bit; @xiang2016milp]. The round keys are
independent variables and the constants merge with $RK_1$, which gives
the claimed generality. ◻
:::

::: {#lem:mono .lemma}
**Lemma 3** (Monotonicity). *In [MP-EL]{.sans-serif}, if $I\subseteq I'$
and $(I,r,j)$ has no trail, then $(I',r,j)$ has no trail. Consequently,
if no bit-aligned cube of dimension 63 is certified for output bit $j$
after $r$ rounds, no bit-aligned cube of any dimension $\le63$ is.*
:::

::: proof
*Proof.* The first operation is the key addition, so the masks reachable
from $\mathbf 1_I$ after it are $\{w\succeq\mathbf 1_I\}$. This set
contains $\{w\succeq\mathbf 1_{I'}\}$, and all later constraints are
identical. Every cube of dimension at most 63 lies inside some cube of
dimension 63. ◻
:::

::: {#lem:free .lemma}
**Lemma 4** (Free final round). *If bit $j$ of $S^{(r)}$ is balanced
over $I$ and $|I|\ge1$, then bit $j$ of $T^{-1}(S^{(r+1)})$ is balanced
over $I$.*
:::

::: proof
*Proof.* $T^{-1}(S^{(r+1)})=S^{(r)}\oplus RK_{r+1}$, and the constant
$RK_{r+1}$ cancels over the even number $2^{|I|}$ of terms. ◻
:::

Lemma [4](#lem:free){reference-type="ref" reference="lem:free"} uses a
different output test: the ciphertext is first passed through the public
map $T^{-1}$. It gives no information about $RK_{r+1}$. We report round
counts for $S^{(r)}$ and state the $(r{+}1)$-round extension separately.

::: {#rem:percube .remark}
*Remark 1* (Degree bounds versus cubes). A bound $\deg_x S^{(r)}_j\le62$
certifies bit $j$ over *every* 63-dimensional cube. The converse
direction is weaker. Even a proof that $\deg_x S^{(r)}_j=63$ would
exclude a property for only those cubes $I$ whose monomial
$x^{\mathbf 1_I}$ actually occurs. Excluding all 63-dimensional cubes
would require the presence of the monomial $x^{\mathbf 1_{I}}$ for each
of the 64 choices of $I$ separately.
:::

## Presence proofs {#sec:presence}

A certificate proves that monomials are absent. To prove that a bit is
*not* balanced we need the opposite: one coefficient $a_{\mathbf 1_I,v}$
in [\[eq:cubesum\]](#eq:cubesum){reference-type="eqref"
reference="eq:cubesum"} that equals 1. Here $v=(v_1,\dots,v_r)$ is a
*key pattern*, with $v_t$ the mask of the key monomial taken from
$RK_t$. In a trail, the key-addition step $u_t\to w_t$ of round $t$
attaches $k^{w_t\oplus u_t}$
(Section [3](#sec:prelim){reference-type="ref" reference="sec:prelim"}),
so each trail has exactly one key pattern, namely $v_t=w_t\oplus u_t$.

::: {#lem:presence .lemma}
**Lemma 5** (Presence). *If the number of monomial trails from
$\mathbf 1_I$ to $e_j$ with key pattern $v$ is odd, then bit $j$ of
$S^{(r)}$ is not balanced over $I$ for independent round keys. More
precisely, for the constant $c=0$ the cube sum is a nonzero polynomial
in the round keys, and for every constant $c$ some sequence of round
keys gives a nonzero cube sum.*
:::

::: proof
*Proof.* Treat the round-key bits as additional input variables. Each of
them enters the cipher exactly once, through a key addition, so the
trails of the extended function from $x^{\mathbf 1_I}k^v$ to bit $j$ are
exactly the trails above with key pattern $v$. By
Proposition [1](#prop:mp){reference-type="ref" reference="prop:mp"},
$a_{\mathbf 1_I,v}=1$. For $c=0$, the right-hand side
of [\[eq:cubesum\]](#eq:cubesum){reference-type="eqref"
reference="eq:cubesum"} reduces to
$\bigoplus_{v'}a_{\mathbf 1_I,v'}k^{v'}$, which contains $k^v$ and is
therefore not the zero polynomial. The constant enters only through
$c\oplus RK_1$, so replacing $RK_1$ by $RK_1\oplus c$ transfers a
nonzero sum from $c=0$ to any other constant. ◻
:::

::: {#lem:monobal .lemma}
**Lemma 6** (Monotonicity of balancedness). *If bit $j$ of $S^{(r)}$ is
balanced over $I$, it is balanced over every $I'\supseteq I$.
Equivalently, if it is not balanced over $I'$, it is not balanced over
any $I\subseteq I'$.*
:::

::: proof
*Proof.* The cube $\mathcal C_{I'}(c)$ is the disjoint union of the
$2^{|I'\setminus I|}$ cubes $\mathcal C_I(c')$, where $c'$ runs over the
constants that agree with $c$ outside $I'$ and are zero on $I$. Each of
these cube sums is zero. ◻
:::

Lemma [6](#lem:monobal){reference-type="ref" reference="lem:monobal"} is
the cipher-level counterpart of
Lemma [3](#lem:mono){reference-type="ref" reference="lem:mono"}. One
presence proof for a 63-dimensional cube therefore excludes a property
on that output bit for all $2^{63}$ bit-aligned cubes contained in it,
i.e. all cubes that keep the same bit constant.

#### Search for a key pattern.

The choice of $v$ decides whether a count is feasible. A pattern with
few key bits leaves many trails: in a first attempt we took the key
patterns of 20 trails found by the solver on each of two seven-round
instances, and none of them gave an odd count within $2\cdot10^4$
trails. Every key bit taken in round $t$ forces the state mask to zero
at that position and removes trails. We therefore use *maximal*
patterns. Starting from the empty pattern, we visit the $64r$ key
positions in random order and add a position whenever at least one trail
survives. We then count the trails of the resulting pattern by
enumerating the solutions of the [MP-EL]{.sans-serif} instance under
assumptions, with the input mask, the output mask and the key pattern
fixed by assumptions and with blocking clauses over the layer masks; all
other variables are determined by the masks and the pattern. A proof
needs a small odd count, and patterns with large counts are useless, so
the enumeration stops at a small cap (1500 trails, raised to 8000 and
$4\cdot10^4$ for the few bits not resolved at the first stage), and many
random restarts are made. A pattern that proved a bit for one cube is
tried first for the same bit of the other cubes, as a whole and then
with only its rounds 3--7 (or 4--7) kept and the earlier rounds searched
afresh. For the 63-dimensional cubes we also fix $v_1=0$. Nothing is
lost: the only other choice, $v_1=e_p$, makes the state monomial after
the first key addition the product of all 64 bits, and its trail count
is even, because every output bit of the remaining rounds is a component
of a permutation and has degree at most 63. For each proof the trail
returned by the enumeration is validated by the independent checker of
Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"}. The count is correct if every enumerated
trail is valid, which we check for every trail, and if no trail is
missed. The latter has two parts. That no solution of the CNF is missed
is certified by a DRAT proof that the instance becomes unsatisfiable
once the trails found are excluded
(Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"}). That every trail is a solution of the CNF
rests on the exactness of the local rules, which we verified
exhaustively for small word sizes.

Two further lemmas extend presence proofs from single output bits to
linear combinations of output bits. The first is the rank argument of
Hebborn et al. [@hebborn2021], restricted to the single input monomial
$x^{\mathbf 1_I}$.

::: {#lem:lincomb .lemma}
**Lemma 7** (Linear combinations). *Let $v^{(0)},\dots,v^{(63)}$ be key
patterns of $r$ rounds, and let $M$ be the $64\times64$ matrix over
$\mathbb{F}_2$ whose entry $M_{l,j}$ is the number of monomial trails
from $\mathbf 1_I$ to $e_j$ with key pattern $v^{(l)}$, modulo 2. If $M$
is invertible, then for every nonzero $\beta\in\mathbb{F}_2^{64}$ the
function $\langle\beta,S^{(r)}\rangle$ is not balanced over $I$, nor
over any $I'\subseteq I$, for independent round keys.*
:::

::: proof
*Proof.* By Proposition [1](#prop:mp){reference-type="ref"
reference="prop:mp"}, applied to the extended function as in the proof
of Lemma [5](#lem:presence){reference-type="ref"
reference="lem:presence"}, and by linearity, the coefficient of
$x^{\mathbf 1_I}k^{v^{(l)}}$ in $\langle\beta,S^{(r)}\rangle$ is
$\sum_j M_{l,j}\beta_j=(M\beta)_l$. Since $M$ is invertible and
$\beta\neq0$, some $(M\beta)_l$ equals 1, and the argument of
Lemma [5](#lem:presence){reference-type="ref" reference="lem:presence"}
shows that the cube sum is not identically zero. The proof of
Lemma [6](#lem:monobal){reference-type="ref" reference="lem:monobal"}
applies to any output function. ◻
:::

The second lemma gives matrix entries for output functions that, through
the last round, depend on the input of a single S-box. It formalises the
choice of last-round key monomials within one S-box that Hebborn et
al. [@hebborn2021] use to build their integral-resistance matrices (see
also the description by Peng et al. [@peng2026]), for an arbitrary
component of the S-box and a single last-round key bit. Let $r\ge2$, let
$I\neq\emptyset$, and fix an S-box $m$ of round $r$. For $i=0,\dots,3$
write $s_i=S^{(r-1)}_{4m+i}$ for bit $4m+i$ of the state before round
$r$ and $k_{r,i}$ for bit $4m+i$ of $RK_r$, so that the input of S-box
$m$ in round $r$ is $z=s\oplus k_{r}$ with $z_i=s_i\oplus k_{r,i}$. We
identify masks on the four bits of an S-box with subsets of
$\{0,1,2,3\}$, and for a nonzero mask $u$ we write
$s^u=\prod_{i\in u}s_i$.

::: {#lem:component .lemma}
**Lemma 8** (Last-round component). *Let $f=g(z)$ for a Boolean function
$g$ on $\mathbb{F}_2^4$ with ANF coefficients $g_w$,
$w\subseteq\{0,1,2,3\}$. For a key pattern $V$ of the first $r-1$ rounds
and a nonzero mask $u$, let $c_V(u)$ be the coefficient of
$x^{\mathbf 1_I}k^V$ in $s^u$, as a polynomial in the plaintext and the
round keys $RK_1,\dots,RK_{r-1}$. Then for every $t\in\{0,1,2,3\}$ the
coefficient of $x^{\mathbf 1_I}k^{V}k_{r,t}$ in $f$ is
$$\bigoplus_{u\neq0,\ t\notin u} g_{u\cup\{t\}}\,c_V(u).$$ Moreover,
$c_V(u)$ is the number, modulo 2, of $(r-1)$-round monomial trails from
$\mathbf 1_I$ with key pattern $V$ that end in the mask $u$ on S-box $m$
and zero elsewhere.*
:::

::: proof
*Proof.* Expand
$g(s\oplus k_r)=\bigoplus_w g_w\prod_{i\in w}(s_i\oplus k_{r,i})$. The
variables $s_i$ do not depend on $RK_r$, so only the terms with $w\ni t$
contain $k_{r,t}$, and in such a term the only product whose sole factor
from $RK_r$ is $k_{r,t}$ is $s^{w\setminus\{t\}}k_{r,t}$. For $w=\{t\}$
this is $k_{r,t}$ alone, which does not contain $x^{\mathbf 1_I}$
because $|I|\ge1$. Collecting the coefficient of $x^{\mathbf 1_I}k^V$ in
$s^{w\setminus\{t\}}$ for all other $w\ni t$ and writing
$u=w\setminus\{t\}$ gives the formula. The last statement is
Proposition [1](#prop:mp){reference-type="ref" reference="prop:mp"} for
the extended function $(x,RK_1,\dots,RK_{r-1})\mapsto s^u$, whose output
monomial is the mask $u$ on S-box $m$; each key bit enters once, so its
trails from $x^{\mathbf 1_I}k^V$ are the trails with key pattern $V$, as
in the proof of Lemma [5](#lem:presence){reference-type="ref"
reference="lem:presence"}. ◻
:::

# Validation {#sec:validation}

#### Reference implementation.

Our Python implementation reproduces all four published test vectors,
agrees with the authors' reference code on 1000 random encryptions, and
is cross-checked against a vectorised implementation.
Section [10](#sec:erratum){reference-type="ref" reference="sec:erratum"}
gives two corrections to the published key-schedule description.

#### Local models.

The S-box table is computed from the ANF. We verified exhaustively the
Hu--Yap rule for $n\le5$, Lemma [1](#lem:addret){reference-type="ref"
reference="lem:addret"} for $n\le4$ (all $2^{16}$ exponent pairs),
Lemma [2](#lem:deg){reference-type="ref" reference="lem:deg"} for
$n\le8$, and the carry encoding for $n\le6$.

#### Benchmark.

With the same SAT machinery and BDP rules we reproduce the results of
Eskandari et al. [@eskandari2018] for GIFT-64 [@gift2017] and
PRESENT [@present2007]:

-   GIFT-64: a 9-round property with 63 active bits and no 10-round
    property. When the constant bit is the most significant bit of a
    nibble, as in the published result, we find 30 balanced bits; the
    best position gives 32.

-   PRESENT: a 9-round property with 60 active bits and one balanced
    bit, and no 10-round property.

#### Soundness against experiment.

We evaluated cube sums for random constants and independent random round
keys in three settings:

-   the word cubes of Table [1](#tab:words){reference-type="ref"
    reference="tab:words"}, with 1016 trials;

-   the 28 cubes of the tightness study in
    Section [8](#sec:tightness){reference-type="ref"
    reference="sec:tightness"}, with 200 trials per cube and round;

-   every cube of dimension at most 16 in
    Table [3](#tab:frontier){reference-type="ref"
    reference="tab:frontier"}, including those of the variants, with 400
    trials.

No certified bit ever had a nonzero sum.

#### Trail counting.

We validated the counting used for presence proofs in two ways. First,
for 123 (key pattern, bit) pairs at two rounds and 20 at three rounds
(cubes of dimension 5 and 7), the parity of the enumerated count equals
the coefficient $a_{\mathbf 1_I,v}$ computed directly by a Möbius
transform of the cipher over the cube and key bits involved; 11 of these
coefficients are 1. Second, we repeated the enumeration with blocking
clauses over *all* variables of the instance instead of the layer masks.
On 31 instances both counts agree: exactly on the 11 instances below the
cap, and both exceed the cap on the other 20. This supports the claim
that the enumeration counts every trail exactly once.

#### Checkable artifacts.

For the boundary results we produced artifacts that can be verified
without trusting the SAT solver. They do not cover the correctness of
the CNF generator itself, which rests on the exhaustive checks of the
local rules above and on the agreement with experiment. An UNSAT answer
is certified by re-solving the CNF with an external
CaDiCaL 3.0.1 [@cadical2024] binary that writes a DRAT proof, which is
then checked by `drat-trim` [@drattrim2014]. A SAT answer is certified
by converting it into a trail and validating the trail with a checker
that re-derives every layer from the cipher specification and the local
rules, without the CNF; for a trail that belongs to a presence proof,
the checker also confirms its key pattern. A trail count $n$ is
certified by validating each of the $n$ trails found, by checking that
they are pairwise distinct, and by a DRAT proof that the instance, with
the input mask, the output mask and the key pattern fixed by unit
clauses, becomes unsatisfiable once one blocking clause per trail found
is added. A blocking clause excludes the layer masks of one trail; with
the key pattern fixed, the layer masks determine the trail, so each
clause excludes exactly one trail, and the proof shows that the
enumeration is complete. We certified in this way:

-   certificates: every certified (cube, bit) pair of Dipper at six
    rounds, of $\mathrm{Dipper}^{\oplus}$ at nine rounds and of
    $\mathrm{Dipper}^{\varnothing}$ at ten rounds, the smallest cubes of
    Table [3](#tab:frontier){reference-type="ref"
    reference="tab:frontier"} for Dipper, and the five-round word-cube
    properties (138 distinct instances; three five-round instances occur
    both as word cubes and as frontier cubes, so there were 141 proof
    runs), and every certified bit of the two minimal six-round cubes;

-   "no certificate" answers: every one of the $3\times4096$ (cube, bit)
    pairs at Dipper seven rounds, $\mathrm{Dipper}^{\oplus}$ ten rounds
    and $\mathrm{Dipper}^{\varnothing}$ eleven rounds (12 288 trails),
    and the 4456 answers of the minimality search of
    Section [6](#sec:results){reference-type="ref"
    reference="sec:results"};

-   presence proofs: the 4142 counts of
    Sections [6](#sec:results){reference-type="ref"
    reference="sec:results"}
    and [8](#sec:tightness){reference-type="ref"
    reference="sec:tightness"} (32 620 trails) and the 1791 counts
    behind the degree lower bounds of
    Section [7.2](#sec:degree){reference-type="ref"
    reference="sec:degree"} (2187 trails);

-   degree upper bounds: all 1856 bounds of
    Section [7.2](#sec:degree){reference-type="ref"
    reference="sec:degree"};

-   every solver answer behind the seven-round linear-combination result
    (Section [6.4](#sec:r7lin){reference-type="ref"
    reference="sec:r7lin"}).

All DRAT proofs were verified and all trails passed the check. The
remaining UNSAT answers, e.g. the certificates at $r\le5$ in
Table [2](#tab:maximal){reference-type="ref" reference="tab:maximal"}
and the model-comparison instances, rely on the solver answer alone. The
CNF hashes, the tool versions and the verification logs are part of the
repository.

# Certified properties of Dipper {#sec:results}

## Reproducing the published experiment

Table [1](#tab:words){reference-type="ref" reference="tab:words"}
repeats the published experiment: one 16-bit word is saturated, the
other 48 bits are constant, and 1016 trials are run (1000 with
independent random round keys, 16 with the real 128-bit key schedule). A
bit counts as empirically balanced only if its sum is zero in every
trial. As published, five rounds are the maximum, and the round count
refers to the state $S^{(r)}$ itself. For every word and every round
$r=2,\dots,5$, [MP-EL]{.sans-serif} certifies exactly the empirically
balanced bits, so these properties now hold for all round keys. The
number of trials matters. An earlier run of ours with 80 trials reported
two more bits for word $C$, one at $r=4$ and one at $r=5$, whose sums
turned out to be nonzero with probability of roughly 0.5--1%.
Certificates remove exactly this kind of error. In every trial we also
confirmed $\bigoplus T^{-1}(S^{(r+1)})=\bigoplus S^{(r)}$
(Lemma [4](#lem:free){reference-type="ref" reference="lem:free"}).

::: {#tab:words}
  Saturated word    $r{=}1$   2      3      4      5     6   $\mathrm{Dipper}^{\oplus}$   $\mathrm{Dipper}^{\varnothing}$
  ---------------- --------- ---- -------- ---- ------- --- ---------------------------- ---------------------------------
  $A$                 64      64     64     38   **3**   0          6 (26 bits)                     7 (14 bits)
  $B$                 64      56   **24**   0      0     0           5 (7 bits)                     7 (9 bits)
  $C$                 64      64     64     38   **3**   0          6 (25 bits)                     7 (4 bits)
  $D$                 64      60   **25**   0      0     0           5 (8 bits)                     7 (6 bits)

  : Balanced bits of $S^{(r)}$ for 16-bit word-saturated cubes. For
  Dipper, the empirically zero bits (1016 trials) coincide with the
  certified bits in every entry for $r\ge2$. The last two columns give,
  for the analysis variants, the last round with empirically zero bits
  (400 trials) and their number (416 trials: 400 with random round keys,
  16 with the real key schedule); these two columns are empirical only.
  Bold: last round with balanced bits.
:::

## Certified properties over all bit-aligned cubes

By Lemma [3](#lem:mono){reference-type="ref" reference="lem:mono"}, the
64 cubes of dimension 63 (one constant bit $p$) decide which rounds
admit a certificate for some bit-aligned cube.
Table [2](#tab:maximal){reference-type="ref" reference="tab:maximal"}
summarises them. At six rounds, certificates exist for 14 of the 64
positions of the constant bit, and the best positions $p\in\{4,6,7\}$
give nine balanced bits, $\{1,18,19,24,41,48,51,56,58\}$. At seven,
eight and nine rounds no position gives a certificate. Within the model,
therefore, no bit-aligned cube of any dimension certifies a single
output bit at seven rounds or more. Every one of the 4096 seven-round
queries returned a trail that passed the independent check. With
Lemma [4](#lem:free){reference-type="ref" reference="lem:free"}, the
six-round properties give seven-round distinguishers on $T^{-1}(C)$.

::: {#tab:maximal}
   Rounds $r$   cubes with a certificate   max. certified bits   solver time ([MP-EL]{.sans-serif}, 64 cubes)
  ------------ -------------------------- --------------------- ----------------------------------------------
       4                   64                      64                               3.9 s
       5                   64                      42                               6.1 s
       6                   14                       9                               7.9 s
       7                   0                        0                               8.6 s
       8                   0                        0                               11.1 s
       9                   0                        0                               12.2 s

  : Cubes of dimension 63 (constant bit $p$; 64 cubes per row).
  [MP-EL]{.sans-serif}, [MP-circuit]{.sans-serif} and [BDP]{.sans-serif}
  give identical results ([MP-circuit]{.sans-serif} was run for
  $r\le7$).
:::

#### Data complexity.

Starting from certified cubes, we removed active bits one at a time as
long as some bit stayed certified, restarting from several cubes and
random orders. Table [3](#tab:frontier){reference-type="ref"
reference="tab:frontier"} lists the smallest certified cubes *found* in
this way. They are upper bounds on the data required. At five rounds the
smallest cube found has size $2^{16}$, the size of the published
word-saturation structure (word $C$). At six rounds the minimum can be
proven. If a cube is certified for bit $j$, then by
Lemma [3](#lem:mono){reference-type="ref" reference="lem:mono"} so is
every 63-dimensional cube containing it. Its constant bits therefore lie
among the positions $p$ whose 63-dimensional cube certifies bit $j$, a
subset of the 14 positions with a six-round certificate
(Table [2](#tab:maximal){reference-type="ref" reference="tab:maximal"}).
For each bit $j$, the sets of constant bits of cubes certified for $j$
are closed under taking subsets, again by
Lemma [3](#lem:mono){reference-type="ref" reference="lem:mono"}, so they
can be searched level by level. The largest such set, over all $j$, has
four elements. Hence $2^{60}$ is the minimum within the model, and
exactly two cubes attain it: the cube with the nibble $\{4,5,6,7\}$
constant, which certifies six bits, and the cube with the nibble
$\{12,13,14,15\}$ constant, which certifies bits $\{24,51,56,58\}$. Each
of the 4456 "no certificate" answers of this search was turned into a
trail and validated independently. The same search shows that no cube of
dimension below 63 is certified for $\mathrm{Dipper}^{\oplus}$ at nine
rounds or for $\mathrm{Dipper}^{\varnothing}$ at ten rounds.

::: {#tab:frontier}
  Rounds $r$                         3   4   5    6    7    8    9    10
  --------------------------------- --- --- ---- ---- ---- ---- ---- ----
  Dipper                             2   4   16   60   --   --   --  
  $\mathrm{Dipper}^{\oplus}$                 7    22   44   59   63   --
  $\mathrm{Dipper}^{\varnothing}$            3    8    15   48   59   63

  : Smallest certified cubes found (dimension $d$, i.e. $2^d$ chosen
  plaintexts; greedy search). The last value in each row is minimal
  within the model. "--": no certificate for any bit-aligned cube
  (Lemma [3](#lem:mono){reference-type="ref" reference="lem:mono"});
  blank: not computed.
:::

## Seven rounds: presence proofs {#sec:r7presence}

The seven-round entries of Table [2](#tab:maximal){reference-type="ref"
reference="tab:maximal"} say only that the model has a trail. For each
of the 64 cubes of dimension 63 and each of the 64 output bits of
$S^{(7)}$ we searched for a presence proof
(Lemma [5](#lem:presence){reference-type="ref"
reference="lem:presence"}), and found one in all 4096 cases. The trail
counts of the key patterns found range from 1 to 1397, and 1958 of them
equal 1. For every proof all trails were enumerated again and passed the
independent check, and a DRAT proof certifies that the enumeration is
complete (Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"}). The search took about 8 core-hours in
total. Reusing patterns across positions of the constant bit
(Section [4.3](#sec:presence){reference-type="ref"
reference="sec:presence"}) was decisive: whole patterns gave 605 of the
4096 proofs and partial patterns 2107, and the random search gave the
remaining 1384. Every bit-aligned cube of dimension at most 63 lies in
one of the 64 cubes, so by Lemma [6](#lem:monobal){reference-type="ref"
reference="lem:monobal"} no bit-aligned cube has a balanced output bit
after seven rounds, for independent round keys. Since the sum of
$T^{-1}(S^{(8)})$ over a cube equals that of $S^{(7)}$ (proof of
Lemma [4](#lem:free){reference-type="ref" reference="lem:free"}), the
same holds for $T^{-1}(S^{(8)})$. The seven-round answer of the model is
therefore exact for independent round keys. Over bit-aligned cubes and
single output bits, the six-round properties of
Table [2](#tab:maximal){reference-type="ref" reference="tab:maximal"},
and their extension to $T^{-1}(C)$ by
Lemma [4](#lem:free){reference-type="ref" reference="lem:free"}, are the
longest key-independent integral properties of Dipper with independent
round keys. This does not exclude probabilistic or weak-key
distinguishers.

## Seven rounds: linear combinations of output bits {#sec:r7lin}

An attacker may also sum a linear combination
$\langle\beta,S^{(7)}\rangle$ of output bits. With
Lemma [7](#lem:lincomb){reference-type="ref" reference="lem:lincomb"} we
show that no nonzero combination is balanced after seven rounds over any
bit-aligned cube. For each of the 64 cubes of dimension 63 we need 64
key patterns $v^{(0)},\dots,v^{(63)}$, one per row of $M$, for which $M$
is invertible.

#### Deciding invertibility.

The matrix $M$ need not be computed in full. Let $G$ be the graph on the
output bits with an edge $l\to j$ ($j\neq l$) whenever pattern $v^{(l)}$
has at least one trail to bit $j$; without an edge, $M_{l,j}=0$. We
order the strongly connected components of $G$ so that every edge
between different components goes to an earlier component, and permute
the rows and the columns of $M$ by the same order. Then $M$ is block
lower triangular, with one diagonal block per component, and it is
invertible if and only if every diagonal block is. A component $\{l\}$
with a single bit needs $M_{l,l}=1$, i.e. $v^{(l)}$ must be a presence
proof for bit $l$. Inside a larger component a row need not prove its
own bit; only the invertibility of the block matters. A block is decided
by counting the trails of all its entries or, where this is infeasible,
with Lemma [8](#lem:component){reference-type="ref"
reference="lem:component"}. The lemma applies to output bits of
$S^{(7)}$ that come from a retained word of the last ARX layer: through
the rotation and the bit permutation, such a bit is an output bit of one
S-box $m$ of round 7, i.e. a function of the S-box input $z$ alone, and
so is the sum of two such bits of the same S-box. It gives the entry of
a row whose pattern consists of a six-round pattern $V$ and a single key
bit $k_{7,t}$ of S-box $m$. In the final matrices, every block that
could not be counted consists of two such bits $a,b$ of one S-box, and
one of its rows is $(1,1)$ by counting. Its determinant is then the sum
of the two entries of the other row, i.e. the entry for $S_a\oplus S_b$,
which Lemma [8](#lem:component){reference-type="ref"
reference="lem:component"} gives from the ANF of this component of the
GIFT S-box and six-round counts $c_V(u)$. We call this the *sum
argument*.

#### Finding the patterns.

We started from the 64 presence proofs of
Section [6.3](#sec:r7presence){reference-type="ref"
reference="sec:r7presence"} and replaced the patterns of bits on cycles
of $G$ by other presence proofs with no trail to the rest of their
cycle. For the cube with constant bit 0, almost every pattern had trails
to a common set of twelve output bits, all high bits of the two added
words, and the cycles that remained were small. Their blocks were often
singular, or their entries could not be counted. For two output bits 0
and 1 of one last-round S-box of a retained word there is a structural
reason. The two bits have the same ANF except for the constant and the
monomials $z_1$ and $z_0z_2$; their sum is the component
$1\oplus z_1\oplus z_0z_2$ of degree two, and a trail from a nonzero
mask never enters an S-box in the empty monomial. A trail to one of the
two bits whose last-round S-box input is any other monomial is also a
trail to the other bit, with the same key pattern, so the two entries of
a row can differ only through trails that enter the last S-box in $z_1$
or $z_0z_2$. A similar dependence of trail parities on the last-round
S-box input monomials underlies the interfering monomials that Peng et
al. [@peng2026] found in PRESENT. Pairs formed by a bit
$(X\boxplus Y)_i$ of an added word and the retained bit $Y_i$ behaved
similarly, which may be due to their common linear term $Y_i$; we did
not analyse this further. We separated such pairs by patterns that use
the last round: a six-round presence proof $V$ for one input bit of the
S-box, extended by a single last-round key bit $t$. For S-box output
bits 0 and 1 and a presence proof $V$ for $s_0$, for instance,
Lemma [8](#lem:component){reference-type="ref"
reference="lem:component"} gives the row $(1,1)$ for $t=1$ and the row
$(0,1)$ for $t=2$, whatever the other counts $c_V(u)$ are. Indeed, the
monomials that contain $z_1$ and another variable are $z_0z_1$ in both
bits, and those that contain $z_2$ and another variable are none in
bit 0 and $z_0z_2$ in bit 1, so in both cases only $u=\{0\}$
contributes. These two rows have determinant 1. How the patterns were
found does not affect the result, which we verified independently.

#### Independent verification.

A separate program starts from the final patterns only. For each cube it
recomputes $G$ and its components, checks that every edge goes to an
earlier component, and decides every diagonal block as described above;
it validates every trail it counts with the independent checker,
including the key pattern. Over the 64 cubes the matrices have 4016
components: 3948 single bits, each with a counted diagonal entry 1, and
68 blocks, of which 57 have two bits, 10 three and one four. All 68
blocks are invertible: 47 by counting all their entries, and 21 blocks
of two bits, in 13 of the cubes, by the sum argument. In all 21 the two
bits are S-box output bits 0 and 1 and the pattern of the other row ends
in the key bit $t=0$. The only monomial of $1\oplus z_1\oplus z_0z_2$
that contains $z_0$ and another variable is $z_0z_2$, so the determinant
is the single six-round count $c_V(\{2\})$. The counted entries rest on
51 698 seven-round trails and the sum arguments on 55 six-round trails.
The block-triangular structure uses 128 931 zero entries outside the
diagonal blocks, and a few zero entries lie inside the blocks. Every one
of these solver answers is certified by a checked DRAT proof
(Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"}): for each row, one proof that its pattern
has no trail to any output bit without an edge (4096 proofs, covering
all 194 321 zero entries of the 64 matrices), a proof that the
enumeration is complete for each of the 4174 counted entries, and the
same for each of the 21 six-round counts of the sum arguments. All 8291
proofs were verified.

By Lemma [7](#lem:lincomb){reference-type="ref"
reference="lem:lincomb"}, no nonzero linear combination of the output
bits of $S^{(7)}$ is balanced over any bit-aligned cube, for independent
round keys, and by Lemma [4](#lem:free){reference-type="ref"
reference="lem:free"} the same holds for $T^{-1}(S^{(8)})$. This is the
integral-resistance property of [@hebborn2021] after seven rounds,
restricted to bit-aligned cubes. Since $M$ is invertible, it also
implies once more that every single output bit is unbalanced.

## Where the balanced bits come from

We map the nine balanced bits at the six-round boundary back through the
final bit permutation. Every one of them is an output of a retained word
in the last round: bits $D_3,D_4,D_5,D_6,D_{11}$ and
$B_4,B_{12},B_{13},B_{14}$. The same holds for the five-round word-cube
properties. Bits $\{51,56,58\}$ of the word-$C$ cube map to
$D_3,B_4,B_{14}$, and bits $\{1,19,24\}$ of the word-$A$ cube map to
$D_5,D_{11},B_{12}$. No output bit of the last-round additions is
certified at the boundary. This is an observation about the certified
bits, not a claim about every output bit of the additions: bit 0 of
$A\boxplus B$, for example, is linear.
Section [7.2](#sec:degree){reference-type="ref" reference="sec:degree"}
relates it to degree.

# The role of the modular addition {#sec:ablation}

## Ablation

Table [4](#tab:ablation){reference-type="ref" reference="tab:ablation"}
compares Dipper with $\mathrm{Dipper}^{\oplus}$ and
$\mathrm{Dipper}^{\varnothing}$. The three ciphers were analysed under
identical conditions: all 64 maximal cubes, [MP-EL]{.sans-serif} and
[BDP]{.sans-serif} (which again agree), and the same solver settings
(conflict budget $10^5$ with a $5\cdot10^6$ retry; no instance was left
unresolved). Within the model, the two additions shorten the longest
certified property from nine rounds (XOR) or ten rounds (no addition) to
six. The empirical word-cube experiment
(Table [1](#tab:words){reference-type="ref" reference="tab:words"})
orders the three ciphers the same way: 5, 6 and 7 rounds. The data
needed shifts in the same direction. For six rounds the smallest
certified cubes found have size $2^{60}$ for Dipper, $2^{22}$ for
$\mathrm{Dipper}^{\oplus}$ and $2^{8}$ for
$\mathrm{Dipper}^{\varnothing}$.
Figure [2](#fig:ablation){reference-type="ref" reference="fig:ablation"}
shows this round by round.

![Data needed by the smallest certified cube found, per round, for
Dipper and the two variants without carries (values of
Table [3](#tab:frontier){reference-type="ref"
reference="tab:frontier"}). A cross, joined to the last point by a
dotted line, marks the first round at which no bit-aligned cube has a
certificate; it is drawn above the full codebook because no amount of
data suffices there. Dipper's curve reaches the full codebook three to
four rounds earlier.](fig_ablation.pdf){#fig:ablation
width="0.78\\linewidth"}

::: {#tab:ablation}
  Variant                            longest certified $r$   max. certified bits   with free round (Lemma [4](#lem:free){reference-type="ref" reference="lem:free"})
  --------------------------------- ----------------------- --------------------- -----------------------------------------------------------------------------------
  Dipper ($\boxplus$)                          6                      9                                                    7
  $\mathrm{Dipper}^{\oplus}$                   9                      5                                                   10
  $\mathrm{Dipper}^{\varnothing}$             10                      2                                                   11

  : Longest round count with a certificate for some bit-aligned cube
  (all cubes, by Lemma [3](#lem:mono){reference-type="ref"
  reference="lem:mono"}) and the maximum number of balanced bits at that
  round.
:::

The variants keep the rotations, the S-box, the permutation and the
full-state key addition, so they are not GIFT-64. A difference measured
with an existence-based model describes certified properties. It
describes the true algebraic behaviour only where the model is tight. We
measured tightness only on Dipper for up to five rounds
(Section [8](#sec:tightness){reference-type="ref"
reference="sec:tightness"}).

## Algebraic degree {#sec:degree}

By Section [3](#sec:prelim){reference-type="ref"
reference="sec:prelim"}, a bit of degree less than $d$ is balanced over
every cube of dimension $d$, so degrees give a global view of integral
resistance. We consider the degree in the plaintext bits, with the round
keys as independent variables. For every output bit $j$ and round count
$r$ we first computed the smallest $D$ for which [MP-EL]{.sans-serif}
with a free input mask of weight at least $D+1$ and output $e_j$ is
unsatisfiable. This certifies the upper bound $\deg_x S^{(r)}_j\le D$
for all round keys. We then looked for a matching lower bound: a
monomial $x^u$ with $\operatorname{wt}(u)=D$ taken from the model, and a
presence proof for it (Lemma [5](#lem:presence){reference-type="ref"
reference="lem:presence"}). At the degree limit the first-round part of
the key monomial is often forced to be empty, so the search also uses
patterns with $v_1=0$. For one one-round bit the search failed and we
computed its full ANF instead, which has 32 variables; the ANF of four
further one-round bits agrees with their presence proofs. All
$64\times7$ cases for Dipper and $64\times11$ for each variant were
treated without timeouts.

The two bounds coincide in 1843 of the 1856 cases, so there the degree
is exact. The other 13 cases lie in Dipper at rounds 2 and 3 and in
$\mathrm{Dipper}^{\oplus}$ at rounds 4 to 6. In 12 of them the lower
bound is one below the upper bound, and in one it is two below. Here the
upper bound may be loose because trails cancel. Every upper bound is
certified by a checked DRAT proof, and every lower bound by a presence
proof with a certified count, except for the one-round bit whose degree
we took from its ANF (Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"}).

![Mean algebraic degree of the output bits of $S^{(r)}$, with the round
keys as independent variables. The plotted values are proven lower
bounds. They equal the certified upper bounds in 1843 of the 1856 cases
and differ by at most two otherwise. For Dipper, bits are grouped by the
word of the last ARX layer that produced
them.](fig_degree.pdf){#fig:degree width="0.78\\linewidth"}

::: {#tab:deg1}
  $i$               0   1   2   3   4   5    6    7    8    9    10   11   12   13   14   15
  ---------------- --- --- --- --- --- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
  $A\boxplus B$     3   5   7   8   9   11   13   15   16   18   20   21   22   24   25   26
  $C\boxplus D$     2   4   6   6   8   10   12   12   14   16   18   18   20   22   24   24
  $B$ (retained)    2   2   3   3   2   2    3    3    2    2    3    3    2    2    3    3

  : Algebraic degree after one round (exact), by bit position $i$ in the
  output of the ARX layer.
:::

Figure [3](#fig:degree){reference-type="ref" reference="fig:degree"} and
Table [5](#tab:deg1){reference-type="ref" reference="tab:deg1"} support
three observations.

*The addition acts immediately.* After one round, the degree of bit $i$
of $A\boxplus B$ grows almost linearly in $i$, from 3 to 26, the pattern
predicted by Lemma [2](#lem:deg){reference-type="ref"
reference="lem:deg"} and Corollary [1](#cor:round){reference-type="ref"
reference="cor:round"}. The retained word $B$ stays at the S-box degree
2 or 3. The growth is slower than $3(i+1)$ because neighbouring bits
share S-boxes.

*Retained words lag by about one round.* The mean degree of the added
words reaches 60 at $r=3$, and the retained words need one more round.
After five rounds every added-word bit has degree 63, while six
retained-word bits, $\{1,19,24,51,56,58\}$, have degree exactly 62.
Degree 62 certifies the bit over every 63-dimensional cube. These six
bits are exactly the bits certified for all 64 maximal cubes at five
rounds, and the same six bits carry the six-round certificate of the
$2^{60}$ cube (Table [3](#tab:frontier){reference-type="ref"
reference="tab:frontier"}).

*The degree saturates three to four rounds earlier with the additions.*
From $r=6$ on, every output bit of Dipper has degree 63; for
$\mathrm{Dipper}^{\oplus}$ and $\mathrm{Dipper}^{\varnothing}$ this
happens only from $r=9$ and $r=10$ on (the last rounds with a degree
below 63 are 5, 8 and 9, respectively). The ordering matches
Table [4](#tab:ablation){reference-type="ref" reference="tab:ablation"},
but the degree does not determine the certificate boundary: at six
rounds Dipper still has certificates for particular 63-dimensional cubes
although every degree is 63, and $\mathrm{Dipper}^{\oplus}$ at eight
rounds has 64 certified bits on some cube while only two bits have
degree below 63. Certificates are per cube, the degree is over all cubes
(Remark [1](#rem:percube){reference-type="ref"
reference="rem:percube"}). In the linear variants the degree can grow
only through the S-boxes, at most by a factor of three per round. In
Dipper each addition contributes the additional factor of
Corollary [1](#cor:round){reference-type="ref" reference="cor:round"}.
Because the degrees are exact, these are statements about the ciphers
with independent round keys, not only about the model.

# Precision of the models {#sec:tightness}

#### [MP-EL]{.sans-serif} versus [BDP]{.sans-serif}.

On all 64 maximal cubes, [MP-EL]{.sans-serif} and [BDP]{.sans-serif}
produced identical certificate sets: for $r=4,\dots,9$ on Dipper, up to
$r=10$ on $\mathrm{Dipper}^{\oplus}$ and up to $r=11$ on
$\mathrm{Dipper}^{\varnothing}$. [MP-circuit]{.sans-serif} agreed with
both wherever it was run ($r\le7$). On 140 further (cube, round)
instances of dimension 4--16 on Dipper, all three models produced
identical certificate sets, at similar cost (8.4 s, 8.8 s and 6.2 s in
total). This shows that the two *existence* models agree on the tested
instances. It does not show that cancellation-aware monomial prediction
would have no advantage over [BDP]{.sans-serif} in general; for the
instances of Table [6](#tab:tight){reference-type="ref"
reference="tab:tight"}, the end of this section shows that it has none.
Part of the agreement is structural. Every S-box layer of Dipper is
preceded by a full-state key addition. In [MP-EL]{.sans-serif} the
composition "key addition, then S-box" allows exactly the transitions
$u\to v$ with $S[w\to v]=1$ for some $w\succeq u$, which is precisely
the BDP S-box table. The two models can therefore differ only inside the
ARX layer, and there we observed no difference.

#### Certificates versus experiment.

Table [6](#tab:tight){reference-type="ref" reference="tab:tight"}
compares certificates with experiment on 28 cubes of dimension 4--16:
word-aligned, nibble-aligned and random. A bit is *empirically zero* if
its sum is zero in 200 trials, and it is a *gap* bit if it is
empirically zero but not certified. Gap bits were re-tested with 3000
more trials (1000 for 16-dimensional cubes); *persistent* gaps stayed
zero. The last column counts the persistent gap bits that we proved
unbalanced.

-   At four and five rounds the certificates match experiment up to
    three gap bits, none of them persistent.

-   At two and three rounds, about 7--17% of the empirically zero bits
    are not certified, and 46 bits stay zero in every re-test.

Such a bit is either an exact property lost to cancellation
(Example [1](#ex:cancel){reference-type="ref" reference="ex:cancel"}) or
a sum that is nonzero only with small probability. We tried two exact
methods on these bits.

-   *Trail parity per key monomial.* For bit 30 of a 12-dimensional
    random cube at two rounds, the number of trails exceeded our
    enumeration cap of $10^5$. The key monomial was that of a single
    trail and contained few key bits.

-   *Low-weight evaluation.* The cube sum $g$ is a multilinear
    polynomial in the key bits. If it has degree at most $D$, it
    vanishes identically iff it vanishes on every point of Hamming
    weight at most $D$. [MP-EL]{.sans-serif} gives the key support of
    $g$ and a bound on $D$. For the 46 persistent gap bits the support
    has 33--88 key bits and the degree bound is 23--65. For 43 of them
    the number of low-weight points exceeds $10^{15}$. The three
    smallest cases (support 33--38, degree bound 23--27) need about
    $8.5\cdot10^9$--$2.7\cdot10^{11}$ points. Within a time limit of
    800 s per case we evaluated 2.1--3.8 million points, covering all
    points of weight at most 5 or 6. No nonzero cube sum appeared, but
    the enumeration is far from complete, so this method decided none of
    these bits.

Presence proofs with maximal key patterns
(Section [4.3](#sec:presence){reference-type="ref"
reference="sec:presence"}) decide all of them. For each of the 46
persistent gap bits we found a key pattern with an odd count, between 1
and 9 trails, and validated the trail; the search took 11 s in total.
None of these bits is balanced. Each of their cube sums is a nonzero
polynomial in the round keys that vanished in all 3200 trials. This is
the failure mode of the 80-trial experiment of
Section [6](#sec:results){reference-type="ref" reference="sec:results"}
in a stronger form: uniformly random keys almost never reveal it, and an
algebraic argument is needed to decide it. The presence proof also shows
where to look. If $v$ is the key pattern of a proof, some round key
whose bits lie inside $v$ gives the cube sum 1, because the sum of the
cube sum over all such keys equals the coefficient of $k^v$. Sampling
sparse keys inside $v$ found such round keys for 31 of the 46 bits, and
each was confirmed with the reference implementation. For these bits the
claim can be checked without the SAT model. Every other bit that is not
certified had a nonzero sum in some trial. Hence every bit of the 112
instances in Table [6](#tab:tight){reference-type="ref"
reference="tab:tight"} is decided, and on every instance the certified
bits are exactly the balanced bits. On these instances the existence
model loses nothing to cancellation, and a model that counts trails
could not certify more. The frontier itself (six and seven rounds, cubes
of dimension 60--63) is out of experimental reach;
Section [6.3](#sec:r7presence){reference-type="ref"
reference="sec:r7presence"} treats it with presence proofs.

::: {#tab:tight}
   Rounds   certified   empirically zero   gap   persistent gap   proved unbalanced
  -------- ----------- ------------------ ----- ---------------- -------------------
     2        1283            1384         101         21                21
     3         446            537          91          25                25
     4         91              93           2          0                 --
     5          6              7            1          0                 --

  : Certified versus empirically zero bits over 28 cubes of dimension
  4--16 (sums over all cubes). Last column: persistent gap bits proved
  unbalanced by a presence proof
  (Lemma [5](#lem:presence){reference-type="ref"
  reference="lem:presence"}).
:::

# A partial-key filtering extension {#sec:keyrec}

This section describes how the six-round properties could be used for
key filtering over one further round. We present it as a proposed
procedure with an explicit cost model. It is not a validated eight-round
attack.

#### Procedure.

Let bit $j$ of $S^{(6)}$ be certified over a cube $I$. For eight-round
ciphertexts $C$, Lemma [4](#lem:free){reference-type="ref"
reference="lem:free"} gives
$$\bigoplus_{x\in\mathcal C_I(c)} T^{-1}\!\big(T^{-1}(C)\oplus RK_8\big)_j = 0 .$$
Bit $j$ of $T^{-1}(z)$ depends on four bits of $z$ if its nibble lies in
word $B$ or $D$, where the inverse layer is only a rotation. It depends
on up to 32 bits if the nibble lies in $A$ or $C$, because of the borrow
chain of the subtraction. For $j=1$, which is certified over the
$2^{60}$ cube, it depends on four bits of $Z=T^{-1}(C)$ and hence on
four bits of $RK_8$. One structure of $2^{60}$ chosen plaintexts is
processed in a streaming fashion:

1.  For each ciphertext, compute $Z=T^{-1}(C)$ (keyless) and toggle one
    of 16 parity bits indexed by the four relevant bits of $Z$.

2.  Let $h:\mathbb{F}_2^4\to\mathbb{F}_2$ be the partial inverse that
    maps the four relevant bits of $z$ to bit $j$ of $T^{-1}(z)$
    (inverse rotation of word $D$, then the inverse S-box of the
    corresponding nibble). For each of the 16 guesses $g$, evaluate
    $\bigoplus_{v:\text{parity}[v]=1} h(v\oplus g)$ over the 16 table
    entries, and discard $g$ if the result is 1.

One structure costs $2^{60}$ evaluations of $T^{-1}$ plus $2^8$ table
operations. It needs 16 bits of memory besides the ciphertext stream.
Every structure uses a fresh value of the four constant bits.

#### Assumptions and small-scale evidence.

The right guess always passes. The number of wrong guesses left after
$N$ structures depends on how the wrong-guess sums behave. Under the
usual heuristic that they are independent and uniform, $N$ structures
leave $15\cdot2^{-N}$ wrong guesses on average. We ran the same
procedure at small scale, on six rounds: the 4-round certificate of the
cube $\{60,\dots,63\}$ on bit 1, followed by the free round and one
key-guessed round, with 200 random keys. The right guess always
survived. A wrong guess survived one structure with probability about
$0.565$, so the uniform heuristic is optimistic, and eight structures
left $1.13$ candidates on average, with a unique survivor in 88.5% of
the runs. We have not established that this rate carries over to eight
rounds or that the structures act as independent filters there.
Extrapolating anyway, about eight structures, i.e. $2^{63}$ chosen
plaintexts, would be needed to identify four bits of $RK_8$. This
recovers round-key bits, not the master key, and the data requirement is
half the codebook. We therefore regard the procedure as evidence of a
large margin, not as an attack on Dipper.

# Specification of the analysed cipher and corrections {#sec:erratum}

The results of this paper depend only on the round function, because
every certificate holds for arbitrary independent round keys. The round
function is fixed by Section [3](#sec:prelim){reference-type="ref"
reference="sec:prelim"} and confirmed by all published test vectors,
which exercise all 28 rounds.

We implemented both key schedules independently and compared them with
the published test vectors and with the authors' reference
implementation (Specification v1.1 and its Python reference code, which
generated the vectors of [@dipper2026]). Our implementation agrees with
the reference code on all four published vectors and on 1000 random
encryptions (500 per key size). The specification and the reference code
are consistent with each other. Two statements in the key-schedule
section of the published paper [@dipper2026] are not, and we correct
them here.

1.  *Round-key window of Dipper-64/128.* Equation (7) of [@dipper2026]
    states $RK_r=K^{(r)}[127{:}64]$. The specification and the reference
    code use $RK_r=K^{(r)}[63{:}0]=k_3\|k_2\|k_1\|k_0$ for both key
    sizes, and this produces the published vectors.

2.  *S-box positions of Dipper-64/96.* Equation (9) of [@dipper2026]
    applies the S-box to the top nibble $[15{:}12]$ of words
    $k'_1,k'_2,k'_4,k'_5$. The specification and the reference code
    apply it to the key-state bits $K[95{:}92]$, $K[71{:}68]$,
    $K[47{:}44]$ and $K[23{:}20]$, i.e. to $k'_5[15{:}12]$,
    $k'_4[7{:}4]$, $k'_2[15{:}12]$ and $k'_1[7{:}4]$. For $k'_4$ and
    $k'_1$ the S-box therefore acts on the second-lowest nibble, not on
    the top nibble. The comments of the specification call these
    positions "top nibbles", which is how the error entered the paper.
    With this correction the published Dipper-64/96 vectors are
    reproduced. The word permutation, the rotations and the
    round-constant position $K[52{:}48]$ are as stated in [@dipper2026].

The Dipper-64/128 S-box positions ($k'_7$, $k'_3$, $k'_1$, top nibbles)
are stated correctly in [@dipper2026].
Appendix [13](#app:tv){reference-type="ref" reference="app:tv"} lists
all published vectors with intermediate round keys and states. Neither
correction affects the integral results, which hold for arbitrary
independent round keys, or the round function, which the published text
states correctly.

# Discussion {#sec:discussion}

#### Security implications.

The integral properties certified here reach six of Dipper's 28 rounds
on the state, and seven with the keyless final-round inversion. The
filtering extension of Section [9](#sec:keyrec){reference-type="ref"
reference="sec:keyrec"} would need half the codebook to reach eight
rounds. Integral attacks therefore leave a large margin. This is
consistent with the differential, linear and impossible-differential
bounds of [@dipper2026]. None of these results is a proof of security.

#### Design implication.

The ablation and the degree bounds point the same way. With the two
half-state additions, the certifiable integral properties end three to
four rounds earlier than for an otherwise identical round without
carries. Within the state, the retained operands are the part whose
degree bound grows most slowly, and every certified property at the
boundary lives there. A designer who wants integral saturation to happen
sooner could therefore target the retained words, for example by
alternating which words are added in consecutive rounds. We have not
evaluated this change.

#### Towards exact bounds.

Presence proofs close the gap between "no certificate" and "not
balanced" wherever they succeed: for all 46 persistent gap bits and for
every output bit of all 64 seven-round cubes of dimension 63. The method
goes back to Hebborn et al. [@hebborn2020; @hebborn2021]. Zeng and
Tian [@zeng2024] adapted it to ciphers without a whitening key, and Peng
et al. [@peng2026] showed that interfering monomials can make every
count even when the key monomial is badly chosen. For Dipper the choice
of the key pattern decided the outcome. Taking the key monomial of a
single trail gave no odd count within $2\cdot10^4$ trails on two
seven-round instances, while maximal key patterns gave an odd count for
every bit we tried. With them the seven-round statement becomes a
statement about the cipher for all bit-aligned cubes; the search took
about 8 core-hours. A stronger goal is integral resistance in the sense
of [@hebborn2021], a guarantee that covers input sets other than
bit-aligned cubes and all nonzero linear combinations of output bits.
Section [6.4](#sec:r7lin){reference-type="ref" reference="sec:r7lin"}
establishes it for bit-aligned cubes after seven rounds; other input
sets remain open. Since $RK_1$ acts as a whitening key, the theorem of
Hebborn et al. would cover them, but it needs matrices over all 64 input
monomials of degree 63 jointly. With our presence patterns, the matrix
of every single output bit over these 64 monomials is singular: two
input monomials that differ only inside one nibble usually give equal
rows. Hebborn et al. avoid this with key monomials chosen right after
the first S-box layer; in Dipper that key is added only after the first
ARX layer. We leave this to future work. The framework has been extended
to key whitening by modular addition [@beierle2025] and to complex
linear layers [@gerhalter2026]. To our knowledge it has not been applied
to a round function that itself contains modular additions, as Dipper's
does.

#### The real key schedule.

All presence results assume independent round keys. To test whether they
carry over to the key schedules, we extended [MP-EL]{.sans-serif} by the
key schedule: the master-key bits are variables, each round key is a
COPY of the 64 low bits $K^{(r)}[63{:}0]$ of the key state, and the key
update is modelled by wiring, the key-schedule S-boxes and the round
constants. A trail then carries a master-key monomial. For the cube with
constant bit 0 and six output bits we took 20 samples per bit, key size
and round count, alternately maximal and minimal master-key monomials
found greedily (as in Section [4.3](#sec:presence){reference-type="ref"
reference="sec:presence"}; a minimal monomial is built by excluding key
bits as long as a trail survives), and counted their trails up to a cap
of 2000. At six rounds, 44 of the 45 counts below the cap were even for
the 128-bit key, and one was odd (15 trails; we did not validate these
trails independently, because our checker does not model the key
schedule); 75 samples exceeded the cap. For the 96-bit key, 39 counts
were even, none odd, and 81 samples exceeded the cap. At seven rounds,
226 of the 240 samples for the two key sizes exceeded the cap and the
other 14 counts were even. A possible reason is that each master-key bit
enters several round keys, so that trails may occur in pairs that differ
only in the round key through which a master-key bit enters; we have not
verified this. Proving presence with the key schedule needs a different
technique, such as the nested monomial prediction developed for
superpoly recovery in cube attacks [@hu2021nested]. We leave it open.

#### Limitations.

-   The seven-round statement concerns bit-aligned cubes, for which it
    covers every nonzero linear combination of output bits. It says
    nothing about input sets that are not bit-aligned cubes.

-   Independent round keys make the certificates stronger, since they
    hold for all keys. For the same reason they may miss properties that
    depend on the key schedule.

-   Below the boundary rounds, the data complexities are those of the
    smallest certified cubes found by a greedy search; at the boundary
    rounds they are proven minimal within the model.

-   A presence proof excludes a key-independent zero sum. It does not
    exclude a probabilistic or weak-key distinguisher: a cube sum that
    is a nonzero polynomial can still vanish for most keys, as the gap
    bits of Section [8](#sec:tightness){reference-type="ref"
    reference="sec:tightness"} show.

-   Presence proofs hold for independent round keys. A cube sum that is
    a nonzero polynomial in independent round keys could, in principle,
    vanish for all round keys produced by the key schedule; we do not
    exclude this.

-   The artifacts of Section [5](#sec:validation){reference-type="ref"
    reference="sec:validation"} certify the solver's answers for a given
    CNF. That every monomial trail is a solution of the CNF, and hence
    that no trail is missing from a count or from an unsatisfiable
    instance, rests on the local rules, which we verified exhaustively
    for small word sizes, and is supported by the agreement of the
    counts with the ANF at two and three rounds.

-   Degrees are exact in 1843 of 1856 cases; in the other 13 we give an
    interval of width at most two.

-   The filtering extension relies on an extrapolated survival rate.

# Conclusion

The five-round integral properties that were found experimentally for
Dipper now hold for all round keys, backed by checked DRAT proofs.
Certified properties extend to six rounds, with $2^{60}$ data, the
minimum for a certified cube within the model, and to seven rounds with
the keyless final-round inversion. No bit-aligned cube gives a balanced
bit of $S^{(7)}$: the model has no certificate there, and presence
proofs show that every output bit, and every nonzero linear combination
of output bits, is unbalanced over every such cube, for independent
round keys. The two half-state modular additions account for the
difference between six certified rounds and the nine or ten rounds of
otherwise identical rounds without carries. Only retained-operand bits
are certified at the boundary. This is consistent with the exact degree
of the addition output bits and with the degree of every output bit and
round, which we determined exactly in 1843 of 1856 cases and which grows
fastest on the added words. On every Dipper instance we examined, the
existence model with exact local transitions certifies the same bits as
the conventional division property, partly because a full-state key
addition precedes each S-box layer. Presence proofs also decide every
persistent gap bit of the 112 tightness instances: none of them is
balanced. What remains of integral resistance in the sense
of [@hebborn2021] after seven rounds are input sets other than
bit-aligned cubes.

# Data and code availability {#data-and-code-availability .unnumbered}

The reference implementation, SAT models, scripts, raw JSON results, the
proof-checking pipeline and the sources of this paper are available at
<https://github.com/AlexGuseinov/dipper-integral>. The CNF files and
DRAT proofs of the boundary certificates (about 60 MB) are provided as a
release archive of the repository. The other DRAT proofs of
Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"} are regenerated and checked on the fly; the
repository contains their verification results. The DRAT proofs certify
the solver's answers for the generated CNF files; the CNF generator
itself remains part of the trusted base
(Section [5](#sec:validation){reference-type="ref"
reference="sec:validation"}). `make test` runs all validation checks,
`make reproduce` regenerates every table and figure, and
`make certificates` regenerates and checks all proofs and trails.

# Test vectors and intermediate values {#app:tv}

All values in hexadecimal, most significant bit first. Dipper-64/128
with $RK_r=K^{(r)}[63{:}0]$
(Section [10](#sec:erratum){reference-type="ref"
reference="sec:erratum"}).

::: center
                 Vector 1                             Vector 2
  -------------- ------------------------------------ ------------------------------------
  $K$            `000102030405060708090A0B0C0D0E0F`   `FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF`
  $P$            `0123456789ABCDEF`                   `FFFFFFFFFFFFFFFF`
  $RK_1$         `08090A0B0C0D0E0F`                   `FFFFFFFFFFFFFFFF`
  $S^{(1)}$      `87D2D72CD66C68F2`                   `3118311831183108`
  $RK_2$         `140506076303E0F0`                   `EFFFFFFFEFFFFFFF`
  $S^{(2)}$      `41C18243B4605E18`                   `01A6DC1CB8EEB9D1`
  $RK_3$         `1001020208C00F0E`                   `EFFFFFFEEBFFFFFF`
  $S^{(3)}$      `22C358EDC3BD1695`                   `F49F4481BC92B880`
  $RK_{28}$      `78090A148A9BF0E0`                   `FFFFFFE02664FFFF`
  $C=S^{(28)}$   `4B46284387969060`                   `6ABB4518063706B0`
:::

Dipper-64/96 under the corrected S-box positions
(Section [10](#sec:erratum){reference-type="ref"
reference="sec:erratum"}).

::: center
                 Vector 1                     Vector 2
  -------------- ---------------------------- ----------------------------
  $K$            `00112233445566778899AABB`   `000000000000000000000000`
  $P$            `0123456789ABCDEF`           `0000000000000000`
  $RK_1$         `445566778899AABB`           `0000000000000000`
  $S^{(1)}$      `97B834DFA857A809`           `3118311831183108`
  $RK_2$         `6227BBBA00A12233`           `0001100000100000`
  $S^{(2)}$      `E77DDB5526AFBAB0`           `B23376D0F8957AFC`
  $RK_3$         `402A433264F56697`           `0006100010100010`
  $S^{(3)}$      `3BDC9FD0104AC1C2`           `11D992CE930C3154`
  $RK_{28}$      `200AEA1FD9DD001D`           `E5659977E0A29797`
  $C=S^{(28)}$   `5F189202D3152B8F`           `D873355EC63B1B4B`
:::

[^1]: Corresponding author. ORCID 0009-0003-4959-2887.
