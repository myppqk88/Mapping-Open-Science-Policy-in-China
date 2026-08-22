"""
Figure 5.2: Stage-aggregated entry share by category.
Line chart with 8 lines (one per category) across 3 policy stages.
Category colours match fig5_1 and fig4_1.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import apply_style, OUT_DIR, COLORS

apply_style()

ROOT = Path(__file__).resolve().parent.parent
DATA_XLSX = ROOT / "02_data" / "final_entries" / "开放科学政策数据_最终版_v5.3.xlsx"

entries = pd.read_excel(DATA_XLSX, sheet_name="政策条目")
entries = entries[entries["issue_year"] >= 1998].copy()

# Stage assignment
def stage_of(y):
    if y <= 2005: return "S1"
    if y <= 2015: return "S2"
    if y <= 2025: return "S3"
    return None
entries["stage"] = entries["issue_year"].apply(stage_of)
entries = entries[entries["stage"].notna()]

# Categories order matches fig5_1
CAT_ORDER = ["OA", "OD", "OSS", "OERs", "CS", "OPR", "OI", "ORM"]
PALETTE = ["#2E5A88","#C46A3B","#5B7D4F","#7B4A8C",
           "#B45F4A","#3F7B95","#A78940","#6D4C7D"]
CAT_COLOR = dict(zip(CAT_ORDER, PALETTE))

# Expand multi-cat entries
e_main = entries[entries["category_codes"] != "OS_general"].copy()
exploded = e_main.assign(cat=e_main["category_codes"].str.split("|")).explode("cat")

# Compute stage x category share
stages = ["S1", "S2", "S3"]
stage_labels = ["S1\n(1998–2005)", "S2\n(2006–2015)", "S3\n(2016–2025)"]
share = {cat: [] for cat in CAT_ORDER}
stage_n = {}
for s in stages:
    sub = exploded[exploded["stage"] == s]
    stage_n[s] = len(sub)
    for cat in CAT_ORDER:
        share[cat].append((sub["cat"] == cat).sum() / len(sub) * 100)

# ---- Plot ----
fig, ax = plt.subplots(figsize=(9.5, 6.0))
fig.subplots_adjust(left=0.09, right=0.83, top=0.94, bottom=0.12)

x = np.arange(len(stages))
INK = COLORS["ink"]
RULE = COLORS["rule"]

ax.grid(axis="y", linestyle="--", linewidth=0.5, color=RULE, alpha=0.65, zorder=0)
ax.set_axisbelow(True)

# Sort categories by their max value across stages, so high-share ones plot on top
order_by_max = sorted(CAT_ORDER, key=lambda c: max(share[c]), reverse=True)

for cat in order_by_max:
    ax.plot(x, share[cat], marker="o", markersize=7,
            linewidth=2.0, color=CAT_COLOR[cat],
            markerfacecolor="white", markeredgewidth=1.6,
            markeredgecolor=CAT_COLOR[cat], label=cat, zorder=3)
    # Annotate end-point values for top 5 categories
    if cat in ["OERs", "OI", "OD", "CS", "OSS"]:
        for xi, val in zip(x, share[cat]):
            ax.text(xi + 0.04, val + 0.4, "{:.1f}".format(val),
                    fontsize=8.5, color=CAT_COLOR[cat], zorder=4,
                    fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(stage_labels, fontsize=10.5)
ax.set_ylabel("Entry share (%)", fontsize=11, color=INK)
ax.set_xlim(-0.25, len(stages) - 0.75)

ymax = max(max(share[c]) for c in CAT_ORDER) * 1.10
ax.set_ylim(-3, ymax)
ax.tick_params(axis="both", length=2.5, labelsize=10)

# Stage n annotations under x-labels
for xi, s in enumerate(stages):
    ax.text(xi, -0.085, "n = {:,}".format(stage_n[s]),
            transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=8.5,
            style="italic", color=COLORS["muted"])

# Legend outside the plot area on the right
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5),
          frameon=False, fontsize=10, handlelength=1.6,
          title="Category", title_fontsize=10.5)

NAME = "fig5_2_stage_category"
fig.savefig(OUT_DIR / (NAME + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_DIR / (NAME + ".pdf"), bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Saved:", NAME)
