"""
Export province- and city-level policy file counts as CSVs
for use with online Chinese map-making tools (e.g. 镝数图表,
Datawrapper, 百度地图开放平台).

Output:
    03_outputs/tables/province_policy_counts.csv
    03_outputs/tables/city_policy_counts.csv

Columns:
    province_policy_counts.csv
        name_zh       : 中文名 (full, e.g. 江苏省)
        name_short_zh : 中文简称 (e.g. 江苏)
        name_en       : English name
        file_count    : 政策文件数
    city_policy_counts.csv
        city_zh       : 市名 (e.g. 苏州市)
        province_zh   : 所属省份
        file_count    : 政策文件数
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FILES_XLSX    = ROOT / "02_data" / "final_entries" / "政策文件表_v5.3.xlsx"
ENTRIES_XLSX  = ROOT / "02_data" / "final_entries" / "开放科学政策数据_最终版_v5.3.xlsx"

OUT_DIR = ROOT / "03_outputs" / "tables"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Province table
# ------------------------------------------------------------------
PROVINCES = [
    ("北京市",        "北京",   "Beijing"),
    ("天津市",        "天津",   "Tianjin"),
    ("河北省",        "河北",   "Hebei"),
    ("山西省",        "山西",   "Shanxi"),
    ("内蒙古自治区",   "内蒙古", "Inner Mongolia"),
    ("辽宁省",        "辽宁",   "Liaoning"),
    ("吉林省",        "吉林",   "Jilin"),
    ("黑龙江省",      "黑龙江", "Heilongjiang"),
    ("上海市",        "上海",   "Shanghai"),
    ("江苏省",        "江苏",   "Jiangsu"),
    ("浙江省",        "浙江",   "Zhejiang"),
    ("安徽省",        "安徽",   "Anhui"),
    ("福建省",        "福建",   "Fujian"),
    ("江西省",        "江西",   "Jiangxi"),
    ("山东省",        "山东",   "Shandong"),
    ("河南省",        "河南",   "Henan"),
    ("湖北省",        "湖北",   "Hubei"),
    ("湖南省",        "湖南",   "Hunan"),
    ("广东省",        "广东",   "Guangdong"),
    ("广西壮族自治区", "广西",   "Guangxi"),
    ("海南省",        "海南",   "Hainan"),
    ("重庆市",        "重庆",   "Chongqing"),
    ("四川省",        "四川",   "Sichuan"),
    ("贵州省",        "贵州",   "Guizhou"),
    ("云南省",        "云南",   "Yunnan"),
    ("西藏自治区",    "西藏",   "Tibet"),
    ("陕西省",        "陕西",   "Shaanxi"),
    ("甘肃省",        "甘肃",   "Gansu"),
    ("青海省",        "青海",   "Qinghai"),
    ("宁夏回族自治区", "宁夏",   "Ningxia"),
    ("新疆维吾尔自治区","新疆",  "Xinjiang"),
    ("台湾省",        "台湾",   "Taiwan"),
    ("香港特别行政区", "香港",   "Hong Kong"),
    ("澳门特别行政区", "澳门",   "Macao"),
]

files = pd.read_excel(FILES_XLSX)
# Take primary province only (first segment if joint issuance)
files["prov"] = (files["province_raw"].astype(str)
                 .str.split(";").str[0].str.strip())
files = files[files["governance_level"].isin(["省级", "地市级"])]

prov_counts = files.groupby("prov").size().to_dict()

prov_rows = []
for full, short, en in PROVINCES:
    prov_rows.append({
        "name_zh":       full,
        "name_short_zh": short,
        "name_en":       en,
        "file_count":    int(prov_counts.get(full, 0)),
    })

prov_df = pd.DataFrame(prov_rows)
prov_df = prov_df.sort_values("file_count", ascending=False).reset_index(drop=True)

# Write with UTF-8 BOM so Chinese tools / Excel show 中文 correctly
prov_out = OUT_DIR / "province_policy_counts.csv"
prov_df.to_csv(prov_out, index=False, encoding="utf-8-sig")
print(f"Saved provinces: {prov_out}")
print(f"  total provinces: {len(prov_df)}")
print(f"  with data: {(prov_df['file_count'] > 0).sum()}")
print(f"  top 5:\n{prov_df.head(5).to_string(index=False)}")

# ------------------------------------------------------------------
# City table
# ------------------------------------------------------------------
entries = pd.read_excel(ENTRIES_XLSX)
city = entries[entries["governance_level"] == "地市级"].copy()
city["city_raw"]     = city["city_raw"].astype(str).str.strip()
city["province_raw"] = (city["province_raw"].astype(str)
                        .str.split(";").str[0].str.strip())

city_counts = (
    city.groupby(["province_raw", "city_raw"])["policy_file_id"]
    .nunique().reset_index(name="file_count")
)
city_counts = city_counts.rename(columns={
    "city_raw": "city_zh", "province_raw": "province_zh",
})
city_counts = city_counts[
    (city_counts["city_zh"] != "nan") &
    (city_counts["city_zh"] != "") &
    (city_counts["province_zh"] != "nan")
]
city_counts = city_counts.sort_values("file_count", ascending=False).reset_index(drop=True)

city_out = OUT_DIR / "city_policy_counts.csv"
city_counts[["city_zh", "province_zh", "file_count"]].to_csv(
    city_out, index=False, encoding="utf-8-sig",
)
print(f"\nSaved cities: {city_out}")
print(f"  total cities: {len(city_counts)}")
print(f"  top 10:\n{city_counts.head(10).to_string(index=False)}")
