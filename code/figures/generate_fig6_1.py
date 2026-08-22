"""
Figure 6.1: Dual choropleth map of open-science policy file counts at
the provincial (a) and municipal (b) levels.

Pure-matplotlib version: reads boundaries and the 10-dash South China Sea
line directly from the official GeoJSON files in 02_data/.
White background, proper aspect ratio, single-tone Blues colormap.
"""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
from shapely.geometry import shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import apply_style, OUT_DIR, COLORS

apply_style()

ROOT          = Path(__file__).resolve().parent.parent
FILES_XLSX    = ROOT / "02_data" / "final_entries" / "政策文件表_v5.3.xlsx"
ENTRIES_XLSX  = ROOT / "02_data" / "final_entries" / "开放科学政策数据_最终版_v5.3.xlsx"
PROV_GEOJSON  = ROOT / "02_data" / "中国_省.geojson"
CITY_GEOJSON  = ROOT / "02_data" / "中国_市.geojson"

# Full China extent including all SCS islands
LON_W, LON_E = 72.0, 136.0
LAT_S, LAT_N =  2.5,  54.5

# ----- Data -----
files   = pd.read_excel(FILES_XLSX)
entries = pd.read_excel(ENTRIES_XLSX)

prov_counts = (
    files.assign(prov=files["province_raw"].astype(str).str.split(";").str[0])
    .loc[lambda d: d["governance_level"].isin(["省级", "地市级"])]
    .groupby("prov").size()
)

city_counts = (
    entries[entries["governance_level"] == "地市级"]
    .groupby("city_raw")["policy_file_id"].nunique()
)

# ----- Load geojson, separate polygons from boundary lines -----
def load_features(path):
    """
    Return (poly_feats, dash_feats).
    All '境界线' features are kept so the map shows the full national
    boundary (SCS 10-dash line + Wakhan corridor + HK / coastal segments).
    """
    with open(path, encoding="utf-8") as f:
        g = json.load(f)
    poly, dash = [], []
    for feat in g["features"]:
        name = feat["properties"].get("name")
        geom = feat.get("geometry")
        if not geom or not name:
            continue
        s = shape(geom)
        if name == "境界线" or geom["type"] in ("LineString", "MultiLineString"):
            dash.append({"name": name, "geom": s})
        else:
            poly.append({"name": name, "geom": s})
    return poly, dash

prov_polys, prov_dashes = load_features(PROV_GEOJSON)
city_polys, _           = load_features(CITY_GEOJSON)

# ----- Yellow -> Orange -> Red colormap (ColorBrewer YlOrRd) -----
cmap = LinearSegmentedColormap.from_list(
    "ylorrd_nature",
    ["#FFFFCC", "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C",
     "#FC4E2A", "#E31A1C", "#B10026"],
)

def polygon_patches(geom):
    if geom.geom_type == "Polygon":
        yield MplPolygon(np.array(geom.exterior.coords), closed=True)
    elif geom.geom_type == "MultiPolygon":
        for p in geom.geoms:
            yield MplPolygon(np.array(p.exterior.coords), closed=True)

def draw_dash_line(ax, dash_feats, *, color="#1F2B40", linewidth=1.0):
    for d in dash_feats:
        geom = d["geom"]
        lines = geom.geoms if geom.geom_type == "MultiLineString" else [geom]
        for line in lines:
            xs, ys = np.array(line.coords).T
            ax.plot(xs, ys, color=color, linewidth=linewidth,
                    solid_capstyle="round", zorder=4)

def draw_map(ax, feats, counts, vmax, *, dash_feats=None):
    norm = Normalize(vmin=0, vmax=vmax)

    # 1. Polygons that have data -> coloured by count
    coloured_patches, vals = [], []
    grey_patches = []
    for f in feats:
        v = counts.get(f["name"], 0)
        for poly in polygon_patches(f["geom"]):
            if v > 0:
                coloured_patches.append(poly)
                vals.append(v)
            else:
                grey_patches.append(poly)

    # Grey first (under), then colour on top
    if grey_patches:
        pc0 = PatchCollection(
            grey_patches,
            facecolor="#F4F5F7", edgecolor="#9AA8B8", linewidth=0.30, zorder=2,
        )
        ax.add_collection(pc0)
    pc = None
    if coloured_patches:
        pc = PatchCollection(coloured_patches, cmap=cmap, norm=norm,
                             edgecolor="#7A4828", linewidth=0.35, zorder=3)
        pc.set_array(np.array(vals))
        ax.add_collection(pc)

    if dash_feats:
        draw_dash_line(ax, dash_feats, color="#3A2A1C", linewidth=1.0)

    ax.set_xlim(LON_W, LON_E)
    ax.set_ylim(LAT_S, LAT_N)
    ax.set_aspect("equal")
    ax.set_facecolor("white")
    ax.axis("off")
    return pc

# ----- Figure -----
fig, axes = plt.subplots(1, 2, figsize=(15.5, 9.0),
                         facecolor="white")
fig.subplots_adjust(left=0.04, right=0.95, top=0.97, bottom=0.07, wspace=0.06)

vmax_prov = float(prov_counts.max())
vmax_city = float(city_counts.max())

pc1 = draw_map(axes[0], prov_polys, prov_counts.to_dict(),
               vmax_prov, dash_feats=prov_dashes)
pc2 = draw_map(axes[1], city_polys, city_counts.to_dict(),
               vmax_city, dash_feats=prov_dashes)

if pc1:
    cb1 = fig.colorbar(pc1, ax=axes[0], orientation="vertical",
                       fraction=0.035, pad=0.02, shrink=0.65)
    cb1.set_label("Number of policy files", fontsize=10.5, color=COLORS["ink"])
    cb1.outline.set_visible(False); cb1.ax.tick_params(labelsize=9.5)
if pc2:
    cb2 = fig.colorbar(pc2, ax=axes[1], orientation="vertical",
                       fraction=0.035, pad=0.02, shrink=0.65)
    cb2.set_label("Number of policy files", fontsize=10.5, color=COLORS["ink"])
    cb2.outline.set_visible(False); cb2.ax.tick_params(labelsize=9.5)

# Panel labels (a) (b) BELOW each map
axes[0].text(0.5, 0.02, "(a)", transform=axes[0].transAxes,
             ha="center", va="top", fontsize=13, fontweight="bold",
             color=COLORS["ink"])
axes[1].text(0.5, 0.02, "(b)", transform=axes[1].transAxes,
             ha="center", va="top", fontsize=13, fontweight="bold",
             color=COLORS["ink"])

NAME = "fig6_1_dual_map"
fig.savefig(OUT_DIR / (NAME + ".png"), dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT_DIR / (NAME + ".pdf"), bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Saved:", NAME)
