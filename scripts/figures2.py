"""Additional explanatory figures: ablation frontier, state map, tightness."""
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

# ---------------------------------------------------------------- state map
bal6 = [1, 18, 19, 24, 41, 48, 51, 56, 58]          # six-round balanced bits, p in {4,6,7}
WORD = "DCBA"
hit = {(WORD[PERM_INV[j] // 16], PERM_INV[j] % 16) for j in bal6}
fig, ax = plt.subplots(figsize=(5.6, 2.2))
rows = [("A", True), ("B", False), ("C", True), ("D", False)]
for r, (w, added) in enumerate(rows):
    y = 3 - r
    for b in range(16):
        x = 15 - b
        on = (w, b) in hit
        fc = blue if on else ("#dcdbd5" if added else "white")
        ax.add_patch(Rectangle((x + 0.06, y + 0.08), 0.88, 0.84, fc=fc,
                               ec="#b9b8b1" if not on else blue, lw=0.8))
        if on:
            ax.text(x + 0.5, y + 0.5, str(b), ha="center", va="center", fontsize=7, color="white",
                    fontweight="bold")
    lab = f"{w}: output of addition" if added else f"{w}: retained word"
    ax.text(-0.3, y + 0.5, w, ha="right", va="center", fontsize=10, fontweight="bold", color=ink)
    ax.text(16.3, y + 0.5, lab, ha="left", va="center", fontsize=7.5, color=muted)
ax.text(0.5, 4.25, "bit 15", fontsize=7, color=muted, ha="center")
ax.text(15.5, 4.25, "bit 0", fontsize=7, color=muted, ha="center")
ax.set_xlim(-1.2, 23.5); ax.set_ylim(-0.1, 4.6); ax.axis("off")
fig.tight_layout()
fig.savefig("paper/fig_state.pdf"); fig.savefig("paper/fig_state.png", dpi=200)

# ---------------------------------------------------------------- tightness
t = json.load(open("results/step4_tightness_add.json"))["rows"]
cert, gap, pers = {}, {}, {}
for row in t:
    r = row["rounds"]
    cert[r] = cert.get(r, 0) + row["certified"]
    gap[r] = gap.get(r, 0) + row["gap"]
    pers[r] = pers.get(r, 0) + row["gap_persistent"]
proved = json.load(open("results/step22_gap_presence.json"))["summary"]["odd_with_valid_witness"]
assert proved == sum(pers.values())
fig, ax = plt.subplots(figsize=(6.2, 2.4))
R = [2, 3, 4, 5]
for i, r in enumerate(R):
    tot = cert[r] + gap[r]
    parts = [(cert[r], blue, "certified (balanced for all keys)"),
             (gap[r] - pers[r], "#c9c8c1", "zero in 200 trials, nonzero later"),
             (pers[r], orange, "zero in all trials, proved unbalanced")]
    left = 0
    for v, col, lab in parts:
        w = 100 * v / tot
        if w > 0:
            ax.barh(i, w, left=left, color=col, height=0.62, edgecolor="white", linewidth=1.5,
                    label=lab if i == 0 else None)
        left += w
    extra = f"  ({pers[r]} proved unbalanced)" if pers[r] else ""
    ax.text(101.5, i, f"{tot} bits{extra}", va="center", fontsize=7.5, color=ink)
ax.set_yticks(range(len(R))); ax.set_yticklabels([f"r = {r}" for r in R])
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("share of the bits whose sum was zero in the first 200 trials (%)")
ax.grid(axis="x", color=grid, lw=0.8); ax.set_axisbelow(True)
ax.spines["bottom"].set_bounds(0, 100)
ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.45, -0.32), ncol=2)
fig.tight_layout()
fig.savefig("paper/fig_tight.pdf", bbox_inches="tight"); fig.savefig("paper/fig_tight.png", dpi=200, bbox_inches="tight")
print("ok")
