PY ?= python3

.PHONY: test reproduce quick summary paper springer clean certificates tools

test:            ## fast validation: test vectors, inverses, local models, model soundness
	$(PY) -m tests.test_vectors
	$(PY) -m tests.test_fast
	$(PY) -m tests.test_local_models
	$(PY) -m tests.test_models_small

quick: test      ## ~15 min: Step 1 reproduction, benchmark, Dipper maximal cubes
	$(PY) scripts/step1_empirical_integral.py add 7 1000
	$(PY) scripts/benchmark_spn.py
	$(PY) scripts/step3_maximal_cubes.py add
	$(PY) scripts/step3_maximal_cubes.py add 8,9 mp,bdp

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
	$(PY) scripts/step6_degree.py add 7
	$(PY) scripts/step6_degree.py xor,none 11
	$(PY) scripts/step6_gap_resolution.py
	$(PY) scripts/step6_gap_small.py 800
	$(PY) scripts/step6_presence_attempt.py
	$(PY) -m tests.test_count             # trail counting vs ANF (slow: ~2 h at 3 rounds)
	$(PY) scripts/step14_forced_masks.py
	$(PY) scripts/step16_projection_check.py
	$(PY) scripts/step17_presence_probe.py
	$(PY) scripts/step18_hardbits.py 7,20,23,34,37,45,54
	$(PY) scripts/step22_gap_presence.py results/step4_tightness_add.json
	$(PY) scripts/step21_presence_all_p.py $$(seq -s, 1 2 63) results/step21_presence_odd_p.json
	$(PY) scripts/step21_presence_all_p.py $$(seq -s, 2 2 63) results/step21_presence_even_p.json
	$(PY) scripts/step23_gap_witness_keys.py 60000
	$(PY) scripts/step23b_gap_witness_lowweight.py 24
	$(PY) scripts/step25_exact_degree.py "add:1,2,3,4,5,6;xor:1,2,3,4,5,6" results/step25_degree_part1.json
	$(PY) scripts/step25_exact_degree.py "none:1,2,3,4,5,6,7,8,9,10,11;xor:7,8,9,10,11" results/step25_degree_part2.json
	REDO=1 MAX_U=80 $(PY) scripts/step25_exact_degree.py "add:1,2,3;xor:3,4,5,6" results/step25_degree_part1.json
	$(PY) scripts/step25c_degree_hard.py
	DEEP=1 DEEP_FROM=0 DEEP_TO=12 $(PY) scripts/step25c_degree_hard.py
	$(PY) scripts/step25b_anf_degree_r1.py 6,7,20,36,39
	$(PY) scripts/step25d_degree_summary.py
	$(PY) scripts/step26_min_cube.py add 6
	$(PY) scripts/step26_min_cube.py xor 9
	$(PY) scripts/step26_min_cube.py none 10
	SAMPLES=200 $(PY) scripts/step27_linear_combinations.py $$(seq -s, 0 63) results/step27_lc_all.json
	$(PY) scripts/step27b_consolidate.py
	$(PY) scripts/step27c_verify.py $$(seq -s, 0 63) results/step27c_verify_all.json   # independent verifier
	$(PY) scripts/step27c_merge.py
	$(PY) scripts/step28_keyschedule_probe.py
	$(PY) scripts/figures.py
	$(PY) scripts/figures2.py
	$(PY) scripts/summarize.py

summary:
	$(PY) scripts/summarize.py

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode paper.tex

springer:        ## journal version (needs sn-jnl.cls + sn-mathphys-num.bst in paper/springer/)
	cd paper && $(PY) tools/make_springer.py

clean:
	cd paper && latexmk -C

# External tools for checkable certificates (CaDiCaL + drat-trim), built locally
TOOLS ?= .tools
tools:
	mkdir -p $(TOOLS)
	test -d $(TOOLS)/cadical || git clone --depth 1 https://github.com/arminbiere/cadical.git $(TOOLS)/cadical
	test -x $(TOOLS)/cadical/build/cadical || (cd $(TOOLS)/cadical && ./configure && make -j2)
	test -d $(TOOLS)/drat-trim || git clone --depth 1 https://github.com/marijnheule/drat-trim.git $(TOOLS)/drat-trim
	test -x $(TOOLS)/drat-trim/drat-trim || (cd $(TOOLS)/drat-trim && make)

CAD = $(TOOLS)/cadical/build/cadical
DT  = $(TOOLS)/drat-trim/drat-trim
certificates: tools   ## DRAT proofs + independently validated trails for all boundary results (~2 h on 2 cores)
	$(PY) scripts/step7_certificates.py $(CAD) $(DT) certificates
	$(PY) scripts/step30_drat_lincomb.py $(CAD) $(DT) $$(seq -s, 0 63) results/step30_drat_lincomb_all.json
	$(PY) scripts/step30_merge.py
	$(PY) scripts/step31_drat_presence.py $(CAD) $(DT) r7 results/step31_drat_r7.json
	$(PY) scripts/step31_drat_presence.py $(CAD) $(DT) gap results/step31_drat_gap.json
	$(PY) scripts/step31_drat_presence.py $(CAD) $(DT) degree results/step31_drat_degree.json
	$(PY) scripts/step31_drat_presence.py - - summary results/step31_drat_summary.json
	$(PY) scripts/step32_drat_degree_upper.py $(CAD) $(DT) add,xor,none results/step32_drat_degree_upper.json
	$(PY) scripts/step33_drat_min_cubes.py $(CAD) $(DT)
