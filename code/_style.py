"""
Shared Nature-style matplotlib helper.

Usage:
    from _style import apply_style, COLORS, CATEGORIES, REGIONS
    apply_style()
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path

SERIF_REG  = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_IT   = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

# Eight open-science categories (fixed order)
CATEGORIES = [
    ("OA",   "Open Access"),
    ("OD",   "Open Data"),
    ("OSS",  "Open Source Software"),
    ("OERs", "Open Educational Resources"),
    ("CS",   "Citizen Science"),
    ("OPR",  "Open Peer Review"),
    ("OI",   "Open Infrastructure"),
    ("ORM",  "Open Research Methods"),
]
CAT_CODES = [c for c, _ in CATEGORIES]
CAT_NAMES = [n for _, n in CATEGORIES]

# Three policy stages (from PROGRESS.md)
STAGES = [
    ("S1", 1998, 2005, "S1: Initiation (1998–2005)",     "#F5F9FC"),
    ("S2", 2006, 2015, "S2: Take-off (2006–2015)",       "#ECF3F9"),
    ("S3", 2016, 2025, "S3: Diffusion (2016–2025)",      "#E6EFF6"),
]

# Four economic regions
REGIONS = {
    "East":      ["北京", "天津", "河北", "上海", "江苏", "浙江", "福建", "山东", "广东", "海南"],
    "Central":   ["山西", "安徽", "江西", "河南", "湖北", "湖南"],
    "West":      ["内蒙古", "广西", "重庆", "四川", "贵州", "云南", "西藏",
                  "陕西", "甘肃", "青海", "宁夏", "新疆"],
    "Northeast": ["辽宁", "吉林", "黑龙江"],
}
REGION_ORDER = ["East", "Central", "West", "Northeast"]
REGION_COLORS = {
    "East":      "#2E5A88",
    "Central":   "#C46A3B",
    "West":      "#5B7D4F",
    "Northeast": "#7B4A8C",
}

# Province name normalisation: short form -> full
PROV_SHORT_TO_FULL = {
    "北京": "北京市", "天津": "天津市", "河北": "河北省", "山西": "山西省",
    "内蒙古": "内蒙古自治区", "辽宁": "辽宁省", "吉林": "吉林省", "黑龙江": "黑龙江省",
    "上海": "上海市", "江苏": "江苏省", "浙江": "浙江省", "安徽": "安徽省",
    "福建": "福建省", "江西": "江西省", "山东": "山东省", "河南": "河南省",
    "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省", "广西": "广西壮族自治区",
    "海南": "海南省", "重庆": "重庆市", "四川": "四川省", "贵州": "贵州省",
    "云南": "云南省", "西藏": "西藏自治区", "陕西": "陕西省", "甘肃": "甘肃省",
    "青海": "青海省", "宁夏": "宁夏回族自治区", "新疆": "新疆维吾尔自治区",
}
PROV_FULL_TO_SHORT = {v: k for k, v in PROV_SHORT_TO_FULL.items()}

# Curated palette
COLORS = {
    "primary":   "#2E5A88",
    "secondary": "#C46A3B",
    "tertiary":  "#5B7D4F",
    "accent":    "#7B4A8C",
    "ink":       "#1A2B45",
    "text":      "#34465E",
    "muted":     "#6C7A8B",
    "rule":      "#B7C2CC",
}


def apply_style():
    """Apply Nature-style matplotlib rcParams. Tries to register the
    bundled Liberation Serif (Linux/macOS) but silently falls back to
    whatever serif font matplotlib finds on the system — on Windows
    this is normally the real Times New Roman."""
    import os as _os
    for p in (SERIF_REG, SERIF_BOLD, SERIF_IT):
        if _os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
            except Exception:
                pass
    plt.rcParams.update({
        "font.family":       "serif",
        # Order matters: matplotlib uses the first available font.
        # Windows usually has Times New Roman; Linux/macOS often have
        # Liberation Serif which is metric-compatible.
        "font.serif":        ["Times New Roman", "Liberation Serif",
                              "DejaVu Serif", "serif"],
        "mathtext.fontset":  "stix",
        "axes.titlesize":    12,
        "axes.labelsize":    11,
        "axes.labelcolor":   COLORS["ink"],
        "axes.edgecolor":    COLORS["ink"],
        "axes.linewidth":    0.9,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.titleweight":  "bold",
        "axes.titlecolor":   COLORS["ink"],
        "xtick.color":       COLORS["text"],
        "ytick.color":       COLORS["text"],
        "xtick.labelsize":   9.5,
        "ytick.labelsize":   9.5,
        "xtick.direction":   "out",
        "ytick.direction":   "out",
        "xtick.major.size":  3,
        "ytick.major.size":  3,
        "legend.fontsize":   9.5,
        "legend.frameon":    False,
        "pdf.fonttype":      42,
        "ps.fonttype":       42,
        "axes.unicode_minus": False,
        "figure.dpi":        120,
        "savefig.dpi":       300,
        "savefig.bbox":      "tight",
        "savefig.facecolor": "white",
    })


def province_region(province_full_name: str):
    """Return region label ('East', 'Central', 'West', 'Northeast') or None."""
    short = PROV_FULL_TO_SHORT.get(province_full_name)
    if short is None:
        # try to handle short already
        short = province_full_name.replace("省", "").replace("市", "").replace("自治区", "")
        short = short.replace("壮族", "").replace("回族", "").replace("维吾尔", "")
    for region, members in REGIONS.items():
        if short in members:
            return region
    return None


OUT_DIR = Path(__file__).resolve().parent.parent / "01_manuscript" / "overleaf" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
