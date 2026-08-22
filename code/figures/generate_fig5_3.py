"""
Figure 5.3 (v5): Three equal-sized horizontal panels presenting a stepwise
'discovery progression':
  (a) Aggregate view  — time series with overall r = 0.717
  (b) Stage breakdown — per-stage scatter; aggregate correlation hides
      stage heterogeneity (S1 r=+0.95, S2 r=+0.81, S3 r=-0.09)
  (c) First-difference — after removing the common upward trend,
      year-on-year changes are uncorrelated (r = -0.29, p = 0.14)
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

sys.path.insert(0, '/sessions/hopeful-keen-maxwell/mnt/writing_projrct_5.5/03_scripts')
from _style import apply_style, STAGES, OUT_DIR, COLORS
apply_style()

ROOT = Path('/sessions/hopeful-keen-maxwell/mnt/writing_projrct_5.5')
DATA_XLSX  = ROOT / "02_data" / "final_entries" / "开放科学政策数据_最终版_v5.3.xlsx"
TECH_PANEL = ROOT / "02_data" / "technology_indicators" / "分省科技指标面板数据_1998_2024.xlsx"
TECH_INDEX = ROOT / "02_data" / "technology_indicators" / "分省科技综合指数_熵权法_1998_2024.xlsx"

YR_LO, YR_HI = 1998, 2024
STAGE_ALPHA = 0.35

files   = pd.read_excel(DATA_XLSX, sheet_name="政策文件")
entries = pd.read_excel(DATA_XLSX, sheet_name="政策条目")
panel   = pd.read_excel(TECH_PANEL)
ent_calc = pd.read_excel(TECH_INDEX, sheet_name="熵权计算")

years = np.arange(YR_LO, YR_HI + 1)
F = np.array([int((files["issue_year"]==y).sum()) for y in years])
E = np.array([int((entries["issue_year"]==y).sum()) for y in years])

def mm(a):
    a = np.array(a, dtype=float)
    return (a - np.nanmin(a)) / (np.nanmax(a) - np.nanmin(a))

O_star = mm(mm(np.log1p(F)) + mm(np.log1p(E)))

nat = panel.groupby("年份")[["R&D人员全时当量","R&D经费内部支出","专利授权数","技术市场成交额"]].sum().reset_index()
w = ent_calc.set_index("指标")["熵权"]
for col in w.index:
    a = nat[col].values
    nat[col + "_z"] = (a - a.min()) / (a.max() - a.min())
nat["S_score"] = sum(nat[c + "_z"] * w[c] for c in w.index)
S_raw = nat.set_index("年份")["S_score"].reindex(years).values
S_star = mm(S_raw)

r_all, _ = stats.pearsonr(O_star, S_star)
rho_all, _ = stats.spearmanr(O_star, S_star)

stage_colors = ["#3D5A80", "#C46A3B", "#3F6B47"]
stage_r = []
for (sid, ys, ye, *_), col in zip(STAGES, stage_colors):
    idx = (years >= ys) & (years <= ye)
    xs, ys_v = O_star[idx], S_star[idx]
    if len(xs) >= 3:
        r_s, p_s = stats.pearsonr(xs, ys_v)
        stage_r.append((sid, r_s, p_s, len(xs)))

dO = np.diff(O_star); dS = np.diff(S_star)
diff_years = years[1:]
r_diff, p_diff = stats.pearsonr(dO, dS)

# === 1x3 等宽子图 ===
fig, axes = plt.subplots(1, 3, figsize=(19, 6),
                          gridspec_kw={'wspace': 0.28})
fig.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=0.13)

# ===== (a) 时间序列 =====
ax = axes[0]
ax2 = ax.twinx()
ax2.spines["right"].set_visible(True)
ax2.spines["top"].set_visible(False)

for sid, ys, ye, label, color in STAGES:
    if ye < YR_LO or ys > YR_HI: continue
    ax.axvspan(max(ys, YR_LO)-0.5, min(ye, YR_HI)+0.5,
               color=color, alpha=STAGE_ALPHA, zorder=0)

l1, = ax.plot(years, O_star, color=COLORS["primary"], linewidth=2.0,
              marker="o", markersize=4, markerfacecolor="white",
              markeredgewidth=1.3, label=r"$O_t^*$", zorder=3)
l2, = ax2.plot(years, S_star, color=COLORS["secondary"], linewidth=2.0,
               marker="s", markersize=3.5, markerfacecolor="white",
               markeredgewidth=1.3, linestyle="--",
               label=r"$S_t^*$", zorder=3)

ax.set_xlim(YR_LO-0.5, YR_HI+0.5)
ax.set_ylim(-0.03, 1.18); ax2.set_ylim(-0.03, 1.18)
ax.set_xlabel("Year", fontsize=10.5, color=COLORS["ink"])
ax.set_ylabel(r"Policy intensity $O_t^*$", fontsize=10.5, color=COLORS["ink"])
ax2.set_ylabel(r"S\&T composite $S_t^*$", fontsize=10.5, color=COLORS["ink"])
ax.tick_params(axis="y", colors=COLORS["ink"], labelsize=9)
ax2.tick_params(axis="y", colors=COLORS["ink"], labelsize=9)
for sp in ax2.spines.values():
    sp.set_edgecolor(COLORS["ink"])
ax.grid(False)
ax.set_xticks(np.arange(YR_LO, YR_HI+1, 4))

for sid, ys, ye, label, color in STAGES:
    if ye < YR_LO or ys > YR_HI: continue
    mid = (max(ys, YR_LO) + min(ye, YR_HI)) / 2
    short = label.split(":")[0]
    ax.text(mid, 1.13, short, ha="center", va="top",
            fontsize=9.5, fontweight="bold", color=COLORS["muted"])

ax.legend(handles=[l1, l2], loc="upper left",
          bbox_to_anchor=(0.02, 0.92), fontsize=9.5, frameon=False)
ax.text(0.03, 0.72,
        f"All years (n = 27)\nPearson r = {r_all:.3f}\nSpearman ρ = {rho_all:.3f}",
        transform=ax.transAxes, fontsize=9.5,
        color=COLORS["ink"], va="top", ha="left")

ax.text(0.5, -0.16, "(a)",
        transform=ax.transAxes, ha="center", va="top",
        fontsize=13, fontweight="bold", color=COLORS["ink"])

# ===== (b) 阶段散点 =====
ax_b = axes[1]
# bc 改白底
med_O = float(np.nanmedian(O_star))
med_S = float(np.nanmedian(S_star))
ax_b.axvline(med_O, color=COLORS["muted"], linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)
ax_b.axhline(med_S, color=COLORS["muted"], linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)

for (sid, ys, ye, label, _), col in zip(STAGES, stage_colors):
    idx = (years >= ys) & (years <= ye)
    xs_v, ys_v = O_star[idx], S_star[idx]
    r_v = stats.pearsonr(xs_v, ys_v)[0] if len(xs_v) >= 3 else np.nan
    ax_b.scatter(xs_v, ys_v, s=70, color=col, alpha=0.85, edgecolor="white",
                 linewidth=0.9, zorder=3,
                 label=f"{sid}  (r = {r_v:+.2f})")
    if len(xs_v) >= 3:
        z = np.polyfit(xs_v, ys_v, 1)
        x_line = np.linspace(xs_v.min(), xs_v.max(), 50)
        ax_b.plot(x_line, np.polyval(z, x_line), color=col,
                  linewidth=1.4, linestyle="--", alpha=0.75, zorder=2)

# 关键年份
_label_years = set()
for yy, ox, sx in zip(years, O_star, S_star):
    if int(yy) not in _label_years: continue
    if np.isnan(ox) or np.isnan(sx): continue
    ax_b.annotate(f"{int(yy)}", xy=(ox, sx),
                  xytext=(5, 5), textcoords="offset points",
                  fontsize=8.5, color=COLORS["text"], zorder=4)

ax_b.text(0.97, 0.04, "HL", transform=ax_b.transAxes, ha="right", va="bottom",
          fontsize=9, style="italic", color=COLORS["muted"])
ax_b.text(0.03, 0.04, "LL", transform=ax_b.transAxes, ha="left", va="bottom",
          fontsize=9, style="italic", color=COLORS["muted"])
ax_b.text(0.03, 0.96, "LH", transform=ax_b.transAxes, ha="left", va="top",
          fontsize=9, style="italic", color=COLORS["muted"])
ax_b.text(0.97, 0.96, "HH", transform=ax_b.transAxes, ha="right", va="top",
          fontsize=9, style="italic", color=COLORS["muted"])

ax_b.set_xlim(-0.05, 1.08); ax_b.set_ylim(-0.05, 1.08)
ax_b.set_xlabel(r"Policy intensity $O_t^*$", fontsize=10.5)
ax_b.set_ylabel(r"S\&T composite $S_t^*$", fontsize=10.5)
ax_b.tick_params(labelsize=9)
ax_b.grid(False)
ax_b.legend(loc="lower right", fontsize=9.5, frameon=True, framealpha=0.95,
            edgecolor=COLORS["rule"])

ax_b.text(0.5, -0.16, "(b)",
          transform=ax_b.transAxes, ha="center", va="top",
          fontsize=13, fontweight="bold", color=COLORS["ink"])

# ===== (c) 差分散点 =====
ax_c = axes[2]
# bc 改白底

for (sid, ys, ye, *_), col in zip(STAGES, stage_colors):
    idx = (diff_years >= ys) & (diff_years <= ye)
    ax_c.scatter(dO[idx], dS[idx], s=70, color=col, alpha=0.85,
                 edgecolor="white", linewidth=0.9, zorder=3,
                 label=sid)

z = np.polyfit(dO, dS, 1)
x_line = np.linspace(dO.min(), dO.max(), 50)
ax_c.plot(x_line, np.polyval(z, x_line), color=COLORS["ink"],
          linewidth=1.5, linestyle="--", alpha=0.75, zorder=2,
          label=f"Linear fit (r = {r_diff:+.2f})")
ax_c.axhline(0, color=COLORS["muted"], linewidth=0.6, alpha=0.5, zorder=1)
ax_c.axvline(0, color=COLORS["muted"], linewidth=0.6, alpha=0.5, zorder=1)

ax_c.set_xlabel(r"$\Delta O_t^*$  (year-on-year change in policy)", fontsize=10.5)
ax_c.set_ylabel(r"$\Delta S_t^*$  (year-on-year change in S\&T)", fontsize=10.5)
ax_c.tick_params(labelsize=9)
ax_c.grid(False)
ax_c.text(0.04, 0.96,
          f"Pearson r = {r_diff:+.3f}\np = {p_diff:.3f}  (n.s.)\nn = {len(dO)}",
          transform=ax_c.transAxes, fontsize=9.5,
          color=COLORS["ink"], va="top", ha="left")
ax_c.legend(loc="upper right", fontsize=9.5, frameon=True, framealpha=0.95,
            edgecolor=COLORS["rule"])

ax_c.text(0.5, -0.16, "(c)",
          transform=ax_c.transAxes, ha="center", va="top",
          fontsize=13, fontweight="bold", color=COLORS["ink"])

OUT = Path('/sessions/hopeful-keen-maxwell/mnt/outputs')
NAME = "fig5_3_national_coupling_final"
fig.savefig(OUT / (NAME + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"保存到: {OUT / (NAME + '.png')}")
