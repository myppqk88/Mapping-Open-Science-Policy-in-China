"""
Figure (Chapter 3): policy_text_processing_flowchart
====================================================
Nature-style English flowchart of the open-science policy text processing
and screening pipeline. Single vertical column, 12 steps grouped into
4 phases via background colour bands.

All geometry expressed in data-units == inches (ax has the same xlim/ylim
as the figure size), so coordinates map 1:1 to physical layout.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib import font_manager

# ----- Font: Times New Roman -> Liberation Serif (metric compatible) -----
SERIF_REG  = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_IT   = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
for p in (SERIF_REG, SERIF_BOLD, SERIF_IT):
    font_manager.fontManager.addfont(p)
plt.rcParams["font.family"]  = "serif"
plt.rcParams["font.serif"]   = ["Liberation Serif", "Times New Roman", "DejaVu Serif"]
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"]  = 42
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "01_manuscript" / "overleaf" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# (title, body[1 line, ~<=60 chars], highlight, phase_index)
STEPS = [
    ("Raw policy corpus",
     "Pkulaw.cn central and local government documents",
     "14,596 documents",                0),
    ("Metadata cleaning",
     "Deduplication; year, level, region and issuer fields standardised",
     None,                              0),
    ("Keyword-anchored retrieval",
     "Eight-category open-science lexicon applied to titles and full text",
     None,                              0),

    ("Hierarchical segmentation",
     "Chapter / section / article split; header path preserved",
     None,                              1),
    ("Text preprocessing",
     "Character normalisation; removal of contact and boilerplate info",
     None,                              1),
    ("Initial classification",
     "DeepSeek-V4-Pro entry-level semantic labelling",
     "Yes 12,055  /  No 21,392",        1),

    ("Wide-criterion re-judgement",
     "All ‘No’ entries re-evaluated under inclusive open-science criteria",
     None,                              2),
    ("High-risk re-judgement",
     "Boundary cases manually re-screened and re-included",
     "+ 9,203 entries restored",        2),
    ("Consistency review",
     "Unified exclusion rules applied; full audit log retained",
     None,                              2),

    ("Final entry table",
     "Open-science policy entries, version 5.3 (1998 – 2026)",
     "21,242 entries",                  3),
    ("File-level reconstruction",
     "Categories of each file = union of its constituent entries",
     "10,413 files",                    3),
    ("Analysis output",
     "Structural, temporal and spatial statistics; figures and tables",
     None,                              3),
]

PHASES = [
    {"name": "Phase 1.  Acquisition & Cleaning", "band": "#E9F0F7", "accent": "#3D5A80"},
    {"name": "Phase 2.  Text Structuring",       "band": "#EFEEE6", "accent": "#7A6A45"},
    {"name": "Phase 3.  Iterative Refinement",   "band": "#EAF0EA", "accent": "#3F6B47"},
    {"name": "Phase 4.  Final Outputs",          "band": "#F4EAE6", "accent": "#8C4A3C"},
]

# ----- Geometry -----
FIG_W, FIG_H = 9.5, 18.5

TITLE_Y    = 17.85
SUBTITLE_Y = 17.30
FOOT_Y     = 0.45

TOP_Y      = 16.85          # top edge of box 01
BOX_X      = 1.65
BOX_W      = 6.40
BOX_H      = 1.10
ROW_GAP    = 0.22

N = len(STEPS)

def box_top_y(i):
    return TOP_Y - i * (BOX_H + ROW_GAP)

# sanity: last box bottom must clear footer
_last_bot = box_top_y(N - 1) - BOX_H
assert _last_bot > FOOT_Y + 0.55, (
    f"Layout overflow: last box bottom = {_last_bot:.2f}, footer at {FOOT_Y:.2f}"
)

# ----- Draw -----
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# Title block
ax.text(FIG_W / 2, TITLE_Y,
        "Open-science policy text processing and screening pipeline",
        ha="center", va="top", fontsize=18, fontweight="bold",
        color="#1A2B45")
ax.text(FIG_W / 2, SUBTITLE_Y,
        "From a raw corpus of 14,596 government documents to 21,242 entries across 10,413 policy files",
        ha="center", va="top", fontsize=11.5, style="italic",
        color="#4A5A70")

# Phase background bands
phase_step_indices = {p: [i for i, s in enumerate(STEPS) if s[3] == p] for p in range(4)}
PAD = 0.18
for p, ph in enumerate(PHASES):
    idxs = phase_step_indices[p]
    band_top = box_top_y(idxs[0]) + PAD
    band_bot = box_top_y(idxs[-1]) - BOX_H - PAD
    band_h   = band_top - band_bot
    band = Rectangle((0.40, band_bot), FIG_W - 0.80, band_h,
                     linewidth=0, facecolor=ph["band"], alpha=0.55)
    ax.add_patch(band)
    ax.text(0.82, (band_top + band_bot) / 2, ph["name"],
            ha="center", va="center", rotation=90,
            fontsize=11.5, fontweight="bold", color=ph["accent"])

# Boxes — 3 vertical zones inside each box
TITLE_DY = 0.26     # title text top is this far below box top
BODY_DY  = 0.58     # body text top
HL_DY    = 0.24     # highlight (anchored from bottom of box)

for i, (title, body, highlight, p) in enumerate(STEPS):
    accent = PHASES[p]["accent"]
    y_top  = box_top_y(i)
    y_bot  = y_top - BOX_H
    # Outer box
    ax.add_patch(FancyBboxPatch(
        (BOX_X, y_bot), BOX_W, BOX_H,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.0, edgecolor=accent,
        facecolor="white",
    ))
    # Step number badge
    ax.text(BOX_X + 0.22, y_top - TITLE_DY, f"{i+1:02d}",
            ha="left", va="top", fontsize=11, fontweight="bold",
            color=accent)
    # Title
    ax.text(BOX_X + 0.82, y_top - TITLE_DY, title,
            ha="left", va="top", fontsize=13, fontweight="bold",
            color="#1F2B40")
    # Body
    ax.text(BOX_X + 0.82, y_top - BODY_DY, body,
            ha="left", va="top", fontsize=10.2, color="#34465E")
    # Highlight (italic bold accent text, bottom-right; NO bbox to avoid overlap)
    if highlight:
        ax.text(BOX_X + BOX_W - 0.22, y_bot + HL_DY, highlight,
                ha="right", va="center",
                fontsize=10.7, fontweight="bold", style="italic",
                color=accent)

# Vertical connecting arrows
for i in range(N - 1):
    y_bot_up   = box_top_y(i) - BOX_H
    y_top_down = box_top_y(i + 1)
    x_mid = BOX_X + BOX_W / 2
    ax.add_patch(FancyArrowPatch(
        (x_mid, y_bot_up - 0.01), (x_mid, y_top_down + 0.01),
        arrowstyle="-|>", mutation_scale=12,
        linewidth=1.2, color="#4A5A70",
    ))

# Footer
ax.text(FIG_W / 2, FOOT_Y,
        "DeepSeek-V4-Pro performs initial entry classification; ‘No’ entries are re-evaluated by an inclusive semantic\n"
        "re-judgement, boundary cases by a high-risk re-judgement, and the union is confirmed by a consistency review\n"
        "with full audit trail.",
        ha="center", va="bottom", fontsize=9.7, style="italic",
        color="#475568", linespacing=1.35)

fig.savefig(OUT / "policy_text_processing_flowchart.png",
            dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(OUT / "policy_text_processing_flowchart.pdf",
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved: {OUT/'policy_text_processing_flowchart.png'}")
print(f"Saved: {OUT/'policy_text_processing_flowchart.pdf'}")
