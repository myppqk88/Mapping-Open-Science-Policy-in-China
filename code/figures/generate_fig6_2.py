"""
Figure 6.2: Heatmap of entry-level category shares (%) across four
economic regions (East / Central / West / Northeast).
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import (apply_style, CATEGORIES, CAT_CODES, REGIONS,
                    REGION_ORDER, REGION_COLORS, province_region,
                    OUT_DIR, COLORS)

apply_style()

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_XLSX = ROOT / "02_data" / "final_entries" / "开放科学政策数据_最终版_v5.3.xlsx"

# ---- Load ----
entries = pd.read_excel(ENTRIES_XLSX)
# Keep only province + city level (exclude central, joint cross-province)
entries = entries[entries["governance_level"].isin(["省级", "地市级"])]

# Take primary province only (first one if joint)
entries = entries.assign(prov=entries["province_raw"].astype(str).str.split(";").str[0])
# Drop NaN/empty
entries = entries[entries["prov"].str.len() > 0]
entries["region"] = entries["prov"].apply(province_region)
entries = entries[entries["region"].isin(REGION_ORDER)]

# Region totals
# Expand multi-category entries (consistent with fig4_1)
entries_main = entries[entries["category_codes"] != "OS_general"].copy()
exploded = entries_main.assign(cat=entries_main["category_codes"].str.split("|")).explode("cat")

region_totals = exploded.groupby("region").size().reindex(REGION_ORDER)

# Category x Region matrix (expanded entry counts), pivot to share
mat = exploded.groupby(["region", "cat"]).size().unstack(fill_value=0)
mat = mat.reindex(REGION_ORDER)[CAT_CODES]
share = mat.div(region_totals, axis=0) * 100        # row-wise share %
share = share.reindex(REGION_ORDER)                 # ensure ordering

# ---- Plot ----
fig = plt.figure(figsize=(11.0, 5.4))
gs = fig.add_gridspec(
    nrows=1, ncols=1,
    left=0.13, right=0.87, top=0.95, bottom=0.10,
)
ax = fig.add_subplot(gs[0, 0])

cmap = LinearSegmentedColormap.from_list(
    "blues_nature",
    ["#FFFFFF", "#D8E4F0", "#A8C0DC", "#6E94BE", "#3D6FA0", "#1F4A7B"],
)

vmax = float(np.max(share.values))
im = ax.imshow(share.values, cmap=cmap, vmin=0, vmax=vmax, aspect="auto")

# Cell annotations
for i in range(share.shape[0]):
    for j in range(share.shape[1]):
        v = share.values[i, j]
        c = "white" if v > vmax * 0.55 else "#1A2B45"
        ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                fontsize=10.5, color=c, fontweight="bold")

# Ticks
ax.set_xticks(range(len(CAT_CODES)))
ax.set_yticks(range(len(REGION_ORDER)))
ax.set_xticklabels(CAT_CODES, fontsize=11)
ax.set_yticklabels(REGION_ORDER, fontsize=11)
ax.tick_params(length=0)

# Coloured tick labels for region rows
for label, region in zip(ax.get_yticklabels(), REGION_ORDER):
    label.set_color(REGION_COLORS[region])
    label.set_fontweight("bold")

# Cell borders — only across the heatmap rectangle (no extension to the
# right-hand 'n=...' annotation area). Use ax.plot with explicit endpoints.
ncols, nrows = share.shape[1], share.shape[0]
GRID_COLOR = "#5A6B82"
GRID_LW    = 0.7
for k in np.arange(-0.5, ncols + 0.5, 1):
    ax.plot([k, k], [-0.5, nrows - 0.5],
            color=GRID_COLOR, linewidth=GRID_LW, clip_on=False)
for k in np.arange(-0.5, nrows + 0.5, 1):
    ax.plot([-0.5, ncols - 0.5], [k, k],
            color=GRID_COLOR, linewidth=GRID_LW, clip_on=False)

# Region size annotations on right
for i, region in enumerate(REGION_ORDER):
    n = int(region_totals[region])
    ax.text(share.shape[1] - 0.4, i, f"n = {n:,}",
            ha="left", va="center", fontsize=9.5, style="italic",
            color=COLORS["muted"])

ax.set_xlim(-0.5, share.shape[1] - 0.5 + 1.3)

# Colourbar
cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.13, shrink=0.85)
cbar.set_label("Category share (%)", fontsize=10.5, color=COLORS["ink"])
cbar.outline.set_visible(False)
cbar.ax.tick_params(labelsize=9.5)

NAME = "fig6_2_regional_category"
fig.savefig(OUT_DIR / (NAME + ".png"), dpi=300, bbox_inches="tight",
            facecolor="white")
fig.savefig(OUT_DIR / (NAME + ".pdf"), bbox_inches="tight",
            facecolor="white")
plt.close(fig)
print("Saved:", NAME)
