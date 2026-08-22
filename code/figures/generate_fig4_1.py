"""
Figure 4.1 (dual-panel): bubble matrices.
v3 changes: no axis frame; legend bubbles use a representative colour
from the panel's colormap (median tone); legend title in a single line.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import apply_style, CATEGORIES, CAT_CODES, OUT_DIR, COLORS

apply_style()

ROOT       = Path(__file__).resolve().parent.parent
FILES_XLSX = ROOT / "02_data" / "final_entries" / "政策文件表_v5.3.xlsx"

files = pd.read_excel(FILES_XLSX, sheet_name=0)
has_cols = [f"has_{c}" for c in CAT_CODES]
B = files[has_cols].astype(bool).values
n_cats = len(CAT_CODES)
cat_counts = B.sum(axis=0)

co_cat  = np.zeros((n_cats, n_cats), dtype=int)
jac_cat = np.zeros((n_cats, n_cats), dtype=float)
for i in range(n_cats):
    for j in range(n_cats):
        inter = int((B[:, i] & B[:, j]).sum())
        union = int((B[:, i] | B[:, j]).sum())
        co_cat[i, j]  = inter
        jac_cat[i, j] = inter / union if union > 0 else 0.0

co_typ_df = pd.read_excel(FILES_XLSX, sheet_name="联合发文-共现矩阵").set_index("type")
jac_typ_df = pd.read_excel(FILES_XLSX, sheet_name="联合发文-Jaccard矩阵").set_index("type")
dist_df = pd.read_excel(FILES_XLSX, sheet_name="联合发文-类型分布")

TYPE_KEEP = [t for t in co_typ_df.index if t != "Other"]
co_typ  = co_typ_df.loc[TYPE_KEEP, TYPE_KEEP].values
jac_typ = jac_typ_df.loc[TYPE_KEEP, TYPE_KEEP].values
typ_counts = np.diag(co_typ).copy()

TYPE_LABEL = {
    "Central Party":              "Central Party",
    "State Council & Ministries": "State Council /\nMinistries",
    "National Sci./Society":      "National Sci. /\nSociety",
    "Provincial Party":           "Provincial Party",
    "Provincial Gov./Bureau":     "Provincial Gov. /\nBureau",
    "Municipal Party":            "Municipal Party",
    "Municipal Gov./Bureau":      "Municipal Gov. /\nBureau",
}
type_labels = [TYPE_LABEL.get(t, t) for t in TYPE_KEEP]

cmap_a = LinearSegmentedColormap.from_list("ylorrd",
    ["#FFFFE0", "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C",
     "#FC4E2A", "#E31A1C", "#B10026"])
cmap_b = LinearSegmentedColormap.from_list("blues",
    ["#F4F8FC", "#E0EBF5", "#C2D8EB", "#9BBED9", "#6E9EC4",
     "#467FAE", "#2A5F94", "#173E6E"])

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15.0, 7.5))
fig.subplots_adjust(left=0.07, right=0.96, top=0.96, bottom=0.16, wspace=0.30)

BUBBLE_MAX = 2400

def draw_panel(ax, labels, counts, co, jac, cmap=None,
               edge_color="#000", bubble_max=BUBBLE_MAX, label_rot=35,
               label_fontsize=10):
    n = len(labels)
    pts_i, pts_j, pts_co, pts_jac = [], [], [], []
    for i in range(n):
        for j in range(n):
            if i > j:
                pts_i.append(i); pts_j.append(j)
                pts_co.append(co[i, j]); pts_jac.append(jac[i, j])
    pts_co = np.asarray(pts_co); pts_jac = np.asarray(pts_jac)
    max_co = max(int(pts_co.max()), 1)
    sizes = np.clip((pts_co / max_co) * bubble_max, 25, None)
    vmax = max(pts_jac.max() * 1.02, 1e-6)

    sc = ax.scatter(pts_j, pts_i, s=sizes, c=pts_jac, cmap=cmap,
                    vmin=0, vmax=vmax,
                    edgecolor=edge_color, linewidth=0.5,
                    alpha=0.95, zorder=3)

    for i in range(n):
        ax.text(i, i, f"{int(counts[i]):,}",
                ha="center", va="center", fontsize=9.5,
                fontweight="bold", color=COLORS["ink"])

    for k in range(n):
        ax.axhline(k, color="#E8ECEF", linewidth=0.6, zorder=1)
        ax.axvline(k, color="#E8ECEF", linewidth=0.6, zorder=1)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=label_rot, ha="right",
                       fontsize=label_fontsize)
    ax.set_yticklabels(labels, fontsize=label_fontsize)
    ax.tick_params(length=0)
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(-0.6, n - 0.4)
    ax.invert_yaxis()
    ax.set_aspect("equal")
    # 去掉所有边框
    for sp in ax.spines.values():
        sp.set_visible(False)
    return sc, max_co

sc_a, max_a = draw_panel(axL,
    labels=[name for _, name in CATEGORIES],
    counts=cat_counts, co=co_cat, jac=jac_cat,
    cmap=cmap_a, edge_color="#7A4828")

sc_b, max_b = draw_panel(axR,
    labels=type_labels,
    counts=typ_counts, co=co_typ, jac=jac_typ,
    cmap=cmap_b, edge_color="#1F4A7B",
    label_fontsize=9.5)

cbA = fig.colorbar(sc_a, ax=axL, fraction=0.045, pad=0.04, shrink=0.85)
cbA.set_label("Jaccard similarity", fontsize=10.2, color=COLORS["ink"])
cbA.outline.set_visible(False); cbA.ax.tick_params(labelsize=9)
cbB = fig.colorbar(sc_b, ax=axR, fraction=0.045, pad=0.04, shrink=0.85)
cbB.set_label("Jaccard similarity", fontsize=10.2, color=COLORS["ink"])
cbB.outline.set_visible(False); cbB.ax.tick_params(labelsize=9)

from matplotlib.offsetbox import (AnchoredOffsetbox, VPacker, HPacker,
                                  TextArea, DrawingArea)
import matplotlib.patches as mpatches

def add_size_legend(ax, max_co, cmap, edge_color, cmap_pos,
                    bubble_max=BUBBLE_MAX, title="Co-deployment files"):
    """自定义图例: 圆圈边到边间距均匀,标题与圆圈组单独留更大空隙。"""
    if max_co >= 500:
        values = [500, 200, 50]
    elif max_co >= 200:
        values = [200, 100, 25]
    else:
        values = [100, 50, 10]
    fill_color = cmap(cmap_pos)

    rows = []
    for v in values:
        s = max((v / max_co) * bubble_max, 25)
        r_pt = (s / np.pi) ** 0.5  # 半径(points)
        da_side = 2 * r_pt + 2
        da = DrawingArea(da_side, da_side, 0, 0)
        circle = mpatches.Circle((da_side / 2, da_side / 2), r_pt,
                                  facecolor=fill_color,
                                  edgecolor=edge_color, linewidth=0.5)
        da.add_artist(circle)
        ta = TextArea(f"{v:,}",
                      textprops=dict(fontsize=10, color=COLORS["ink"]))
        row = HPacker(children=[da, ta], align="center", pad=0, sep=10)
        rows.append(row)

    # 圆圈之间用 8pt 边到边间距; 标题与圆圈组用 16pt 间距
    entries = VPacker(children=rows, sep=8, align="center", pad=0)
    title_ta = TextArea(title,
                        textprops=dict(fontsize=10.5, color=COLORS["ink"],
                                       fontweight="bold"))
    full = VPacker(children=[title_ta, entries], sep=16,
                   align="center", pad=0)

    box = AnchoredOffsetbox(loc="upper right", child=full,
                             pad=0, borderpad=1, frameon=False,
                             bbox_to_anchor=(0.985, 0.985),
                             bbox_transform=ax.transAxes)
    ax.add_artist(box)

add_size_legend(axL, max_a, cmap=cmap_a, edge_color="#7A4828",
                cmap_pos=0.02, title="Co-deployment files")
add_size_legend(axR, max_b, cmap=cmap_b, edge_color="#1F4A7B",
                cmap_pos=0.20, title="Co-issuance files")

axL.text(0.5, -0.20, "(a)", transform=axL.transAxes,
         ha="center", va="top", fontsize=13, fontweight="bold",
         color=COLORS["ink"])
axR.text(0.5, -0.20, "(b)", transform=axR.transAxes,
         ha="center", va="top", fontsize=13, fontweight="bold",
         color=COLORS["ink"])

NAME = "fig4_1_jaccard_heatmap"
fig.savefig(OUT_DIR / (NAME + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_DIR / (NAME + ".pdf"), bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Saved:", NAME)
print(f"  panel (a) max co-deployment: {max_a:,}")
print(f"  panel (b) max co-issuance:  {max_b:,}")
,
                cmap_pos=0.20, title="Co-issuance files")

axL.text(0.5, -0.20, "(a)", transform=axL.transAxes,
         ha="center", va="top", fontsize=13, fontweight="bold",
         color=COLORS["ink"])
axR.text(0.5, -0.20, "(b)", transform=axR.transAxes,
         ha="center", va="top", fontsize=13, fontweight="bold",
         color=COLORS["ink"])

NAME = "fig4_1_jaccard_heatmap"
fig.savefig(OUT_DIR / (NAME + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_DIR / (NAME + ".pdf"), bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Saved:", NAME)
print(f"  panel (a) max co-deployment: {max_a:,}")
print(f"  panel (b) max co-issuance:  {max_b:,}")
