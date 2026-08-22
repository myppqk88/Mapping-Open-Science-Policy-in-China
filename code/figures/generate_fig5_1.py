"""
Figure 5.1: Annual trajectory of open-science policy files (top)
and entry counts by category (bottom 2x4), 1998-2025.
Each subplot is labelled (a)-(i) BELOW the chart.
Stage backgrounds use reduced opacity for readability.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import (apply_style, CATEGORIES, CAT_CODES, STAGES, OUT_DIR,
                    COLORS)

apply_style()

ROOT = Path(__file__).resolve().parent.parent
FILES_XLSX   = ROOT / "02_data" / "final_entries" / "政策文件表_v5.3.xlsx"
ENTRIES_XLSX = ROOT / "02_data" / "final_entries" / "开放科学政策数据_最终版_v5.3.xlsx"

files   = pd.read_excel(FILES_XLSX)
entries = pd.read_excel(ENTRIES_XLSX)

YR_LO, YR_HI = 1998, 2025
files   = files[(files["issue_year"] >= YR_LO) & (files["issue_year"] <= YR_HI)]
entries = entries[(entries["issue_year"] >= YR_LO) & (entries["issue_year"] <= YR_HI)]
years = np.arange(YR_LO, YR_HI + 1)

annual_files = files.groupby("issue_year").size().reindex(years, fill_value=0)
cat_annual = {}
for code, _ in CATEGORIES:
    s = entries[entries["category_codes"] == code].groupby("issue_year").size()
    cat_annual[code] = s.reindex(years, fill_value=0).values

STAGE_ALPHA = 0.35   # reduced opacity

fig = plt.figure(figsize=(14, 9.4))
gs = fig.add_gridspec(
    nrows=3, ncols=4, height_ratios=[1.55, 1, 1],
    hspace=0.75, wspace=0.30,
    left=0.06, right=0.98, top=0.97, bottom=0.07,
)

# ---------- Top panel (a) ----------
ax_top = fig.add_subplot(gs[0, :])
for sid, ys, ye, label, color in STAGES:
    ax_top.axvspan(ys - 0.5, ye + 0.5, color=color, alpha=STAGE_ALPHA, zorder=0)

ax_top.plot(years, annual_files.values, color=COLORS["primary"],
            linewidth=2.2, marker="o", markersize=4.5,
            markerfacecolor="white", markeredgewidth=1.4,
            markeredgecolor=COLORS["primary"], zorder=3)
ax_top.fill_between(years, annual_files.values, color=COLORS["primary"],
                    alpha=0.10, zorder=2)

peak_idx = int(np.argmax(annual_files.values))
peak_y, peak_v = int(years[peak_idx]), int(annual_files.values[peak_idx])

ax_top.set_xlim(YR_LO - 0.5, YR_HI + 0.5)
# Raise y-axis ceiling so peak annotation does not collide with stage label
y_top_max = annual_files.max() * 1.40
ax_top.set_ylim(0, y_top_max)

ax_top.annotate(f"Peak: {peak_v:,} ({peak_y})",
                xy=(peak_y, peak_v),
                xytext=(peak_y - 6, peak_v + y_top_max * 0.10),
                fontsize=10.5, color=COLORS["ink"], ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", color=COLORS["muted"], lw=0.8))

ax_top.set_xlabel("Year", fontsize=11, color=COLORS["ink"])
ax_top.set_ylabel("Number of policy files", fontsize=11, color=COLORS["ink"])
ax_top.grid(axis="y", linestyle="--", linewidth=0.6,
            color=COLORS["rule"], alpha=0.7)

# Stage labels near the very top (clearly above the line)
stage_y = y_top_max * 0.96
for sid, ys, ye, label, color in STAGES:
    mid = (ys + ye) / 2
    ax_top.text(mid, stage_y, label,
                ha="center", va="top", fontsize=10,
                fontweight="bold", color=COLORS["muted"])
ax_top.set_xticks(np.arange(YR_LO, YR_HI + 1, 2))

# Subplot label (a) BELOW the chart
ax_top.text(0.5, -0.20, "(a)",
            transform=ax_top.transAxes,
            ha="center", va="top", fontsize=13, fontweight="bold",
            color=COLORS["ink"])

# ---------- Bottom 8 category panels ----------
cat_palette = [
    "#2E5A88", "#C46A3B", "#5B7D4F", "#7B4A8C",
    "#B45F4A", "#3F7B95", "#A78940", "#6D4C7D",
]
subplot_letters = "bcdefghi"

for k in range(8):
    r = 1 + (k // 4)
    c = k % 4
    ax = fig.add_subplot(gs[r, c])
    code, full = CATEGORIES[k]
    vals = cat_annual[code]
    col = cat_palette[k]
    for sid, ys, ye, label, color in STAGES:
        ax.axvspan(ys - 0.5, ye + 0.5, color=color, alpha=STAGE_ALPHA, zorder=0)
    ax.fill_between(years, vals, color=col, alpha=0.22, zorder=2)
    ax.plot(years, vals, color=col, linewidth=1.6, zorder=3)

    total = int(vals.sum())
    # n=... LEFT side at top-left (no chart title)
    ax.text(0.03, 0.95, f"{code}  (n = {total:,})",
            transform=ax.transAxes,
            ha="left", va="top", fontsize=9.5, style="italic",
            color=COLORS["muted"])
    ax.set_xlim(YR_LO - 0.5, YR_HI + 0.5)
    # Headroom
    ymx = max(vals.max() * 1.18, 1)
    ax.set_ylim(0, ymx)
    ax.set_xticks([2000, 2010, 2020])
    ax.grid(axis="y", linestyle="--", linewidth=0.5,
            color=COLORS["rule"], alpha=0.5)
    ax.tick_params(axis="both", labelsize=8.5)
    if c == 0:
        ax.set_ylabel("Entries / yr", fontsize=9.5)

    # Subplot letter (b)..(i) BELOW each small chart
    ax.text(0.5, -0.30, f"({subplot_letters[k]})",
            transform=ax.transAxes,
            ha="center", va="top", fontsize=11.5, fontweight="bold",
            color=COLORS["ink"])

NAME = "fig5_1_temporal_trajectory"
fig.savefig(OUT_DIR / (NAME + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_DIR / (NAME + ".pdf"), bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Saved:", NAME)
