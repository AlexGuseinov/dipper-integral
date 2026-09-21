"""Documented attempt to PROVE monomial presence (exact non-balance) at the
7-round frontier via key-monomial parity (dipper/resolve.presence_witness)."""
import json, sys, time
sys.path.insert(0, ".")
from dipper.resolve import presence_witness
out = []
for r, p, j in ((7, 0, 0), (7, 5, 17)):
    t = time.time()
    ok, info = presence_witness(set(range(64)) - {p}, r, j, tries=20, cap=20000)
    row = dict(rounds=r, constant_bit=p, bit=j, proved_present=ok, info=info, seconds=round(time.time() - t, 1))
    out.append(row); print(row); sys.stdout.flush()
json.dump(out, open("results/step6_presence_attempt.json", "w"), indent=1)
