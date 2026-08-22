"""
Figure 6.3 (clean): Two versions, no leader lines.
  - labeled : province name placed directly next to S3 endpoint
  - blank   : no labels at all, for manual annotation in PowerPoint
Smooth quadratic curve through S1, S2, S3. Hollow circle at S1,
solid disc at S3. Same independent axes per region.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

sys.path.insert(0, '/sessions/hopeful-keen-maxwell/mnt/writing_projrct_5.5/03_scripts')
from _style import (apply_style, STAGES, REGION_ORDER, REGION_COLORS,
                    PROV_FULL_TO_SHORT, province_region, COLORS)
apply_style()

ROOT = Path('/sessions/hopeful-keen-maxwell/mnt/writing_projrct_5.5')
FILES_XLSX = ROOT / "02_data" / "final_entries" / "政策文件表_v5.3.xlsx"
TECH_XLSX  = ROOT / "02_data" / "technology_indicators" / "分省科技综合指数_熵权法_1998_2024.xlsx"

PROV_EN = {
    "北京":"Beijing","上海":"Shanghai","天津":"Tianjin","重庆":"Chongqing",
    "江苏":"Jiangsu","浙江":"Zhejiang","广东":"Guangdong","山东":"Shandong",
    "河南":"Henan","湖北":"Hubei","湖南":"Hunan","四川":"Sichuan","陕西":"Shaanxi",
    "辽宁":"Liaoning","吉林":"Jilin","黑龙江":"Heilongjiang",
    "河北":"Hebei","山西":"Shanxi","安徽":"Anhui","福建":"Fujian","江西":"Jiangxi",
    "广西":"Guangxi","海南":"Hainan","云南":"Yunnan","贵州":"Guizhou",
    "内蒙古":"Inner Mongolia","宁夏":"Ningxia","新疆":"Xinjiang","甘肃":"Gansu",
    "青海":"Qinghai","西藏":"Tibet"
}

files = pd.read_excel(FILES_XLSX)
tech  = pd.read_excel(TECH_XLSX)
files = files[files["governance_level"].isin(["省级", "地市级"])].copy()
files["prov"] = files["province_raw"].astype(str).str.split(";").str[0]
files["prov_short"] = files["prov"].map(PROV_FULL_TO_SHORT).fillna(files["prov"])
files["region"]   = files["prov"].apply(province_region)
files = files[files["region"].isin(REGION_ORDER)]

def stage_for_year(y):
    for sid, ys, ye, *_ in STAGES:
        if ys <= y <= ye: return sid
    return None

files["stage"] = files["issue_year"].apply(stage_for_year)
policy_stage = (files.dropna(subset=["stage"])
    .groupby(["prov_short", "stage"]).size().rename("O").reset_index())

tech = tech.rename(columns={"省份": "prov_short", "年份": "year"})
tech["stage"] = tech["year"].apply(stage_for_year)
tech_stage = (tech.dropna(subset=["stage"])
    .groupby(["prov_short", "stage"])["科技综合指数"].mean().rename("T").reset_index())

df = policy_stage.merge(tech_stage, on=["prov_short", "stage"], how="inner")
df["region"] = df["prov_short"].apply(province_region)
df = df[df["region"].isin(REGION_ORDER)]

def norm(x):
    x = np.asarray(x, dtype=float)
    if np.nanmax(x) > np.nanmin(x):
        return (x - np.nanmin(x)) / (np.nanmax(x) - np.nanmin(x))
    return np.zeros_like(x)

for s in df["stage"].unique():
    m = df["stage"] == s
    df.loc[m, "O_star"] = norm(df.loc[m, "O"].values)
    df.loc[m, "T_star"] = norm(df.loc[m, "T"].values)

med_O = float(df[df["stage"]=='S3']["O_star"].median())
med_T = float(df[df["stage"]=='S3']["T_star"].median())

all_provs = sorted(df["prov_short"].unique())

def get_xy(prov, stage):
    sub = df[(df["prov_short"]==prov) & (df["stage"]==stage)]
    if len(sub) == 0: return (np.nan, np.nan)
    return (sub.iloc[0]["O_star"], sub.iloc[0]["T_star"])

def smooth_curve(x1, y1, x2, y2, x3, y3, n=50):
    t_data = np.array([0.0, 0.5, 1.0])
    fx = interp1d(t_data, np.array([x1, x2, x3]), kind='quadratic')
    fy = interp1d(t_data, np.array([y1, y2, y3]), kind='quadratic')
    t = np.linspace(0, 1, n)
    return fx(t), fy(t)

def draw_figure(show_labels: bool, outname: str):
    fig, axes = plt.subplots(2, 2, figsize=(18, 16))
    fig.subplots_adjust(left=0.06, right=0.97, top=0.94, bottom=0.06, wspace=0.20, hspace=0.32)
    panel_letters = "abcd"

    for k, region in enumerate(REGION_ORDER):
        ax = axes[k // 2, k % 2]
        color = REGION_COLORS[region]
        ax.set_facecolor("#FAFBFD")
        region_provs = [p for p in all_provs if province_region(p) == region]

        all_pts_x = []; all_pts_y = []
        province_data = []
        for prov in region_provs:
            x1, y1 = get_xy(prov, 'S1')
            x2, y2 = get_xy(prov, 'S2')
            x3, y3 = get_xy(prov, 'S3')
            if np.isnan(x3): continue
            for x, y in [(x1, y1), (x2, y2), (x3, y3)]:
                if not np.isnan(x):
                    all_pts_x.append(x); all_pts_y.append(y)
            province_data.append((prov, x1, y1, x2, y2, x3, y3))

        if not all_pts_x: continue

        pad = 0.12
        x_lo = max(-0.05, min(all_pts_x) - pad); x_hi = min(1.10, max(all_pts_x) + pad)
        y_lo = max(-0.05, min(all_pts_y) - pad); y_hi = min(1.10, max(all_pts_y) + pad)
        if x_hi - x_lo < 0.55:
            mid = (x_hi + x_lo) / 2
            x_lo = max(-0.05, mid - 0.32); x_hi = min(1.10, mid + 0.32)
        if y_hi - y_lo < 0.55:
            mid = (y_hi + y_lo) / 2
            y_lo = max(-0.05, mid - 0.32); y_hi = min(1.10, mid + 0.32)
        ax.set_xlim(x_lo, x_hi); ax.set_ylim(y_lo, y_hi)

        if x_lo <= med_O <= x_hi:
            ax.axvline(med_O, color=COLORS["muted"], linestyle="--", linewidth=0.7, alpha=0.5, zorder=1)
        if y_lo <= med_T <= y_hi:
            ax.axhline(med_T, color=COLORS["muted"], linestyle="--", linewidth=0.7, alpha=0.5, zorder=1)

        for prov, x1, y1, x2, y2, x3, y3 in province_data:
            if not np.isnan(x1) and not np.isnan(x2):
                try:
                    xs_c, ys_c = smooth_curve(x1, y1, x2, y2, x3, y3, n=50)
                    ax.plot(xs_c, ys_c, color=color, linewidth=1.3, alpha=0.55, zorder=2)
                except Exception:
                    ax.plot([x1, x2, x3], [y1, y2, y3], color=color, linewidth=1.3, alpha=0.55, zorder=2)
            elif not np.isnan(x1):
                ax.plot([x1, x3], [y1, y3], color=color, linewidth=1.3, alpha=0.55, zorder=2)

            if not np.isnan(x1):
                ax.scatter([x1], [y1], s=30, facecolors='white', edgecolors=color,
                           linewidths=1.2, zorder=3)
            ax.scatter([x3], [y3], s=125, facecolors=color, edgecolors=COLORS["ink"],
                       linewidths=1.0, zorder=5)

            if show_labels:
                en_name = PROV_EN.get(prov, prov)
                # 简单偏移,不画引线
                ax.text(x3 + 0.012, y3 + 0.008, en_name,
                        fontsize=11.5, color=COLORS["ink"],
                        fontweight='medium', zorder=8,
                        ha='left', va='bottom')

        ax.text(0.97, 0.97, "HH", transform=ax.transAxes, ha="right", va="top",
                fontsize=11, style="italic", color=COLORS["muted"], fontweight='bold', alpha=0.85)
        ax.text(0.03, 0.97, "LH", transform=ax.transAxes, ha="left", va="top",
                fontsize=11, style="italic", color=COLORS["muted"], fontweight='bold', alpha=0.85)
        ax.text(0.97, 0.03, "HL", transform=ax.transAxes, ha="right", va="bottom",
                fontsize=11, style="italic", color=COLORS["muted"], fontweight='bold', alpha=0.85)
        ax.text(0.03, 0.03, "LL", transform=ax.transAxes, ha="left", va="bottom",
                fontsize=11, style="italic", color=COLORS["muted"], fontweight='bold', alpha=0.85)

        ax.set_xlabel(r"Policy intensity $O^*_{i,s}$", fontsize=12)
        ax.set_ylabel(r"S\&T composite $T^*_{i,s}$", fontsize=12)
        ax.grid(linestyle="--", linewidth=0.4, color=COLORS["rule"], alpha=0.35)

        ax.text(0.5, 1.04, f"{region}  (n = {len(province_data)} provinces)",
                transform=ax.transAxes, ha="center", va="bottom",
                fontsize=14, fontweight="bold", color=COLORS["ink"])
        ax.text(0.5, -0.12, f"({panel_letters[k]})",
                transform=ax.transAxes, ha="center", va="top",
                fontsize=14, fontweight="bold", color=COLORS["ink"])

    import matplotlib.lines as mlines
    h1 = mlines.Line2D([], [], color="#444", marker='o', markersize=9,
                       markerfacecolor='white', markeredgewidth=1.4,
                       linestyle='None', label="S1 start  (1998–2005)")
    h_curve = mlines.Line2D([], [], color="#444", linewidth=2,
                            label="Smooth path through S1→S2→S3")
    h2 = mlines.Line2D([], [], color="#444", marker='o', markersize=13,
                       markerfacecolor='#444', markeredgecolor='white',
                       linestyle='None', label="S3 endpoint  (2016–2025)")
    fig.legend(handles=[h1, h_curve, h2], loc="lower center",
               bbox_to_anchor=(0.5, 0.005), ncol=3, frameon=False,
               fontsize=12, columnspacing=3, handletextpad=0.6)

    OUT = Path('/sessions/hopeful-keen-maxwell/mnt/outputs')
    fig.savefig(OUT / (outname + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"保存: {OUT / (outname + '.png')}")

# 生成两个版本
draw_figure(show_labels=True,  outname="fig6_3_regional_trajectory_labeled")
draw_figure(show_labels=False, outname="fig6_3_regional_trajectory_blank")
