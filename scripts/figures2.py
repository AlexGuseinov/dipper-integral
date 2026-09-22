"""Figure: data complexity of the smallest certified cube per round (ablation)."""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, ".")
from dipper.cipher import PERM_INV

blue, orange, aqua, ink, muted, grid = "#2a78d6", "#eb6834", "#1baf7a", "#3d3d3a", "#8a8983", "#e6e5df"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

# ---------------------------------------------------------------- ablation
# smallest certified cube dimension found per round (Table "frontier")
front = {
    "Dipper": ({3: 2, 4: 4, 5: 16, 6: 60}, 7, blue, "o"),
    r"Dipper$^{\oplus}$ (addition $\to$ XOR)": ({5: 7, 6: 22, 7: 44, 8: 59, 9: 63}, 10, orange, "s"),
    r"Dipper$^{\varnothing}$ (addition removed)": ({5: 3, 6: 8, 7: 15, 8: 48, 9: 59, 10: 63}, 11, aqua, "^"),
}
fig, ax = plt.subplots(figsize=(5.4, 3.2))
for name, (d, stop, col, mk) in front.items():
    xs = sorted(d); ys = [d[x] for x in xs]
    ax.plot(xs, ys, color=col, lw=2, marker=mk, ms=5, label=name)
    ax.plot([xs[-1], stop], [ys[-1], 66], color=col, lw=1.2, ls=(0, (2, 2)))
    ax.plot([stop], [66], marker="x", ms=7, mew=2, color=col, clip_on=False)
ax.axhline(64, color=ink, lw=0.8, ls=":")
ax.text(2.55, 64.8, "full codebook ($2^{64}$)", fontsize=7.5, color=ink, va="bottom")
ax.plot([], [], ls="none", marker="x", ms=6, mew=2, color=muted, label="no cube certified (> full codebook)")
ax.set_xlabel("rounds $r$")
ax.set_ylabel(r"data: $\log_2$(chosen plaintexts)")
ax.set_xticks(range(3, 12)); ax.set_xlim(2.5, 11.5); ax.set_ylim(0, 70)
ax.grid(axis="y", color=grid, lw=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
fig.tight_layout()
fig.savefig("paper/fig_ablation.pdf"); fig.savefig("paper/fig_ablation.png", dpi=200)

print("ok")
