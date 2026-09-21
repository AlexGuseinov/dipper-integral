PY ?= python3

.PHONY: test reproduce quick summary paper clean

test:            ## fast validation: test vectors, inverses, local models, model soundness
	$(PY) -m tests.test_vectors
	$(PY) -m tests.test_fast
	$(PY) -m tests.test_local_models
	$(PY) -m tests.test_models_small

quick: test      ## ~15 min: Step 1 reproduction, benchmark, Dipper maximal cubes
	$(PY) scripts/step1_empirical_integral.py add 7 1000
	$(PY) scripts/benchmark_spn.py
	$(PY) scripts/step3_maximal_cubes.py add

reproduce: quick ## everything (several hours on 2 cores)
	$(PY) scripts/step1_empirical_integral.py xor 8 400
	$(PY) scripts/step1_empirical_integral.py none 9 400
	$(PY) scripts/step3_maximal_cubes.py xor,none
	$(PY) scripts/step3_maximal_cubes.py none 8,9,10,11 mp,bdp
	$(PY) scripts/step3_maximal_cubes.py xor 8,9,10 mp,bdp
	$(PY) scripts/step3_frontier.py add mp 3,4,5,6
	$(PY) scripts/step3_frontier.py none mp 5,6,7,8,9,10
	$(PY) scripts/step3_frontier.py xor mp 5,6,7,8,9
	$(PY) scripts/step3_frontier_empirical.py
	$(PY) scripts/step4_tightness.py add
	$(PY) scripts/step4_model_comparison.py add
	$(PY) scripts/step4_parity_attempt.py
	$(PY) scripts/step5_attack_smallscale.py
	$(PY) scripts/step5_key_recovery.py
	$(PY) scripts/summarize.py

summary:
	$(PY) scripts/summarize.py

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode paper.tex

clean:
	cd paper && latexmk -C
