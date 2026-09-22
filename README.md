# Certified integral properties of the Dipper block cipher

Code, data and paper for **"Certified Integral Properties of the Dipper Block
Cipher: Monomial-Trail Analysis and the Role of the Half-State Modular Addition"**
(A. Huseynli, Y. Imamverdiyev, J. Alizadeh).

Dipper ([Cryptography 10(4):52, 2026](https://doi.org/10.3390/cryptography10040052))
is a 64-bit hybrid SPN–ARX block cipher. Its designers bounded integral
distinguishers *experimentally* at 5 rounds. This repository replaces that
evidence with SAT-based certificates that hold **for every choice of round keys**.

## Main results

| | Result |
|---|---|
| Published 5-round word-saturation integrals | reproduced; certified for all keys |
| Longest certified property | **6 rounds** (9 balanced bits with 2^63 data; 6 bits with the smallest cube found, 2^60) |
| 7 rounds | no certificate for **any** cube (exhaustive within the model, monotonicity lemma); for every cube keeping bit 0 constant, **all 64 output bits proven unbalanced** (presence proofs, odd trail counts) |
| Persistent gap bits | all 46 bits that were zero in 3200 random-key trials without a certificate are **proven unbalanced** → certificates are exact on all 112 tested instances |
| Free final round (no whitening key) | every r-round property is an (r+1)-round property of T⁻¹(C) → 7-round distinguisher |
| Key filtering (secondary) | proposed 1-round extension recovering 4 bits of RK₈ with ~2^63 data (extrapolated; not a validated attack) |
| Ablation: ⊞ → ⊕ / addition removed | 9 / 10 certified rounds (vs 6) |
| MP-EL (existence, exact local rules) vs gate-level MP vs classical BDP | identical certificates on every tested instance |
| Mechanism | at the 6-round boundary every balanced bit comes from the retained words B, D |
| Degree lemma | bit i of x⊞y has algebraic degree exactly i+1 (proved; checked n ≤ 8) |
| Degree UPPER bounds | all bounds are 63 from r=6 (Dipper) vs r=9 / 10 (XOR / no-add); retained words lag ~1 round |
| Checkable artifacts | 138 distinct DRAT proofs checked by drat-trim; 12 288 SAT trails validated independently (`make certificates`); 110 presence-proof trails validated; trail counting cross-checked with the ANF |
| Key-schedule corrections | paper text vs. spec/reference code: 128-bit RK = K[63:0] (not K[127:64]); 96-bit S-boxes at k4[7:4], k1[7:4] (not top nibbles). All 4 vectors reproduced |

Full numbers: [`results/RESULTS.md`](results/RESULTS.md), raw data: `results/*.json`,
paper: [`paper/paper.pdf`](paper/paper.pdf) (LaTeX source `paper/paper.tex`,
Markdown `paper/paper.md`).

## Layout

```
dipper/            library
  cipher.py        reference implementation (+ XOR / no-addition analysis variants)
  fast.py          numpy engine for cube sums (checked against cipher.py)
  anf.py           exact ANF / monomial tables (S-box, modular addition)
  models.py        SAT models: 'mp' (exact), 'mpc' (gate-level MP), 'bdp' (classical)
  exact.py         trail enumeration with parity per key monomial
  resolve.py       key-support / key-degree bounds, exact zero test, presence attempt
scripts/           one script per experiment (step1 … step5), summarize.py
tests/             test vectors, inverses, exhaustive local-model checks, soundness
results/           JSON outputs, logs, RESULTS.md, step1_spec_check.md
paper/             paper.tex, refs.bib, paper.md, paper.pdf
```

## Reproduce

```bash
pip install -r requirements.txt      # numpy, python-sat (NOT the 'pysat' package)
make test        # ~1 min: vectors, exhaustive local checks, soundness vs experiment
make quick       # ~10 min: Step 1, GIFT/PRESENT benchmark, Dipper maximal cubes
make reproduce   # all tables (several hours on 2 cores)
make paper       # builds paper/paper.pdf
```

Tested with Python 3.11, numpy 2.4, python-sat 1.9 (CaDiCaL 1.5.3). Experiments
use fixed seeds; SAT results do not depend on solver randomness (UNSAT = certificate).

## Certificates archive

The CNF files and DRAT proofs (~60 MB, `certificates/`) are not tracked in git.
Attach `dipper-integral-certificates.zip` to a GitHub release (or Zenodo) and
link it here; `make certificates` regenerates and re-checks everything
(builds CaDiCaL and drat-trim into `.tools/`).

## How to read a result

* **certified / balanced** — the SAT model is unsatisfiable: the cube sum is 0
  for all constants and all (independent) round keys. Sound.
* **unknown** — a trail exists. Says nothing about the cipher.
* **timeout** — none left in the reported runs (conflict budget 1e5, retry 5e6).
* **degree bound D** — certified upper bound deg ≤ D; never an actual degree.

## Citation

If you use this code, please cite the paper above and the Dipper paper.

MIT License.
