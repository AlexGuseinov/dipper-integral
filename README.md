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
| Longest certified property | **6 rounds** (9 balanced bits with 2^63 data; 6 bits with 2^60) |
| 7 rounds | no certificate for **any** cube (exhaustive within the model, monotonicity lemma) |
| Free final round (no whitening key) | every r-round property is an (r+1)-round property of T⁻¹(C) → 7-round distinguisher |
| Key recovery | 8 rounds, 4 bits of RK₈, 2^63 chosen plaintexts (theoretical; validated at small scale) |
| Ablation: ⊞ → ⊕ / addition removed | 9 / 10 certified rounds (vs 6) |
| Exact MP vs gate-level MP vs classical BDP | identical certificates on every instance |
| Mechanism | at the 6-round boundary every balanced bit comes from the retained words B, D |
| Specification check | 128-bit vectors need RK = K[63:0] (text says K[127:64]); 96-bit vectors not reproducible |

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

## How to read a result

* **certified / balanced** — the SAT model is unsatisfiable: the cube sum is 0
  for all constants and all (independent) round keys. Sound.
* **unknown** — a trail exists. Says nothing about the cipher.
* **timeout** — none left in the reported runs (conflict budget 1e5, retry 5e6).

## Citation

If you use this code, please cite the paper above and the Dipper paper.

MIT License.
