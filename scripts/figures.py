"""Figure: algebraic degree per round (proven lower bounds; they equal the certified
upper bounds for 1843 of the 1856 (variant, round, bit) cases, see step25)."""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, ".")
from dipper.cipher import PERM_INV

WORD = "DCBA"
summ = json.load(open("results/step25_degree_summary.json"))["per_bit"]
def as_bounds(mode, rmax):
    return {str(r): {"per_bit": {str(j): summ[f"{mode}|{r}"][str(j)]["lower"] for j in range(64)}}
            for r in range(1, rmax + 1) if f"{mode}|{r}" in summ}
add = as_bounds("add", 7)
var = {"xor": as_bounds("xor", 11), "none": as_bounds("none", 11)}


def series(d, words=None, rmax=11):
    xs, ys = [], []
    for r in range(1, rmax + 1):
        if str(r) not in d:
            v = 63.0                              # bound saturated (all bits 63)
        else:
            pb = d[str(r)]["per_bit"]
            bits = [int(j) for j in pb if words is None or WORD[PERM_INV[int(j)] // 16] in words]
            v = sum(min(pb[str(j)], 63) for j in bits) / len(bits)
        xs.append(r); ys.append(v)
    return xs, ys


plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(5.2, 3.1))
blue, orange, aqua, ink, grid = "#2a78d6", "#eb6834", "#1baf7a", "#3d3d3a", "#e6e5df"
x, y = series(add, "AC", 7); ax.plot(x, y, color=blue, lw=2, marker="o", ms=4, label=r"Dipper, words $A,C$ (added)")
x, y = series(add, "BD", 7); ax.plot(x, y, color=blue, lw=2, ls="--", marker="o", ms=4, mfc="white", label=r"Dipper, words $B,D$ (retained)")
x, y = series(var["xor"]); ax.plot(x, y, color=orange, lw=2, marker="s", ms=4, label=r"Dipper$^{\oplus}$ (all words)")
x, y = series(var["none"]); ax.plot(x, y, color=aqua, lw=2, marker="^", ms=4, label=r"Dipper$^{\varnothing}$ (all words)")
ax.axhline(63, color=ink, lw=0.8, ls=":")
ax.text(11, 64.2, "63 (max. for a permutation)", ha="right", va="bottom", fontsize=7.5, color=ink)
ax.set_xlabel("rounds $r$"); ax.set_ylabel("mean algebraic degree")
ax.set_xticks(range(1, 12)); ax.set_ylim(0, 70)
ax.grid(axis="y", color=grid, lw=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
fig.tight_layout()
fig.savefig("paper/fig_degree.pdf"); fig.savefig("paper/fig_degree.png", dpi=200)
print("ok")
