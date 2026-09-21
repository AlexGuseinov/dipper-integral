---
abstract: |
  Dipper is a 64-bit lightweight block cipher whose round combines the
  GIFT S-box and bit permutation with two 16-bit modular additions
  acting on half of the state. In the design paper we bounded integral
  distinguishers experimentally at five rounds. We replace this
  experimental evidence with machine-checked certificates that hold for
  every choice of the round keys. We model monomial trails through
  reduced-round Dipper as SAT instances, using the exact coefficient
  table of the S-box and an exact local rule for the map
  $(x,y)\mapsto(x\boxplus y,\,y)$ that we derive from the
  Braeken–Semaev/Hu–Yap characterisation of modular addition and verify
  exhaustively. The models are validated component-wise against exact
  algebraic normal forms, against published division-property results
  for GIFT-64 and PRESENT, and against cube-sum experiments with random
  keys, which never contradicted a certificate. On Dipper we obtain: (i)
  the published five-round properties are reproduced and certified for
  all keys; (ii) six-round integral properties exist (up to nine
  balanced bits with $2^{63}$ chosen plaintexts, six balanced bits with
  $2^{60}$); (iii) no seven-round property is certified for any
  bit-aligned cube and single output bit, which is exhaustive within the
  model because of a monotonicity lemma; (iv) since Dipper has no final
  key whitening, every $r$-round property extends to $r{+}1$ rounds
  without key guessing, giving a seven-round distinguisher and an
  eight-round partial key recovery with $2^{63}$ data. In a controlled
  ablation, replacing the two modular additions by XOR extends the
  longest certified property to nine rounds, and removing them extends
  it to ten; all certified balanced bits at the six-round boundary
  originate from the two words that bypass the addition in the last
  round. We explain this with a degree lemma for modular addition
  (output bit $i$ has algebraic degree exactly $i+1$) and with certified
  degree bounds for every output bit and round: after one round the
  added words already reach degree 26, against 3 for the retained words,
  and every output bit reaches the maximal bound 63 after six rounds for
  Dipper, but only after nine and ten rounds for the variants. Exact
  monomial prediction and the conventional bit-based division property
  produce identical certificates in every case we examined, which we
  partly explain by the full-state key addition that precedes each S-box
  layer. We also report that the published Dipper-64/96 test vectors
  could not be reproduced from the specification text and that the
  128-bit vectors require a different round-key window than the one
  stated. All code and data are public.
author:
- Ali Huseynli[^1]
- Yadigar Imamverdiyev
- |
  Jalal Alizadeh  
  Department of Cybersecurity, Faculty of Information Technologies and
  Telecommunications,  
  Azerbaijan Technical University, Baku AZ1073, Azerbaijan
bibliography: refs.bib
title: |
  Certified Integral Properties of the Dipper Block Cipher:  
  Monomial-Trail Analysis and the Role of the Half-State Modular
  Addition
---

**Keywords:** integral cryptanalysis; division property; monomial
prediction; modular addition; SAT; lightweight block cipher; Dipper

# Introduction

Integral (square, saturation) cryptanalysis (Knudsen and Wagner 2002)
looks for a set of chosen plaintexts, typically an affine subspace (a
*cube*), over which some output bit sums to zero independently of the
key. The division property (Todo 2015b) and its bit-based versions (Todo
and Morii 2016; Xiang et al. 2016) turned the search for such properties
into a propagation problem that can be solved with MILP or SAT tools;
monomial prediction (Hu et al. 2020), shown in (Hu et al. 2020) to be
equivalent to the three-subset division property without unknown
subset (Hao et al. 2020), gives the exact algebraic view in which a cube
sum vanishes if and only if the corresponding monomial coefficient is
zero.

Algebraic properties of modular addition are well understood in
isolation. Its differential and linear behaviour is described exactly by
the results of Lipmaa and Moriai (Lipmaa and Moriai 2002) and of
Wallén (Wallén 2003), and its algebraic normal form by Braeken and
Semaev (Braeken and Semaev 2005). Integral analysis of ciphers that mix
modular addition with S-boxes is less developed. Division-property
models for ARX designs (Sun, Wang, and Wang 2016; Sun et al. 2017) were
designed for pure ARX ciphers such as SPECK (Beaulieu et al. 2015),
where the addition is the only nonlinear operation. In a hybrid round
the addition interacts with a small S-box and a bit permutation, and it
is not obvious how much it contributes to resistance against integral
attacks, or which part of the state carries an integral property the
longest.

Dipper, proposed in our previous work (Huseynli, Imamverdiyev, and
Alizadeh 2026), is a 64-bit hybrid SPN–ARX cipher with 96- and 128-bit
keys and 28 rounds. Each round applies a full-state key addition,
sixteen GIFT S-boxes (Banik et al. 2017), four word rotations, two
16-bit modular additions over half of the state and the GIFT-64 bit
permutation. Its security evaluation includes MILP differential bounds,
CP-SAT linear bounds, an impossible-differential search and an
*experimental* integral search that saturates one 16-bit word and
reports distinguishers of at most five rounds. Experimental integral
searches have two weaknesses: a sum that is zero for a few random keys
is not necessarily zero for all keys, and a search limited to
word-saturated cubes says nothing about other cubes.
Section 6 shows that the first weakness is real
for Dipper: with 80 trials, two bits appear balanced that are not.

#### Research questions.

We ask three questions. (Q1) Which integral properties of reduced-round
Dipper hold for *all* keys, and how far do they extend over *all*
bit-aligned cubes? (Q2) Does the exact treatment of the modular
addition, now possible through the Hu–Yap characterisation (Hu and Yap
2024), certify more than the conventional division property? (Q3) What
exactly do the two half-state additions contribute, and why do some
parts of the state stay balanced longer than others?

#### Contributions.

1.  **Exact local models.** We model the Dipper round with the exact
    $16\times16$ monomial table of the GIFT S-box and an exact local
    rule (Lemma 1) for the addition with retained
    operand $(x,y)\mapsto(x\boxplus y,y)$, which is the actual shape of
    Dipper’s ARX layer. Every local model is checked exhaustively
    against algebraic normal forms.

2.  **All-key certificates and a complete round bound within the
    model.** We certify the published five-round properties for all
    keys, find six-round properties, and prove that no bit-aligned cube
    of any dimension gives a certificate for a single output bit at
    seven rounds in our model
    (Lemma 3 reduces this to the 64 cubes of
    dimension 63).

3.  **Free final round and key recovery.** Because Dipper has no final
    whitening key, every $r$-round state property is an $(r{+}1)$-round
    property of $T^{-1}(C)$ without key guessing
    (Lemma 4). We quantify the resulting
    seven-round distinguisher and an eight-round partial key recovery,
    and we validate the key-recovery procedure end-to-end at small
    scale.

4.  **Model comparison and tightness.** Exact monomial prediction,
    gate-level monomial prediction and the conventional bit-based
    division property give identical certificates on every instance
    examined. We explain this and measure how close the certificates are
    to experiment.

5.  **Role of the modular addition.** An ablation with the additions
    replaced by XOR or removed isolates the contribution of the modular
    additions: 6 certified rounds versus 9 and 10.

6.  **Degree mechanism.** We prove that output bit $i$ of an $n$-bit
    modular addition has algebraic degree exactly $i+1$
    (Lemma 2). We compute certified upper bounds
    on the algebraic degree of every output bit of Dipper and of the
    variants for every round, and show that the degree gap between added
    and retained words explains where integral properties survive
    (Section 9).

7.  **Specification check.** We report discrepancies between the Dipper
    specification text and its published test vectors
    (Section 10).

The repository <https://github.com/AlexGuseinov/dipper-integral>
contains the reference implementation, all models, scripts and raw
results.

#### Organisation.

Section 2 reviews related work.
Section 3 fixes notation.
Section 4 gives the local rules, the degree
lemma and the structural lemmas.
Section 5 validates the models.
Section 6 reports the certified properties of
Dipper. Section 7 compares the models with each other
and with experiment.
Sections 8
and 9 study the role of the modular
addition. Section 10 reports the specification check, and
Section 11 discusses implications and
limitations.

#### Scope of the claims.

A certificate proves that a cube sum is zero for all keys. The absence
of a certificate proves nothing about the cipher: it only means that the
model found no certificate. Our round bound at seven rounds is therefore
a statement about the models used here, not a proof that Dipper has no
seven-round integral distinguisher.

# Related work

#### Integral and higher-order differential cryptanalysis.

Integral attacks go back to the Square attack (Daemen, Knudsen, and
Rijmen 1997) and were formalised as integral cryptanalysis by Knudsen
and Wagner (Knudsen and Wagner 2002) and as the saturation attack by
Lucks (Lucks 2002). Z’aba et al. (Z’aba et al. 2008) extended them to
bit-oriented ciphers. The underlying algebra is that of higher-order
derivatives (Lai 1994; Knudsen 1995): a cube sum is a derivative of
order equal to the cube dimension, and it vanishes when the algebraic
degree is smaller than that order. Degree bounds for iterated
constructions were given by Canteaut and Videau (Canteaut and Videau
2002) and by Boura, Canteaut and De Cannière (Boura, Canteaut, and De
Cannière 2011). The cube attack of Dinur and Shamir (Dinur and Shamir
2009) uses the same algebra in a key-recovery setting.

#### Division property and monomial prediction.

Todo introduced the division property (Todo 2015b) and used it to break
full MISTY1 (Todo 2015a). The bit-based division property (Todo and
Morii 2016) and its MILP modelling (Xiang et al. 2016) made automated
search practical. Eskandari et al. (Eskandari et al. 2019) provide a
SAT-based tool and a table of results that we use as a benchmark. For
stream ciphers, the division property underlies modern cube
attacks (Todo et al. 2017; Wang et al. 2018). The three-subset division
property (Hu and Wang 2019) and its variant without unknown subset (Hao
et al. 2020) remove the imprecision of the two-subset version. Hu et
al. (Hu et al. 2020) showed that the latter is equivalent to monomial
prediction, which counts monomial trails modulo 2. Complex linear layers
need dedicated models (Hu, Wang, and Wang 2020; Zhang and Rijmen 2019).

#### Modular addition.

Sun, Wang and Wang (Sun, Wang, and Wang 2016) gave the first MILP model
of the bit-based division property for ARX ciphers, based on a
gate-level decomposition of the carry chain. Sun et al. (Sun et al.
2017) moved it to SAT. Hu and Yap (Hu and Yap 2024) observed that the
characterisation of Braeken and Semaev (Braeken and Semaev 2005) gives a
perfect local monomial-prediction model for modular addition, and
CLAASP-MP (Bellini, Rachidi, and Tiwari 2026) integrates such models
into a general MILP framework. We use this characterisation for the
specific map $(x,y)\mapsto(x\boxplus y,y)$ of Dipper and derive from it
a degree statement.

#### Security guarantees and degree lower bounds.

Finding an integral distinguisher is an upper-bound question. The
converse question, proving that *no* integral distinguisher exists after
a number of rounds, requires exact information such as degree lower
bounds. Hebborn et al. developed lower bounds on the degree (Hebborn et
al. 2020) and strong security guarantees against integral
distinguishers (Hebborn et al. 2021) for ciphers with full-state key
addition. Zeng and Tian (Zeng and Tian 2024) extended them to ciphers
without a whitening key. Dipper falls into the latter class, so these
methods are the natural next step
(Section 11).

#### Integral key recovery.

Key recovery built on monomial prediction is studied, for example, by
Hadipour and Eichlseder (Hadipour and Eichlseder 2022).

#### Positioning.

We do not claim a new general framework. Our contribution is the
analysis of one hybrid cipher: exact rules for its particular ARX shape,
all-key certificates, a round bound over all bit-aligned cubes within
the model, a model comparison, an ablation, and a degree-based
explanation.

# Preliminaries

## Dipper

The state is $S=A\|B\|C\|D$ with 16-bit words, $A=S[63{:}48]$ and bit 0
the least significant. For $r=1,\dots,28$,
$$S^{(r)} = T\big(S^{(r-1)}\oplus RK_r\big),\qquad
T = P\circ M\circ \mathrm{SC},$$ where $\mathrm{SC}$ applies the GIFT
S-box to the sixteen nibbles, $M$ rotates $A,B,C,D$ left by $1,4,7,11$
and then sets $A\gets A\boxplus B$ and $C\gets C\boxplus D$ (with $B,D$
unchanged), and $P$ is the GIFT-64 bit permutation. The ciphertext is
$S^{(28)}$; there is no final key addition. $T$ is a public permutation.
We write $\mathrm{Dipper}^{\oplus}$ for the variant in which the two
additions are replaced by XOR and $\mathrm{Dipper}^{\varnothing}$ for
the variant in which they are removed (rotations kept). These are
analysis variants only.

## Cube sums and monomial prediction

For $u\in\mathbb{F}_2^n$ write $x^u=\prod_{i:u_i=1}x_i$. Let
$I\subseteq\{0,\dots,63\}$ be a set of active bits and let the remaining
plaintext bits be constants. For an output bit $f$ of $r$ rounds, viewed
as a polynomial in the plaintext $x$ and the key material $k$,
$$\bigoplus_{x_I\in\mathbb{F}_2^{|I|}} f(x,k) \;=\; \sum_{u\supseteq I,\,v} a_{u,v}\, x^{u\setminus I}k^v ,$$
so the sum vanishes for all constants and all keys if and only if
$a_{u,v}=0$ whenever $u\supseteq I$. For a composite function
$f=f_r\circ\dots\circ f_1$, the coefficient of $x^{u_0}$ in $f^{u_r}$
equals the parity of the number of *monomial trails*
$u_0\to u_1\to\dots\to u_r$ in which each step is a nonzero local
coefficient (Hu et al. 2020). If no trail exists, the coefficient is
zero. This is the only direction we use: *no trail* $\Rightarrow$
*balanced*.

The conventional bit-based division property (BDP) (Todo and Morii 2016;
Xiang et al. 2016) propagates a set of vectors instead of monomials. It
is sound in the same direction (no division trail to a unit vector
$\Rightarrow$ the bit is balanced) and can be less precise.

# Models

## Local propagation rules

#### Key addition.

For $s'=s\oplus k$ with free $k$,
$s'^{w}=\sum_{u\preceq w}s^u k^{w\oplus u}$. Hence $u\to w$ is a trail
step iff $u\preceq w$, and distinct steps carry distinct key monomials.
Under BDP the key addition is transparent.

#### S-box.

For $y=S(x)$ we compute $T[u][v]=[x^u]\,y^v$ for all
$u,v\in\mathbb{F}_2^4$ by Möbius transform. For the GIFT S-box, 68 of
the 256 pairs are nonzero. The BDP table is $\mathrm{BDP}[k][v]=1$ iff
$T[u][v]=1$ for some $u\succeq k$, which gives 170 transitions.

#### Modular addition.

Braeken and Semaev (Braeken and Semaev 2005), applied to cryptanalysis
by Hu and Yap (Hu and Yap 2024), show that for $z=x\boxplus y$ on $n$
bits, $[x^ay^b]\,z^w=1$ if and only if
$\operatorname{val}(a)+\operatorname{val}(b)=\operatorname{val}(w)$ over
the integers. Dipper does not use $z$ alone: the addend is also an
output. The following lemma gives the exact rule for that shape.

<div id="lem:addret" class="lemma">

**Lemma 1**. *Let $F(x,y)=(x\boxplus y,\,y)$ on $n$-bit words. Then
$[x^a y^b]\,(x\boxplus y)^w y^c = 1$ if and only if
$\operatorname{val}(w)\ge\operatorname{val}(a)$ and $b = b'\vee c$,
where $b'$ is the word with
$\operatorname{val}(b')=\operatorname{val}(w)-\operatorname{val}(a)$.*

</div>

<div class="proof">

*Proof.* By the Braeken–Semaev characterisation,
$(x\boxplus y)^w=\sum_{\operatorname{val}(a')+\operatorname{val}(b')=\operatorname{val}(w)}x^{a'}y^{b'}$.
Multiplying by $y^c$ and using $y_i^2=y_i$ gives
$\sum x^{a'}y^{b'\vee c}$. The coefficient of $x^ay^b$ is the parity of
$\#\{b' : \operatorname{val}(a)+\operatorname{val}(b')=\operatorname{val}(w),\ b'\vee c=b\}$.
The equation determines $b'$ uniquely, and $b'$ exists iff
$\operatorname{val}(w)\ge\operatorname{val}(a)$. ◻

</div>

The same characterisation gives the exact algebraic degree of each
output bit of the addition.

<div id="lem:deg" class="lemma">

**Lemma 2** (Degree of an addition bit). *Let $z=x\boxplus y$ on $n$-bit
words. For $0\le i<n$, the output bit $z_i$ has algebraic degree exactly
$i+1$ as a Boolean function of the $2n$ input bits.*

</div>

<div class="proof">

*Proof.* Take $w=e_i$, i.e. $\operatorname{val}(w)=2^i$. By the
Braeken–Semaev characterisation, $x^ay^b$ occurs in $z_i$ iff
$\operatorname{val}(a)+\operatorname{val}(b)=2^i$, and its degree is
$\mathrm{wt}(a)+\mathrm{wt}(b)$. By Kummer’s theorem (Kummer 1852),
$\mathrm{wt}(a)+\mathrm{wt}(b)=\mathrm{wt}(a+b)+c(a,b)$, where $c(a,b)$
is the number of carries in the binary addition of $a$ and $b$. Here
$\mathrm{wt}(a+b)=1$, and carries can only occur at positions
$0,\dots,i-1$, so the degree is at most $i+1$. The pair $a=1$, $b=2^i-1$
produces $i$ carries and attains $i+1$. ◻

</div>

<div id="cor:round" class="corollary">

**Corollary 1**. *In one Dipper round, let $d$ bound the degree of the
round input. Every bit of the retained words $B,D$ after the ARX layer
is an S-box output bit and has degree at most $3d$. Bit $i$ of
$A\boxplus B$ or $C\boxplus D$ is a polynomial of degree $i+1$ in S-box
output bits, so its degree can reach $\min\{3d(i+1),64\}$. Only bit 0 of
the added words is linear in the S-box outputs.*

</div>

The corollary is an upper bound, not a statement about the actual
degree. Section 9 shows that the certified bounds follow
this pattern closely.

In the SAT model, the integer equation
$\operatorname{val}(a)+\operatorname{val}(b')=\operatorname{val}(w)$ is
encoded bitwise with auxiliary carries: $a_i+b'_i+q_i=w_i+2q_{i+1}$ with
$q_0=q_n=0$. These are carries between exponent integers, not the
cipher’s data carries. Since $b'$ and $q$ are determined by $(a,w)$,
each trail has exactly one extension to the auxiliary variables.

We call the model built from these tables *exact MP*: its local
relations are exact, while the global test is trail *existence*, not
trail parity.

#### Gate-level alternatives.

For comparison we also model the addition as a ripple-carry circuit
($s_i=x_i\oplus y_i\oplus c_i$,
$c_{i+1}=x_iy_i\oplus(x_i\oplus y_i)c_i$) with explicit COPY gates,
including the copy of $y$ that forms the retained output. The circuit is
propagated with monomial rules (COPY: $u=\bigvee v_j$; AND: $u_1=u_2=v$;
XOR: $v=u_1+u_2$) in the model we call *MP-circuit*, and with BDP rules
(COPY: $u=\sum v_j$; AND: $v=u_1\vee u_2$) in the model we call *BDP*.

## Round model, soundness and two structural lemmas

One round is modelled as key addition, sixteen S-box relations, the word
rotations (wiring), the two addition relations and the bit permutation
(wiring). The input mask is fixed to the indicator of $I$ and the output
mask after $r$ rounds to the unit vector $e_j$. Every relation is a set
of clauses that forbid the invalid assignments. We solve the instances
with CaDiCaL (Biere et al. 2020) through PySAT (Ignatiev, Morgado, and
Marques-Silva 2018). Each output bit is an incremental query under
assumptions.

<div class="proposition">

**Proposition 1** (Soundness). *If the exact MP model (or the BDP model)
is unsatisfiable for $(I,r,j)$, then $\bigoplus_{x_I}S^{(r)}_j=0$ for
every value of the constant bits and every sequence of round keys
$RK_1,\dots,RK_r$. In particular, the property holds under both Dipper
key schedules.*

</div>

<div class="proof">

*Proof.* Every local relation contains all transitions with nonzero
coefficient, so every nonzero coefficient of $x^{u}$, $u\supseteq I$, in
$S_j^{(r)}$ has at least one trail starting from $u$. Such a trail first
passes the key addition to some $w\succeq u\succeq I$, and $I\preceq w$
is also a valid key-addition step, so the model, whose input mask is
exactly $I$, contains a trail as well. (Under BDP the same holds because
the division property is defined by $u\succeq I$.) The round keys are
independent free variables, so the statement covers all key sequences,
and therefore the subset produced by any key schedule. The constant bits
merge with $RK_1$ into free variables. ◻

</div>

<div id="lem:mono" class="lemma">

**Lemma 3** (Monotonicity). *In the MP model, if $I\subseteq I'$ and
$(I,r,j)$ has no trail, then $(I',r,j)$ has no trail. Consequently, if
no bit-aligned cube of dimension 63 yields a certificate for output bit
$j$ after $r$ rounds, no bit-aligned cube of any dimension $\le63$
does.*

</div>

<div class="proof">

*Proof.* The first operation is the key addition, so the masks reachable
after it from $I$ are $\{w\succeq I\}$, which contains
$\{w\succeq I'\}$. All subsequent constraints are identical. Every cube
of dimension $\le 63$ lies inside some cube of dimension 63. ◻

</div>

The 64-dimensional cube (the full codebook) is trivially balanced for
any permutation and is excluded.

<div id="lem:free" class="lemma">

**Lemma 4** (Free final round). *If
$\bigoplus_{x\in\mathcal C}S^{(r)}_j=0$ for all keys and $|\mathcal C|$
is even, then $\bigoplus_{x\in\mathcal C}T^{-1}(S^{(r+1)})_j=0$ for all
keys.*

</div>

<div class="proof">

*Proof.* $T^{-1}(S^{(r+1)})=S^{(r)}\oplus RK_{r+1}$, and the constant
$RK_{r+1}$ cancels over an even number of terms. ◻

</div>

Lemma 4 uses a different output test (the
ciphertext passed through the public map $T^{-1}$) and gives no
information about $RK_{r+1}$. We therefore report round counts for
$S^{(r)}$ and state the $(r{+}1)$-round extension separately.

# Validation

#### Reference implementation.

Our Python implementation reproduces both published Dipper-64/128 test
vectors and is cross-checked against a vectorised implementation.
Section 10 discusses the key schedule.

#### Local models.

The S-box table is computed from the ANF. We verified the Hu–Yap rule
for $x\boxplus y$ exhaustively for $n\le5$,
Lemma 1 exhaustively for $n\le4$ (all $2^{16}$
exponent pairs), Lemma 2 for $n\le8$, and the carry encoding for
$n\le6$.

#### Benchmark.

With the same SAT machinery and BDP rules we reproduce the results of
Eskandari et al. (Eskandari et al. 2019) for GIFT-64 (Banik et al. 2017)
and PRESENT (Bogdanov et al. 2007): a 9-round property with 63 active
bits for GIFT-64 (30 balanced bits when the constant bit is the most
significant bit of a nibble, as in the published result; 32 for the best
position), no 10-round property, a 9-round property with 60 active bits
and one balanced bit for PRESENT, and no 10-round property.

#### Soundness against experiment.

We evaluated cube sums for random constants and independent random round
keys in three places: the word cubes of
Table 1 (1016 trials), the 28 cubes of the
tightness study in
Section 7 (200 trials per cube and round),
and every cube of dimension at most 16 in the frontier of
Table 3, including those of the variants
(400 trials). No certified bit ever had a nonzero sum in any of these
experiments.

# Results on Dipper

## Reproducing the published experiment

Table 1 repeats the published experiment: one
16-bit word saturated, the other 48 bits constant, and 1016 trials (1000
with independent random round keys, 16 with the real 128-bit key
schedule). A bit counts as empirically balanced only if its sum is zero
in every trial. Five rounds are the maximum, as published, and the round
count refers to the state $S^{(r)}$ itself. For every word and every
round $r=2,\dots,5$, the exact MP model certifies exactly the
empirically balanced bits, so these properties now hold for all keys.
The trial count matters: an earlier run with 80 trials reported two
additional bits for word $C$ (one at $r=4$, one at $r=5$) whose sums
turned out to be nonzero with probability of roughly 0.5–1%. This is the
weakness of purely experimental bounds that certificates remove. In
every trial we also confirmed
$\bigoplus T^{-1}(S^{(r+1)})=\bigoplus S^{(r)}$
(Lemma 4).

<div id="tab:words">

| Saturated word | $r{=}1$ |  2  |  3  |  4  |   5   |  6  | $\mathrm{Dipper}^{\oplus}$ | $\mathrm{Dipper}^{\varnothing}$ |
|:---------------|:-------:|:---:|:---:|:---:|:-----:|:---:|:--------------------------:|:-------------------------------:|
| $A$            |   64    | 64  | 64  | 38  | **3** |  0  |        6 (26 bits)         |           7 (14 bits)           |
| $B$            |   64    | 56  | 24  |  0  |   0   |  0  |         5 (7 bits)         |           7 (9 bits)            |
| $C$            |   64    | 64  | 64  | 38  | **3** |  0  |        6 (25 bits)         |           7 (4 bits)            |
| $D$            |   64    | 60  | 25  |  0  |   0   |  0  |         5 (8 bits)         |           7 (6 bits)            |

Balanced bits of $S^{(r)}$ for 16-bit word-saturated cubes. For Dipper
($r=1$–$6$) the empirically zero bits (1016 trials) coincide with the
certified bits in every entry for $r\ge2$. The last two columns give,
for the analysis variants, the last round with empirically zero bits
(400 trials) and their number; these are empirical only. Bold: last
round with balanced bits.

</div>

## Certified properties over all cubes

By Lemma 3, the 64 cubes of dimension 63 (one
constant bit $p$) decide which rounds admit a certificate for some cube.
Table 2 summarises them. Six rounds admit
certificates for 14 of the 64 positions of the constant bit. The best
positions $p\in\{4,6,7\}$ give nine balanced bits
$\{1,18,19,24,41,48,51,56,58\}$. At seven rounds no position gives a
certificate, so within the model no bit-aligned cube of any dimension
has a seven-round certificate for any single output bit. With
Lemma 4, the six-round properties are
seven-round distinguishers on $T^{-1}(C)$.

<div id="tab:maximal">

| Rounds $r$ | cubes with a certificate | max. balanced bits | solver time (MP, all 64 cubes) |
|:----------:|:------------------------:|:------------------:|:------------------------------:|
|     4      |            64            |         64         |             3.9 s              |
|     5      |            64            |         42         |             6.1 s              |
|     6      |            14            |         9          |             7.9 s              |
|     7      |            0             |         0          |             8.6 s              |

Cubes of dimension 63 (constant bit $p$, 64 cubes per row). Identical
for exact MP, MP-circuit and BDP.

</div>

#### Data complexity.

Starting from certified cubes, we removed active bits one at a time for
as long as some bit stayed certified. We restarted from several cubes
and random orders.
Table 3 lists the smallest cubes found. They
are upper bounds on the data needed, not proven minima. The five-round
bound $2^{16}$ coincides with the published word-saturation structure
(word $C$). The six-round cube keeps the nibble $\{4,5,6,7\}$ constant
and certifies six bits.

<div id="tab:frontier">

| Rounds $r$                      |  3  |  4  |  5  |  6  |  7  |  8  |  9  | 10  |
|:--------------------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Dipper                          |  2  |  4  | 16  | 60  |  –  |  –  |  –  |  –  |
| $\mathrm{Dipper}^{\oplus}$      |     |     |  7  | 22  | 44  | 59  | 63  |  –  |
| $\mathrm{Dipper}^{\varnothing}$ |     |     |  3  |  8  | 15  | 48  | 59  | 63  |

Smallest certified cubes found (dimension $d$, i.e. $2^d$ chosen
plaintexts) per round count. “–”: no certificate for any bit-aligned
cube (Lemma 3); blank: not computed.

</div>

## Where the balanced bits come from

Mapping the nine balanced bits at the six-round boundary back through
the final bit permutation shows that every one of them is an output of
word $B$ or word $D$ in the last round (bits $D_3,D_4,D_5,D_6,D_{11}$
and $B_4,B_{12},B_{13},B_{14}$). These are the words that feed the
additions but pass through them unchanged. No output bit of
$A\boxplus B$ or $C\boxplus D$ is balanced at the boundary. The same
holds for the five-round word-cube properties: bits $\{51,56,58\}$ of
the word-$C$ cube map to $D_3,B_4,B_{14}$ and bits $\{1,19,24\}$ of the
word-$A$ cube to $D_5,D_{11},B_{12}$. No output bit of the last-round
additions is certified at the boundary; only retained-operand bits are.
(Bit 0 of $A\boxplus B$ is linear, so this is an observation about the
certified bits, not a general statement about every output bit of the
additions.)

## Consequences for key recovery

Consider an eight-round attack: the six-round property on bit $j$ of
$S^{(6)}$, the free seventh round
(Lemma 4), and one round with a key guess,
i.e. $S^{(6)}_j\oplus RK_{7,j}=T^{-1}\big(T^{-1}(C)\oplus RK_8\big)_j$.
Bit $j$ of $T^{-1}$ depends on four input bits if its nibble lies in
word $B$ or $D$ (rotation only), and on up to 32 bits if it lies in $A$
or $C$ (borrow chain of the subtraction). Bit $j=1$ is certified for the
$2^{60}$ cube and depends on only four bits of $RK_8$. Each structure of
$2^{60}$ plaintexts gives one parity condition on those four bits. We
validated the procedure end-to-end on a scaled-down instance (4-round
certificate of the cube $\{60,\dots,63\}$ on bit 1, followed by the free
round and one key-guessed round, i.e. six rounds, 200 random keys). The
right guess always survived. A wrong guess survived one structure with
probability about $0.565$, so eight structures left on average $1.13$
candidates. Applying this rate to the eight-round attack is an
extrapolation from the scaled-down instance. The eight-round attack
therefore needs about $8\cdot2^{60}=2^{63}$ chosen plaintexts and
$2^{63}$ partial decryptions to recover four bits of $RK_8$. This data
complexity is half the codebook, so the attack is of theoretical
interest only. Our best integral attack therefore covers 8 of the 28
rounds.

# Precision of the models

#### MP versus BDP.

Across all 64 maximal cubes, exact MP and BDP produced identical
certificate sets for $r=4,\dots,7$ on Dipper and up to $r=11$ on the
variants, and MP-circuit agreed with both wherever it was run ($r\le7$).
Across 140 further (cube, round) instances of dimension 4–16 on Dipper,
all three models produced *identical* certificate sets. Their costs were
similar: 8.4 s, 8.8 s and 6.2 s for the 140 instances. Part of the
explanation is structural. In Dipper every S-box layer is preceded by a
full-state key addition. In the MP model, the composition “key addition
then S-box” allows exactly the transitions $u\to v$ with $T[w][v]=1$ for
some $w\succeq u$, and this is precisely the BDP S-box table. The two
approaches can therefore differ only inside the ARX layer, and there we
observed no difference. This agrees with the general observation of Hu
et al. (Hu et al. 2020) that existence-based models lose precision
mainly through cancellation, which neither model captures.

#### Certificates versus experiment.

Table 4 compares certificates with experiment
on 28 cubes (word, nibble-aligned and random, dimension 4–16).
*Empirically zero* means zero in 200 trials. A *gap* bit is empirically
zero but not certified. Gap bits were re-tested with 3000 more trials
(1000 for 16-dimensional cubes), and *persistent* gaps stayed zero. At
four and five rounds the certificates match experiment up to three gap
bits, none of them persistent. At two and three rounds about 7–17% of
the empirically zero bits are not certified, and 46 bits stay zero in
all re-tests. Such a bit is either an exact property lost to trail
cancellation or a sum that is nonzero only with small probability. We
tried two exact methods to decide these bits. First, trail counting with
parity per key monomial: for bit 30 of a 12-dimensional random cube at
two rounds, the number of trails exceeded our enumeration cap of $10^5$,
because every key-addition layer multiplies the trails by key monomials.
Second, a degree argument. The cube sum $g$ is a multilinear polynomial
in the key bits, and a polynomial of degree at most $D$ vanishes
identically iff it vanishes on every point of Hamming weight at most
$D$. The MP model gives both the key support of $g$ and a bound on $D$.
For all 46 persistent gap bits, however, the support contains 33–88 key
bits and the degree bound is 23–65, so the number of evaluations is far
beyond reach. We leave these cases open. In this sample they occur only
at two and three rounds. The frontier itself (six and seven rounds,
cubes of dimension 60–63) is out of experimental reach, so we cannot
measure tightness there.

<div id="tab:tight">

| Rounds | certified | empirically zero | gap | persistent gap |
|:------:|:---------:|:----------------:|:---:|:--------------:|
|   2    |   1283    |       1384       | 101 |       21       |
|   3    |    446    |       537        | 91  |       25       |
|   4    |    91     |        93        |  2  |       0        |
|   5    |     6     |        7         |  1  |       0        |

Certified versus empirically zero bits over 28 cubes of dimension 4–16
(sums over all cubes).

</div>

# The role of the modular addition

Table 5 compares Dipper with
$\mathrm{Dipper}^{\oplus}$ and $\mathrm{Dipper}^{\varnothing}$ under
identical cubes (all 64 maximal cubes), models (exact MP and BDP,
identical results) and solver settings (conflict budget $10^5$ with a
$5\cdot10^6$ retry, no instance left unresolved). Within the models, the
two modular additions shorten the longest certified property from nine
rounds (XOR) or ten rounds (no addition) to six. The empirical word-cube
experiment (Table 1) shows the same ordering: 5, 6 and 7
rounds. The data frontier
(Table 3) shifts in the same way: six rounds
need $2^{60}$ plaintexts for Dipper, $2^{22}$ for
$\mathrm{Dipper}^{\oplus}$ and $2^{8}$ for
$\mathrm{Dipper}^{\varnothing}$.
Section 9 gives the mechanism: the additions
raise the degree of their high-order output bits in proportion to the
bit position (Lemma 2), and the retained operands lag behind by
about one round.

<div id="tab:ablation">

| Variant                         | longest certified $r$ | max. balanced bits | with free round (Lemma 4)                    |
|:--------------------------------|:---------------------:|:------------------:|:--------------------------------------------------------------------:|
| Dipper ($\boxplus$)             |           6           |         9          |                                  7                                   |
| $\mathrm{Dipper}^{\oplus}$      |           9           |         5          |                                  10                                  |
| $\mathrm{Dipper}^{\varnothing}$ |          10           |         2          |                                  11                                  |

Longest round count with a certificate for some cube (all cubes, by
Lemma 3) and the maximum number of balanced bits
at that round.

</div>

A caution about scope: the variants keep the rotations, the S-box, the
permutation and the full-state key addition, so they are not GIFT-64. A
difference between variants measured with an existence-based model shows
how the models behave. It becomes a statement about the true algebraic
behaviour only where the models are tight. We measured tightness only on
Dipper at up to five rounds
(Section 7), not at the boundary rounds of the
variants, so the round differences in
Table 5 are statements about certified
properties.

# Algebraic degree and the mechanism

A cube sum over a cube of dimension $d$ vanishes for all keys whenever
the output bit has degree less than $d$ in the plaintext bits. Degree
bounds therefore give a coarse but global view of integral resistance.
For every output bit $j$ and round count $r$ we computed the smallest
$D$ such that the exact-MP model with a free input mask of weight at
least $D+1$ and output $e_j$ is unsatisfiable. This certifies
$\deg_x S^{(r)}_j\le D$ for all round keys. Degree 64 is impossible for
a component of a permutation, so bounds are reported up to 63. All
$64\times7$ bounds for Dipper and $64\times11$ bounds for each variant
were resolved without timeouts.

<figure id="fig:degree">
<embed src="fig_degree.png" />
<figcaption>Mean certified upper bound on the algebraic degree of the
output bits of <span
class="math inline"><em>S</em><sup>(<em>r</em>)</sup></span>. For
Dipper, bits are grouped by the word of the last ARX layer that produced
them.</figcaption>
</figure>

<div id="tab:deg1">

| $i$            |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  | 10  | 11  | 12  | 13  | 14  | 15  |
|:---------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| $A\boxplus B$  |  3  |  5  |  7  |  8  |  9  | 11  | 13  | 15  | 16  | 18  | 20  | 21  | 22  | 24  | 25  | 26  |
| $C\boxplus D$  |  2  |  4  |  6  |  6  |  8  | 10  | 12  | 12  | 14  | 16  | 18  | 18  | 20  | 22  | 24  | 24  |
| $B$ (retained) |  2  |  2  |  3  |  3  |  2  |  2  |  3  |  3  |  2  |  2  |  3  |  3  |  2  |  2  |  3  |  3  |

Certified degree bounds after one round, by bit position $i$ in the
output of the ARX layer.

</div>

Three observations follow from
Figure 1 and
Table 6.

*The addition acts immediately.* After one round, the bound of bit $i$
of $A\boxplus B$ grows almost linearly with $i$, from 3 to 26, as
Lemma 2 predicts. The retained word $B$ stays at
the S-box degree, 2 or 3. Bits that share S-boxes explain why the growth
is slower than $3(i+1)$.

*Retained words lag by about one round.* For Dipper the mean bound of
the added words reaches 60 at $r=3$, while the retained words need one
more round. After five rounds all added-word bits have bound 63, while
six retained-word bits, $\{1,19,24,51,56,58\}$, are still at 62. A bound
of 62 means that the bit is balanced over every 63-dimensional cube, and
these six bits are indeed exactly the bits certified for all 64 maximal
cubes at five rounds. The same six bits carry the six-round certificate
of the $2^{60}$ cube
(Table 3).

*The variants are slower by three to four rounds.*
$\mathrm{Dipper}^{\oplus}$ and $\mathrm{Dipper}^{\varnothing}$ reach
bound 63 on every bit only after nine and ten rounds, against six for
Dipper. This matches the longest certified properties of
Table 5 (9 and 10 rounds against 6). In the
linear variants the degree grows only through the S-boxes, and each
round multiplies it by at most three. In Dipper, each addition
contributes the extra factor of
Lemma 2.

These bounds are upper bounds: a bound of 63 does not prove that a
degree-63 monomial occurs. Proving degree lower bounds, as in (Hebborn
et al. 2020), would turn the seven-round model bound into an exact
statement. Section 11 discusses this.

# Specification check

Our text-faithful implementation of Dipper-64/128 reproduces both
published test vectors only when the round key is taken as
$RK_r=K^{(r)}[63{:}0]$. Equation (7) of (Huseynli, Imamverdiyev, and
Alizadeh 2026) states $K^{(r)}[127{:}64]$. For Dipper-64/96 we could not
reproduce either published test vector. This remained true under a
brute-force search over all 720 word permutations of the key update, all
placements and directions of the two word rotations, every 3- or
4-subset of S-box words, all six round-constant positions and three
extraction windows. The round function itself is confirmed by the
128-bit vectors. None of the integral results depends on the key
schedule, because every certificate holds for arbitrary independent
round keys. This is an erratum to our design paper: before submission,
the 96-bit schedule must be checked against the reference code, and
intermediate round keys should be published with the test vectors.

# Discussion

#### Security implications.

The integral properties certified here reach seven of Dipper’s 28 rounds
(six on $S^{(r)}$, plus the keyless final round), and the only key
recovery we derived reaches eight rounds with $2^{63}$ data. Integral
attacks therefore leave a large margin. This is consistent with the
differential, linear and impossible-differential bounds of (Huseynli,
Imamverdiyev, and Alizadeh 2026). None of these results is a proof of
security.

#### Design implication.

The ablation and the degree bounds agree: the two half-state additions
make Dipper reach full degree three to four rounds earlier than an
otherwise identical round without carries. The degree is also uneven
within the state. The retained operands are the slowest part, and every
certified property at the boundary lives there. A designer who wants
faster integral saturation could therefore target the retained words,
for example by alternating which words are added in consecutive rounds.
We have not evaluated this change.

#### Towards exact bounds.

The main open point is the gap between “no certificate” and “no
distinguisher”. Hebborn et al. (Hebborn et al. 2020, 2021) prove the
presence of monomials by finding a key monomial with an odd number of
trails, and Zeng and Tian (Zeng and Tian 2024) adapt the method to
ciphers without a whitening key, a class that includes Dipper. We tried
a direct version (take the key monomial of one trail, then count all
trails with that monomial) on two seven-round, 63-dimensional instances.
With 20 random key monomials per instance we found no odd count within
the enumeration limit of $2\cdot10^4$ trails, so the question remains
open. A tailored choice of key monomials, as in (Hebborn et al. 2021),
is the most promising route.

# Limitations

\(1\) The round bound at seven rounds holds within existence-based
models. It does not exclude a seven-round integral property that depends
on trail cancellation, or other kinds of integral distinguishers: input
sets that are not bit-aligned cubes (affine subspaces in other bases,
non-affine sets), or output functions other than single bits. (2)
Independent round keys make the certificates stronger (they hold for all
keys) but may miss properties that depend on the key schedule. (3) The
data-complexity frontier comes from greedy search and gives upper
bounds. (4) The gap bits of
Section 7 are unresolved. (5) The eight-round
key recovery needs $2^{63}$ data and is theoretical.

# Conclusion

The experimental five-round integral bound of Dipper is now a certified
all-key result. Certified properties extend to six rounds ($2^{60}$
data), and to seven rounds with the keyless final-round inversion.
Within the model no bit-aligned cube reaches seven rounds. In terms of
certified properties, the two half-state modular additions cost three to
four integral rounds compared with XOR or no addition, and only
retained-operand bits are certified at the boundary. On Dipper, exact
monomial prediction brings no precision gain over the conventional
division property, partly because a full-state key addition precedes
each S-box layer. The remaining imprecision appears only at two and
three rounds, where some bits are empirically zero but uncertified; they
are either lost to trail cancellation or nonzero with small probability.
A degree lemma for modular addition and certified degree bounds explain
the mechanism: the added words reach full degree about one round before
the retained words, and three to four rounds before the variants without
carries. Dipper’s 28 rounds leave a large margin against these
properties.

# Data and code availability

Reference implementation, SAT models, scripts, raw JSON results and this
paper’s sources: <https://github.com/AlexGuseinov/dipper-integral>.
`make test` runs all validation checks; `make reproduce` regenerates
every table.

<div id="refs" class="references csl-bib-body hanging-indent">

<div id="ref-gift2017" class="csl-entry">

Banik, Subhadeep, Sumit Kumar Pandey, Thomas Peyrin, Yu Sasaki, Siang
Meng Sim, and Yosuke Todo. 2017. “GIFT: A Small Present.” In
*Cryptographic Hardware and Embedded Systems – CHES 2017*, 10529:321–45.
LNCS. Springer.

</div>

<div id="ref-simonspeck2015" class="csl-entry">

Beaulieu, Ray, Douglas Shors, Jason Smith, Stefan Treatman-Clark, Bryan
Weeks, and Louis Wingers. 2015. “The SIMON and SPECK Lightweight Block
Ciphers.” In *Proceedings of the 52nd Design Automation Conference
(DAC)*. ACM.

</div>

<div id="ref-bellini2026claaspmp" class="csl-entry">

Bellini, Emanuele, Mohamed Rachidi, and Sharwan K. Tiwari. 2026.
“CLAASP-MP: An Automated MILP Framework for Monomial Prediction.”
Cryptology ePrint Archive, Paper 2026/735.
<https://eprint.iacr.org/2026/735>.

</div>

<div id="ref-cadical2020" class="csl-entry">

Biere, Armin, Katalin Fazekas, Mathias Fleury, and Maximilian Heisinger.
2020. “CaDiCaL, Kissat, Paracooba, Plingeling and Treengeling Entering
the SAT Competition 2020.” Proceedings of SAT Competition 2020 B-2020-1.
University of Helsinki.

</div>

<div id="ref-present2007" class="csl-entry">

Bogdanov, Andrey, Lars R. Knudsen, Gregor Leander, Christof Paar, Axel
Poschmann, Matthew J. B. Robshaw, Yannick Seurin, and Charlotte
Vikkelsoe. 2007. “PRESENT: An Ultra-Lightweight Block Cipher.” In
*Cryptographic Hardware and Embedded Systems – CHES 2007*, 4727:450–66.
LNCS. Springer.

</div>

<div id="ref-boura2011" class="csl-entry">

Boura, Christina, Anne Canteaut, and Christophe De Cannière. 2011.
“Higher-Order Differential Properties of Keccak and Luffa.” In *Fast
Software Encryption – FSE 2011*, 6733:252–69. LNCS. Springer.

</div>

<div id="ref-braeken2005" class="csl-entry">

Braeken, An, and Igor Semaev. 2005. “The ANF of the Composition of
Addition and Multiplication Mod $2^n$ with a Boolean Function.” In *Fast
Software Encryption – FSE 2005*, 3557:112–25. LNCS. Springer.

</div>

<div id="ref-canteaut2002" class="csl-entry">

Canteaut, Anne, and Marion Videau. 2002. “Degree of Composition of
Highly Nonlinear Functions and Applications to Higher Order Differential
Cryptanalysis.” In *Advances in Cryptology – EUROCRYPT 2002*,
2332:518–33. LNCS. Springer.

</div>

<div id="ref-square1997" class="csl-entry">

Daemen, Joan, Lars R. Knudsen, and Vincent Rijmen. 1997. “The Block
Cipher Square.” In *Fast Software Encryption – FSE 1997*, 1267:149–65.
LNCS. Springer.

</div>

<div id="ref-dinur2009" class="csl-entry">

Dinur, Itai, and Adi Shamir. 2009. “Cube Attacks on Tweakable Black Box
Polynomials.” In *Advances in Cryptology – EUROCRYPT 2009*, 5479:278–99.
LNCS. Springer.

</div>

<div id="ref-eskandari2018" class="csl-entry">

Eskandari, Zahra, Andreas Brasen Kidmose, Stefan Kölbl, and Tyge
Tiessen. 2019. “Finding Integral Distinguishers with Ease.” In *Selected
Areas in Cryptography – SAC 2018*. Vol. 11349. LNCS. Springer.

</div>

<div id="ref-hadipour2022" class="csl-entry">

Hadipour, Hosein, and Maria Eichlseder. 2022. “Integral Cryptanalysis of
WARP Based on Monomial Prediction.” *IACR Transactions on Symmetric
Cryptology* 2022 (2).

</div>

<div id="ref-hao2020" class="csl-entry">

Hao, Yonglin, Gregor Leander, Willi Meier, Yosuke Todo, and Qingju Wang.
2020. “Modeling for Three-Subset Division Property Without Unknown
Subset.” In *Advances in Cryptology – EUROCRYPT 2020*, 12105:466–95.
LNCS. Springer.

</div>

<div id="ref-hebborn2020" class="csl-entry">

Hebborn, Phil, Baptiste Lambin, Gregor Leander, and Yosuke Todo. 2020.
“Lower Bounds on the Degree of Block Ciphers.” In *Advances in
Cryptology – ASIACRYPT 2020*, 12491:537–66. LNCS. Springer.

</div>

<div id="ref-hebborn2021" class="csl-entry">

———. 2021. “Strong and Tight Security Guarantees Against Integral
Distinguishers.” In *Advances in Cryptology – ASIACRYPT 2021*. Vol.
13090. LNCS. Springer.

</div>

<div id="ref-hu2020mp" class="csl-entry">

Hu, Kai, Siwei Sun, Meiqin Wang, and Qingju Wang. 2020. “An Algebraic
Formulation of the Division Property: Revisiting Degree Evaluations,
Cube Attacks, and Key-Independent Sums.” In *Advances in Cryptology –
ASIACRYPT 2020*, 12491:446–76. LNCS. Springer.

</div>

<div id="ref-huwang2019" class="csl-entry">

Hu, Kai, and Meiqin Wang. 2019. “Automatic Search for a Variant of
Division Property Using Three Subsets.” In *Topics in Cryptology –
CT-RSA 2019*, 11405:412–32. LNCS. Springer.

</div>

<div id="ref-hu2020linear" class="csl-entry">

Hu, Kai, Qingju Wang, and Meiqin Wang. 2020. “Finding Bit-Based Division
Property for Ciphers with Complex Linear Layers.” *IACR Transactions on
Symmetric Cryptology* 2020 (1).

</div>

<div id="ref-huyap2024" class="csl-entry">

Hu, Kai, and Trevor Yap. 2024. “Perfect Monomial Prediction for Modular
Addition.” *IACR Transactions on Symmetric Cryptology*.

</div>

<div id="ref-dipper2026" class="csl-entry">

Huseynli, Ali, Yadigar Imamverdiyev, and Jalal Alizadeh. 2026. “Dipper:
A Lightweight Hybrid SPN–ARX Block Cipher.” *Cryptography* 10 (4): 52.
<https://doi.org/10.3390/cryptography10040052>.

</div>

<div id="ref-pysat2018" class="csl-entry">

Ignatiev, Alexey, Antonio Morgado, and Joao Marques-Silva. 2018. “PySAT:
A Python Toolkit for Prototyping with SAT Oracles.” In *Theory and
Applications of Satisfiability Testing – SAT 2018*, 10929:428–37. LNCS.
Springer.

</div>

<div id="ref-knudsen1994" class="csl-entry">

Knudsen, Lars R. 1995. “Truncated and Higher Order Differentials.” In
*Fast Software Encryption – FSE 1994*, 1008:196–211. LNCS. Springer.

</div>

<div id="ref-knudsen2002integral" class="csl-entry">

Knudsen, Lars R., and David Wagner. 2002. “Integral Cryptanalysis.” In
*Fast Software Encryption – FSE 2002*, 2365:112–27. LNCS. Springer.

</div>

<div id="ref-kummer1852" class="csl-entry">

Kummer, Ernst Eduard. 1852. “Über Die Ergänzungssätze Zu Den Allgemeinen
Reciprocitätsgesetzen.” *Journal für Die Reine Und Angewandte
Mathematik* 44: 93–146.

</div>

<div id="ref-lai1994" class="csl-entry">

Lai, Xuejia. 1994. “Higher Order Derivatives and Differential
Cryptanalysis.” In *Communications and Cryptography: Two Sides of One
Tapestry*, 227–33. Springer.

</div>

<div id="ref-lipmaa2001" class="csl-entry">

Lipmaa, Helger, and Shiho Moriai. 2002. “Efficient Algorithms for
Computing Differential Properties of Addition.” In *Fast Software
Encryption – FSE 2001*, 2355:336–50. LNCS. Springer.

</div>

<div id="ref-lucks2001" class="csl-entry">

Lucks, Stefan. 2002. “The Saturation Attack – a Bait for Twofish.” In
*Fast Software Encryption – FSE 2001*, 2355:1–15. LNCS. Springer.

</div>

<div id="ref-sun2017sat" class="csl-entry">

Sun, Ling, Wei Wang, Ru Liu, and Meiqin Wang. 2017. “Automatic Search of
Bit-Based Division Property for ARX Ciphers and Word-Based Division
Property.” In *Advances in Cryptology – ASIACRYPT 2017*, 10624:128–57.
LNCS. Springer.

</div>

<div id="ref-sun2016arx" class="csl-entry">

Sun, Ling, Wei Wang, and Meiqin Wang. 2016. “MILP-Aided Bit-Based
Division Property for ARX-Based Block Cipher.” Cryptology ePrint
Archive, Paper 2016/1101. <https://eprint.iacr.org/2016/1101>.

</div>

<div id="ref-todo2015misty" class="csl-entry">

Todo, Yosuke. 2015a. “Integral Cryptanalysis on Full MISTY1.” In
*Advances in Cryptology – CRYPTO 2015*, 9215:413–32. LNCS. Springer.

</div>

<div id="ref-todo2015" class="csl-entry">

———. 2015b. “Structural Evaluation by Generalized Integral Property.” In
*Advances in Cryptology – EUROCRYPT 2015*, 9056:287–314. LNCS. Springer.

</div>

<div id="ref-todo2017cube" class="csl-entry">

Todo, Yosuke, Takanori Isobe, Yonglin Hao, and Willi Meier. 2017. “Cube
Attacks on Non-Blackbox Polynomials Based on Division Property.” In
*Advances in Cryptology – CRYPTO 2017*, 10403:250–79. LNCS. Springer.

</div>

<div id="ref-todo2016bit" class="csl-entry">

Todo, Yosuke, and Masakatu Morii. 2016. “Bit-Based Division Property and
Application to Simon Family.” In *Fast Software Encryption – FSE 2016*,
9783:357–77. LNCS. Springer.

</div>

<div id="ref-wallen2003" class="csl-entry">

Wallén, Johan. 2003. “Linear Approximations of Addition Modulo $2^n$.”
In *Fast Software Encryption – FSE 2003*, 2887:261–73. LNCS. Springer.

</div>

<div id="ref-wang2018cube" class="csl-entry">

Wang, Qingju, Yonglin Hao, Yosuke Todo, Chaoyun Li, Takanori Isobe, and
Willi Meier. 2018. “Improved Division Property Based Cube Attacks
Exploiting Algebraic Properties of Superpoly.” In *Advances in
Cryptology – CRYPTO 2018*, 10991:275–305. LNCS. Springer.

</div>

<div id="ref-xiang2016milp" class="csl-entry">

Xiang, Zejun, Wentao Zhang, Zhenzhen Bao, and Dongdai Lin. 2016.
“Applying MILP Method to Searching Integral Distinguishers Based on
Division Property for 6 Lightweight Block Ciphers.” In *Advances in
Cryptology – ASIACRYPT 2016*, 10031:648–78. LNCS. Springer.

</div>

<div id="ref-zaba2008" class="csl-entry">

Z’aba, Muhammad Reza, Håvard Raddum, Matt Henricksen, and Ed Dawson.
2008. “Bit-Pattern Based Integral Attack.” In *Fast Software Encryption
– FSE 2008*, 5086:363–81. LNCS. Springer.

</div>

<div id="ref-zeng2024" class="csl-entry">

Zeng, Fanyang, and Tian Tian. 2024. “On the Security Bounds for Block
Ciphers Without Whitening Key Addition Against Integral Distinguishers.”
In *Information Security and Privacy – ACISP 2024*. Vol. 14895. LNCS.
Springer.

</div>

<div id="ref-zhang2019" class="csl-entry">

Zhang, Wenying, and Vincent Rijmen. 2019. “Division Cryptanalysis of
Block Ciphers with a Binary Diffusion Layer.” *IET Information Security*
13 (2).

</div>

</div>

[^1]: Corresponding author. ORCID 0009-0003-4959-2887.
