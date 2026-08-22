"""
Figure 6.4 (v2): Sankey with cleaner labels.
- Middle-column labels moved above each rectangle so they don't overlap thin bands.
- Slightly larger canvas; flow widths legible.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as MplPath

sys.path.insert(0, '/sessions/hopeful-keen-maxwell/mnt/writing_projrct_5.5/03_scripts')
from _style import apply_style, COLORS, STAGES

apply_style()

QUAD_ORDER  = ["HH", "LH", "HL", "LL"]
QUAD_COLORS = {
    "HH": "#3F6B47",
    "LH": "#7B4A8C",
    "HL": "#C46A3B",
    "LL": "#6C7A8B",
}
QUAD_LABELS = {
    "HH": "HH  (synergistic leader)",
    "LH": "LH  (S&T-led)",
    "HL": "HL  (policy-driven)",
    "LL": "LL  (double laggard)",
}

qdf = pd.read_csv('/sessions/hopeful-keen-maxwell/mnt/outputs/prov_quadrant_records.csv')
pvt = qdf.pivot_table(index='province', columns='stage', values='quadrant', aggfunc='first')
pvt_full = pvt.dropna(subset=['S1','S2','S3']).copy()
TOTAL = len(pvt_full)

stage_cols = ['S1','S2','S3']
node_counts = {s: pvt_full[s].value_counts().reindex(QUAD_ORDER).fillna(0).astype(int).to_dict() for s in stage_cols}

def flows_between(a, b):
    sub = pvt_full[[a, b]]
    out = {}
    for q_from in QUAD_ORDER:
        for q_to in QUAD_ORDER:
            n = ((sub[a]==q_from) & (sub[b]==q_to)).sum()
            if n > 0: out[(q_from, q_to)] = int(n)
    return out

flow_12 = flows_between('S1', 'S2')
flow_23 = flows_between('S2', 'S3')

PAD = 1.6
node_w = 0.16
x_pos = {'S1': 0.0, 'S2': 1.0, 'S3': 2.0}

def compute_node_layout(counts):
    y_top = TOTAL + 3 * PAD
    layout = {}
    for q in QUAD_ORDER:
        h = counts[q]
        y_bot = y_top - h
        layout[q] = (y_bot, y_top, (y_bot + y_top) / 2)
        y_top = y_bot - PAD
    return layout

layouts = {s: compute_node_layout(node_counts[s]) for s in stage_cols}
src_offset = {(s, q): 0 for s in stage_cols for q in QUAD_ORDER}
tgt_offset = {(s, q): 0 for s in stage_cols for q in QUAD_ORDER}

fig, ax = plt.subplots(figsize=(14, 9.5))
ax.set_facecolor("#FAFBFD")

def draw_ribbon(ax, x0, y0_top, y0_bot, x1, y1_top, y1_bot, color, alpha=0.42):
    cx0 = x0 + (x1 - x0) * 0.45
    cx1 = x0 + (x1 - x0) * 0.55
    verts = [
        (x0, y0_top), (cx0, y0_top), (cx1, y1_top), (x1, y1_top),
        (x1, y1_bot), (cx1, y1_bot), (cx0, y0_bot), (x0, y0_bot),
        (x0, y0_top),
    ]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
             MplPath.LINETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.CLOSEPOLY]
    patch = PathPatch(MplPath(verts, codes),
                      facecolor=color, edgecolor='none', alpha=alpha, lw=0)
    ax.add_patch(patch)

def draw_flows(flows, src_stage, tgt_stage):
    for q_from in QUAD_ORDER:
        for q_to in QUAD_ORDER:
            n = flows.get((q_from, q_to), 0)
            if n == 0: continue
            src_y_top = layouts[src_stage][q_from][1]
            src_y_use = src_y_top - src_offset[(src_stage, q_from)]
            src_offset[(src_stage, q_from)] += n
            src_y_bot = src_y_top - src_offset[(src_stage, q_from)]
            tgt_y_top = layouts[tgt_stage][q_to][1]
            tgt_y_use = tgt_y_top - tgt_offset[(tgt_stage, q_to)]
            tgt_offset[(tgt_stage, q_to)] += n
            tgt_y_bot = tgt_y_top - tgt_offset[(tgt_stage, q_to)]
            alpha = 0.62 if q_from == q_to else 0.32
            color = QUAD_COLORS[q_from]
            x0 = x_pos[src_stage] + node_w / 2
            x1 = x_pos[tgt_stage] - node_w / 2
            draw_ribbon(ax, x0, src_y_use, src_y_bot, x1, tgt_y_use, tgt_y_bot, color, alpha=alpha)

draw_flows(flow_12, 'S1', 'S2')
draw_flows(flow_23, 'S2', 'S3')

# Draw nodes
for s in stage_cols:
    for q in QUAD_ORDER:
        n = node_counts[s][q]
        if n == 0: continue
        y_bot, y_top, y_c = layouts[s][q]
        rect = Rectangle((x_pos[s] - node_w/2, y_bot), node_w, y_top - y_bot,
                         facecolor=QUAD_COLORS[q], edgecolor=COLORS["ink"], linewidth=0.8, zorder=5)
        ax.add_patch(rect)
        # Labels: S1 left, S3 right, S2 either above (if small) or inside (if big)
        if s == 'S1':
            ax.text(x_pos[s] - node_w/2 - 0.04, y_c, f"{q}  ({n})",
                    ha="right", va="center", fontsize=11,
                    color=COLORS["ink"], fontweight="bold")
        elif s == 'S3':
            ax.text(x_pos[s] + node_w/2 + 0.04, y_c, f"{q}  ({n})",
                    ha="left", va="center", fontsize=11,
                    color=COLORS["ink"], fontweight="bold")
        else:
            # Middle column: label OUTSIDE rectangle (above)
            ax.text(x_pos[s], y_top + 0.25, f"{q} ({n})",
                    ha="center", va="bottom", fontsize=10,
                    color=COLORS["ink"], fontweight="bold")

# Column headers
top_y = TOTAL + 3 * PAD + 2.5
for s, (sid, ys, ye, label, _) in zip(stage_cols, STAGES):
    ax.text(x_pos[s], top_y, label,
            ha="center", va="bottom", fontsize=13, fontweight="bold",
            color=COLORS["ink"])

# Stickiness annotation
ll_s1 = node_counts['S1']['LL']
ll_s3 = pvt_full[(pvt_full['S1']=='LL') & (pvt_full['S3']=='LL')].shape[0]
hh_s1 = node_counts['S1']['HH']
hh_s3 = pvt_full[(pvt_full['S1']=='HH') & (pvt_full['S3']=='HH')].shape[0]
stick_txt = (f"Persistent LL  (S1 → S3): {ll_s3}/{ll_s1} provinces = {100*ll_s3/ll_s1:.0f}%\n"
             f"Persistent HH  (S1 → S3): {hh_s3}/{hh_s1} provinces = {100*hh_s3/hh_s1:.0f}%")
ax.text(0.5, -0.04, stick_txt,
        transform=ax.transAxes, ha="center", va="top",
        fontsize=11.5, color=COLORS["ink"],
        bbox=dict(boxstyle="round,pad=0.55", facecolor="white",
                  edgecolor=COLORS["rule"], linewidth=0.8))

ax.set_xlim(-0.6, 2.6)
ax.set_ylim(-3.5, TOTAL + 3 * PAD + 4.5)
ax.set_xticks([])
ax.set_yticks([])
for sp in ax.spines.values(): sp.set_visible(False)

legend_handles = [Rectangle((0,0), 1, 1, facecolor=QUAD_COLORS[q],
                            edgecolor=COLORS["ink"], linewidth=0.6,
                            label=QUAD_LABELS[q]) for q in QUAD_ORDER]
ax.legend(handles=legend_handles, loc="upper right",
          bbox_to_anchor=(1.18, 1.0), frameon=True, framealpha=0.95,
          edgecolor=COLORS["rule"], fontsize=10.5, title="Quadrant",
          title_fontsize=11.5)

OUT = Path('/sessions/hopeful-keen-maxwell/mnt/outputs')
NAME = "fig6_4_quadrant_sankey_v2"
fig.savefig(OUT / (NAME + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"已生成: {OUT / (NAME + '.png')}")
