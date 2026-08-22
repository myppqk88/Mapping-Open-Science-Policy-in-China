"""
Comprehensive data audit Excel for manuscript v5.3.
Builds 04_audit/data_audit_master_v5.3.xlsx with sheets covering all
numerical claims in chapters 4-6 + methodology, reproducible from
source data files.
"""
from pathlib import Path
import sys
import re
import numpy as np
import pandas as pd
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "02_data" / "final_entries" / "开放科学政策数据_最终版_v5.3.xlsx"
TECH_PANEL = ROOT / "02_data" / "technology_indicators" / "分省科技指标面板数据_1998_2024.xlsx"
TECH_INDEX = ROOT / "02_data" / "technology_indicators" / "分省科技综合指数_熵权法_1998_2024.xlsx"
OUT = ROOT / "04_audit" / "data_audit_master_v5.3.xlsx"

CAT_ORDER = ["OERs", "OI", "OD", "CS", "OSS", "OPR", "OA", "ORM"]

REGIONS = {
    "East":      ["北京", "天津", "河北", "上海", "江苏", "浙江", "福建", "山东", "广东", "海南"],
    "Central":   ["山西", "安徽", "江西", "河南", "湖北", "湖南"],
    "West":      ["内蒙古", "广西", "重庆", "四川", "贵州", "云南", "西藏",
                  "陕西", "甘肃", "青海", "宁夏", "新疆"],
    "Northeast": ["辽宁", "吉林", "黑龙江"],
}
REGION_ORDER = ["East", "Central", "West", "Northeast"]

def prov_to_region(prov_full):
    if pd.isna(prov_full) or prov_full == "中央":
        return None
    s = str(prov_full).replace("省", "").replace("市", "").replace("自治区", "")
    s = s.replace("壮族", "").replace("回族", "").replace("维吾尔", "")
    s = s.split(";")[0]  # take first if joint
    for region, members in REGIONS.items():
        if s in members:
            return region
    return None


# ============================================================
# Load data
# ============================================================
print("Loading source data...")
entries_all = pd.read_excel(DATA, sheet_name="政策条目")
files_all   = pd.read_excel(DATA, sheet_name="政策文件")

entries = entries_all[entries_all["issue_year"] >= 1998].copy()
files   = files_all[files_all["issue_year"] >= 1998].copy()

# Apply region tag
files["region"] = files["province"].apply(prov_to_region)
entries["region"] = entries.get("province_raw",
                                entries.get("province")).apply(prov_to_region)

# Expanded entries
e_main = entries[entries["category_codes"] != "OS_general"].copy()
exploded = e_main.assign(cat=e_main["category_codes"].str.split("|")).explode("cat")

# Stage labels
def stage_of(yr):
    if yr < 1998: return None
    if yr <= 2005: return "S1"
    if yr <= 2015: return "S2"
    if yr <= 2025: return "S3"
    return None  # 2026

# ============================================================
# Sheet writers
# ============================================================
sheets = {}

# ----- 00 Metadata -----
sheets["00_目录"] = pd.DataFrame({
    "Sheet": [
        "00_目录", "00_元数据",
        "ANOMALY_吉林分类错误", "ANOMALY_省级机关误判地市级",
        "Ch4_T1_范畴构成", "Ch4_T2_治理层级",
        "Ch4_T3_多范畴文件", "Ch4_T4_Jaccard矩阵",
        "Ch4_T5_共现计数", "Ch4_T6_组合频次",
        "Ch5_T1_年度时序", "Ch5_T2_阶段统计",
        "Ch5_T3_断点检测", "Ch5_T4_年度范畴",
        "Ch5_T5_全国政策强度", "Ch5_T6_全国科技指数",
        "Ch5_T7_全国象限",
        "Ch6_T1_分省文件", "Ch6_T2_分市文件",
        "Ch6_T3_四区域汇总", "Ch6_T4_区域范畴",
        "Ch6_T5_分省阶段强度", "Ch6_T6_分省阶段科技",
        "Ch6_T7_分省阶段象限", "Ch6_T8_区域阶段象限",
        "M1_熵权计算结果", "M2_熵权原始面板",
    ],
    "正文对应位置": [
        "目录", "数据版本与生成元信息",
        "数据异常: 吉林166份全部归地市级", "数据异常: 标题含省级机关字样但归地市级",
        "4.1 范畴构成 / Figure 4.1(a)(b)", "4.1 治理层级 / Figure 4.1(c)(d)",
        "4.2 多范畴文件分布", "4.2 / Figure 4.2 Jaccard矩阵",
        "4.2 共现文件数", "4.2 文中最常见组合统计",
        "5.1 年度政策时序 / Figure 5.1(a)", "5.1 阶段统计",
        "5.1 阶段断点 / Dynp", "5.1 / Figure 5.1(b-i)",
        "5.2 全国政策强度指数 O_t*", "5.2 全国科技综合指数 S_t",
        "5.2 全国象限分类",
        "6.1 / Figure 6.1 分省文件", "6.1 分市文件热图",
        "6.1 四区域文件占比", "6.2 / Figure 6.2 区域范畴热图",
        "6.3 分省阶段政策强度", "6.3 分省阶段科技指数",
        "6.3 / Figure 6.3 分省阶段象限", "6.3 四区域阶段象限统计",
        "3.3.3 熵权计算结果", "3.3.3 熵权法原始观测面板",
    ],
})

sheets["00_元数据"] = pd.DataFrame({
    "项目": [
        "数据版本", "源文件1", "源文件2", "源文件3",
        "政策条目总数", "政策文件总数",
        "条目年份范围", "文件年份范围",
        "分析期", "审计生成时间",
    ],
    "值": [
        "v5.3 (2026-05-11 cleaning)",
        "02_data/final_entries/开放科学政策数据_最终版_v5.3.xlsx",
        "02_data/technology_indicators/分省科技指标面板数据_1998_2024.xlsx",
        "02_data/technology_indicators/分省科技综合指数_熵权法_1998_2024.xlsx",
        len(entries_all), len(files_all),
        f"{entries_all['issue_year'].min()}-{entries_all['issue_year'].max()}",
        f"{files_all['issue_year'].min()}-{files_all['issue_year'].max()}",
        "1998-2026 (2026 不纳入阶段统计)",
        datetime.now().isoformat(timespec="seconds"),
    ],
})

# ----- ANOMALY sheets -----
jilin = files_all[files_all["province"].astype(str).str.contains("吉林", na=False)].copy()
jilin_summary = pd.DataFrame({
    "省份": ["吉林省"],
    "总文件数": [len(jilin)],
    "中央": [(jilin["governance_level"] == "中央").sum()],
    "省级": [(jilin["governance_level"] == "省级").sum()],
    "地市级": [(jilin["governance_level"] == "地市级").sum()],
    "标题含省级机关字样": [jilin["policy_title"].astype(str).str.contains(
        r"省委|省人民政府|省政府|省办公厅|省直|省教育厅|省科技厅", regex=True, na=False
    ).sum()],
    "说明": ["所有166份吉林省文件均归地市级，省级为0；其中64份标题明确含省级机关字样，应归入省级"],
})
sheets["ANOMALY_吉林分类错误"] = pd.concat([
    jilin_summary,
    pd.DataFrame({"省份": ["—"], "总文件数": ["—"], "中央": ["—"], "省级": ["—"],
                  "地市级": ["—"], "标题含省级机关字样": ["—"], "说明": ["以下为问题文件明细"]}),
    jilin.assign(说明="").rename(columns={"policy_file_id": "省份"})[
        ["省份", "policy_title", "governance_level", "city", "issue_year"]
    ].rename(columns={"policy_title": "总文件数",
                      "governance_level": "中央",
                      "city": "省级", "issue_year": "地市级"})
], ignore_index=True)

mis_pattern = r"省委|省人民政府|省政府|省办公厅|省直|省教育厅|省科技厅|省财政厅|自治区委|自治区人民政府|自治区政府"
mis = files_all[(files_all["governance_level"] == "地市级") &
                (files_all["policy_title"].astype(str).str.contains(mis_pattern, regex=True, na=False))]
sheets["ANOMALY_省级机关误判地市级"] = pd.concat([
    pd.DataFrame({
        "省份": ["按省份汇总"],
        "policy_file_id": [""], "policy_title": [""],
        "governance_level": [""], "city": [""], "issue_year": [""],
    }),
    mis.groupby("province").size().reset_index(name="文件数").rename(
        columns={"province": "省份", "文件数": "policy_file_id"}
    ).assign(policy_title="", governance_level="", city="", issue_year=""),
    pd.DataFrame({
        "省份": ["---明细---"],
        "policy_file_id": [""], "policy_title": [""],
        "governance_level": [""], "city": [""], "issue_year": [""],
    }),
    mis[["province", "policy_file_id", "policy_title",
         "governance_level", "city", "issue_year"]].rename(columns={"province": "省份"}),
], ignore_index=True)

# ----- Chapter 4 -----
print("Building Ch4 sheets...")

# T1 范畴构成
total_exp = len(exploded)
t1_rows = []
for cat in CAT_ORDER:
    pat = r"(?:^|\|)" + re.escape(cat) + r"(?:\||$)"
    n_files = files["category_codes"].fillna("").str.contains(pat, regex=True).sum()
    n_entries_exp = int((exploded["cat"] == cat).sum())
    t1_rows.append({
        "Category": cat,
        "Policy_files": n_files,
        "File_share_pct": round(n_files / len(files) * 100, 2),
        "Entry_count_expanded": n_entries_exp,
        "Entry_share_pct": round(n_entries_exp / total_exp * 100, 2),
    })
sheets["Ch4_T1_范畴构成"] = pd.DataFrame(t1_rows)

# T2 治理层级
t2_rows = []
for cat in CAT_ORDER:
    row = {"Category": cat}
    for lvl_en, lvl_zh in [("Central", "中央"), ("Provincial", "省级"), ("Municipal", "地市级")]:
        sub = exploded[exploded["governance_level"] == lvl_zh]
        n = int((sub["cat"] == cat).sum())
        row[f"{lvl_en}_n"] = n
        row[f"{lvl_en}_share_pct"] = round(n / len(sub) * 100, 2)
    t2_rows.append(row)
sheets["Ch4_T2_治理层级"] = pd.DataFrame(t2_rows)

# T3 多范畴文件
def count_main_cats(s):
    if pd.isna(s) or s == "": return 0
    return len([c for c in str(s).split("|") if c != "OS_general"])
ncat = files["category_codes"].apply(count_main_cats)
sheets["Ch4_T3_多范畴文件"] = pd.DataFrame({
    "范畴数": ["0 (仅OS_general)", "1", "2", "3", "4+", "合计"],
    "文件数": [int((ncat == 0).sum()), int((ncat == 1).sum()),
              int((ncat == 2).sum()), int((ncat == 3).sum()),
              int((ncat >= 4).sum()), len(files)],
})

# T4 Jaccard 矩阵
file_cat_sets = files["category_codes"].fillna("").apply(
    lambda s: set(s.split("|")) - {"OS_general", ""}
)
n_cats = len(CAT_ORDER)
jac = np.zeros((n_cats, n_cats))
co  = np.zeros((n_cats, n_cats), dtype=int)
for i, c1 in enumerate(CAT_ORDER):
    for j, c2 in enumerate(CAT_ORDER):
        inter = sum((c1 in s) and (c2 in s) for s in file_cat_sets)
        union = sum((c1 in s) or  (c2 in s) for s in file_cat_sets)
        co[i, j]  = inter
        jac[i, j] = inter / union if union > 0 else 0
sheets["Ch4_T4_Jaccard矩阵"] = pd.DataFrame(
    np.round(jac, 4), index=CAT_ORDER, columns=CAT_ORDER
).reset_index().rename(columns={"index": "Category"})
sheets["Ch4_T5_共现计数"] = pd.DataFrame(
    co, index=CAT_ORDER, columns=CAT_ORDER
).reset_index().rename(columns={"index": "Category"})

# T6 组合频次
combo = files[files["n_categories"] >= 2]["category_codes"].value_counts().head(30)
sheets["Ch4_T6_组合频次"] = pd.DataFrame({
    "组合": combo.index, "文件数": combo.values
})

# ----- Chapter 5 -----
print("Building Ch5 sheets...")

# T1 年度时序
yr_files = files_all.groupby("issue_year").size()
yr_entries = entries_all.groupby("issue_year").size()
years_all = sorted(set(files_all["issue_year"]).union(entries_all["issue_year"]))
sheets["Ch5_T1_年度时序"] = pd.DataFrame({
    "Year": years_all,
    "Files": [int(yr_files.get(y, 0)) for y in years_all],
    "Entries": [int(yr_entries.get(y, 0)) for y in years_all],
})

# T2 阶段统计
ent_s = entries.copy()
ent_s["stage"] = ent_s["issue_year"].apply(stage_of)
fil_s = files.copy()
fil_s["stage"] = fil_s["issue_year"].apply(stage_of)
stage_rows = []
for s in ["S1", "S2", "S3"]:
    sub_f = fil_s[fil_s["stage"] == s]
    sub_e = ent_s[ent_s["stage"] == s]
    stage_rows.append({
        "Stage": s,
        "Period": {"S1": "1998-2005", "S2": "2006-2015", "S3": "2016-2025"}[s],
        "Files": len(sub_f),
        "Entries": len(sub_e),
        "Avg_files_per_year": round(len(sub_f) / {"S1": 8, "S2": 10, "S3": 10}[s], 1),
    })
stage_rows.append({
    "Stage": "2026 (excluded)", "Period": "2026",
    "Files": int((files_all["issue_year"] == 2026).sum()),
    "Entries": int((entries_all["issue_year"] == 2026).sum()),
    "Avg_files_per_year": "",
})
sheets["Ch5_T2_阶段统计"] = pd.DataFrame(stage_rows)

# T3 断点检测
try:
    import ruptures as rpt
    series = np.array([int(yr_files.get(y, 0)) for y in range(1998, 2026)])
    algo = rpt.Dynp(model="rbf").fit(series)
    bkps = []
    for n_bkps in (1, 2, 3, 4):
        try:
            result = algo.predict(n_bkps=n_bkps)
            bkps.append({"n_breakpoints": n_bkps,
                         "breakpoint_indices": str(result[:-1]),
                         "breakpoint_years": str([1998 + i for i in result[:-1]])})
        except Exception as ex:
            bkps.append({"n_breakpoints": n_bkps, "breakpoint_indices": f"err: {ex}",
                         "breakpoint_years": ""})
    sheets["Ch5_T3_断点检测"] = pd.DataFrame(bkps)
except ImportError:
    sheets["Ch5_T3_断点检测"] = pd.DataFrame({
        "note": ["ruptures package not available — install with `pip install ruptures`"]
    })

# T4 年度范畴
yr_cat = (e_main.assign(cat=e_main["category_codes"].str.split("|"))
                 .explode("cat")
                 .groupby(["issue_year", "cat"]).size()
                 .unstack(fill_value=0).reindex(columns=CAT_ORDER, fill_value=0))
sheets["Ch5_T4_年度范畴"] = yr_cat.reset_index()

# T5 全国政策强度指数
years_an = np.arange(1998, 2025)
F_t = np.array([int(yr_files.get(y, 0)) for y in years_an])
E_t = np.array([int(yr_entries.get(y, 0)) for y in years_an])

def minmax(arr):
    a = np.array(arr, dtype=float)
    rng = a.max() - a.min()
    return (a - a.min()) / rng if rng > 0 else np.zeros_like(a)

F_log = np.log1p(F_t)
E_log = np.log1p(E_t)
F_star = minmax(F_log)
E_star = minmax(E_log)
O_star = minmax(F_star + E_star)

sheets["Ch5_T5_全国政策强度"] = pd.DataFrame({
    "Year": years_an, "F_t": F_t, "E_t": E_t,
    "log1p_F": np.round(F_log, 4), "log1p_E": np.round(E_log, 4),
    "F_star": np.round(F_star, 4), "E_star": np.round(E_star, 4),
    "O_star": np.round(O_star, 4),
})

# T6 全国科技综合指数
tech_panel = pd.read_excel(TECH_PANEL)
tech_idx = pd.read_excel(TECH_INDEX, sheet_name="分省科技综合指数")
entropy_calc = pd.read_excel(TECH_INDEX, sheet_name="熵权计算")

national_tech = tech_panel.groupby("年份")[
    ["R&D人员全时当量", "R&D经费内部支出", "专利授权数", "技术市场成交额"]
].sum().reset_index()
# Apply same entropy weights to national totals
weights = entropy_calc.set_index("指标")["熵权"]
nat_z = national_tech.copy()
for col in weights.index:
    a = nat_z[col].values
    rng = a.max() - a.min()
    nat_z[col + "_z"] = (a - a.min()) / rng if rng > 0 else 0
national_tech["S_score"] = sum(
    nat_z[col + "_z"] * weights[col] for col in weights.index
)
national_tech["S_index_0_100"] = minmax(national_tech["S_score"]) * 100
national_tech["S_star_minmax01"] = minmax(national_tech["S_score"])
sheets["Ch5_T6_全国科技指数"] = national_tech.round(4)

# T7 全国象限分类
nat_for_q = national_tech[national_tech["年份"].isin(years_an)].copy()
S_star = nat_for_q["S_star_minmax01"].values
O_median = np.median(O_star)
S_median = np.median(S_star)
def quadrant(o, s, om, sm):
    if o >= om and s >= sm: return "HH (协同领先)"
    if o >= om and s <  sm: return "HL (政策驱动)"
    if o <  om and s >= sm: return "LH (科技先行)"
    return "LL (双低滞后)"
sheets["Ch5_T7_全国象限"] = pd.DataFrame({
    "Year": years_an,
    "O_star": np.round(O_star, 4),
    "S_star": np.round(S_star, 4),
    "O_median": round(float(O_median), 4),
    "S_median": round(float(S_median), 4),
    "Quadrant": [quadrant(o, s, O_median, S_median) for o, s in zip(O_star, S_star)],
})

# ----- Chapter 6 -----
print("Building Ch6 sheets...")

# T1 分省文件
prov_files = files[files["governance_level"].isin(["省级", "地市级"])].copy()
prov_summary = prov_files.groupby("province").agg(
    Files=("policy_file_id", "count"),
    Provincial_files=("governance_level",
                      lambda s: (s == "省级").sum()),
    Municipal_files=("governance_level",
                     lambda s: (s == "地市级").sum()),
).reset_index().rename(columns={"province": "Province"})
prov_summary["Region"] = prov_summary["Province"].apply(prov_to_region)

# Add entry counts
prov_entries = entries[entries["governance_level"].isin(["省级", "地市级"])].copy()
prov_entries["prov_first"] = prov_entries["province_raw"].astype(str).str.split(";").str[0]
ent_count = prov_entries.groupby("prov_first").size().to_dict()

# Map full province name back
prov_summary["Entries"] = prov_summary["Province"].map(
    lambda p: ent_count.get(p, 0)
)
sheets["Ch6_T1_分省文件"] = prov_summary.sort_values("Files", ascending=False)

# T2 分市文件
city_files = files[files["governance_level"] == "地市级"].copy()
city_summary = city_files.groupby(["province", "city"]).size().reset_index(name="Files")
city_summary.columns = ["Province", "City", "Files"]
sheets["Ch6_T2_分市文件"] = city_summary.sort_values("Files", ascending=False)

# T3 四区域汇总
prov_files["region"] = prov_files["province"].apply(prov_to_region)
prov_files = prov_files[prov_files["region"].notna()]
reg_summary = prov_files.groupby("region").size().reindex(REGION_ORDER).reset_index()
reg_summary.columns = ["Region", "Files"]
reg_summary["File_share_pct"] = round(reg_summary["Files"] / reg_summary["Files"].sum() * 100, 2)
prov_entries["region"] = prov_entries["prov_first"].apply(prov_to_region)
ent_reg = prov_entries.groupby("region").size().reindex(REGION_ORDER)
reg_summary["Entries"] = [int(ent_reg.get(r, 0)) for r in reg_summary["Region"]]
sheets["Ch6_T3_四区域汇总"] = reg_summary

# T4 区域范畴
ent_for_reg = exploded[exploded["governance_level"].isin(["省级", "地市级"])].copy()
ent_for_reg["prov_first"] = ent_for_reg["province_raw"].astype(str).str.split(";").str[0]
ent_for_reg["region"] = ent_for_reg["prov_first"].apply(prov_to_region)
ent_for_reg = ent_for_reg[ent_for_reg["region"].notna()]
reg_cat_n = ent_for_reg.groupby(["region", "cat"]).size().unstack(fill_value=0).reindex(REGION_ORDER)[CAT_ORDER]
reg_totals = reg_cat_n.sum(axis=1)
reg_cat_share = reg_cat_n.div(reg_totals, axis=0) * 100
out_t4 = pd.concat([reg_cat_n.add_suffix("_n"), reg_cat_share.round(2).add_suffix("_pct")], axis=1)
out_t4.insert(0, "Region_total_entries", reg_totals)
sheets["Ch6_T4_区域范畴"] = out_t4.reset_index()

# T5 分省阶段强度
prov_stage_files = prov_files.copy()
prov_stage_files["stage"] = prov_stage_files["issue_year"].apply(stage_of)
prov_stage_files = prov_stage_files[prov_stage_files["stage"].notna()]
prov_stage_F = prov_stage_files.groupby(["province", "stage"]).size().unstack(fill_value=0).reindex(columns=["S1","S2","S3"], fill_value=0)
prov_stage_F.columns = [f"F_{c}" for c in prov_stage_F.columns]

# O_star per (province, stage): log + minmax within (province, stage) pool
rows_strength = []
for stage in ["S1", "S2", "S3"]:
    col = f"F_{stage}"
    if col in prov_stage_F.columns:
        F_arr = prov_stage_F[col].values
        F_log_p = np.log1p(F_arr)
        F_star_p = minmax(F_log_p)
        for prov, fval, fstar in zip(prov_stage_F.index, F_arr, F_star_p):
            rows_strength.append({
                "Province": prov, "Stage": stage,
                "F": int(fval), "log1p_F": round(float(F_log_p[list(prov_stage_F.index).index(prov)]), 4),
                "O_star": round(float(fstar), 4),
            })
sheets["Ch6_T5_分省阶段强度"] = pd.DataFrame(rows_strength)

# T6 分省阶段科技
# Average science index per (province, stage), then minmax within stage
prov_full = sorted(prov_files["province"].unique())
tech_idx_p = tech_idx.copy()
tech_idx_p["stage"] = tech_idx_p["年份"].apply(lambda y: stage_of(y) if y <= 2024 else None)
prov_stage_T = tech_idx_p.groupby(["省份", "stage"])["科技综合指数"].mean().reset_index()
# Map short province name to full from technology data — already short like 上海, 北京
# Need mapping back to "上海市" etc
short_to_full = {
    "上海": "上海市", "北京": "北京市", "天津": "天津市", "重庆": "重庆市", "河北": "河北省",
    "山西": "山西省", "辽宁": "辽宁省", "吉林": "吉林省", "黑龙江": "黑龙江省", "江苏": "江苏省",
    "浙江": "浙江省", "安徽": "安徽省", "福建": "福建省", "江西": "江西省", "山东": "山东省",
    "河南": "河南省", "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省", "海南": "海南省",
    "四川": "四川省", "贵州": "贵州省", "云南": "云南省", "陕西": "陕西省", "甘肃": "甘肃省",
    "青海": "青海省", "内蒙古": "内蒙古自治区", "广西": "广西壮族自治区", "西藏": "西藏自治区",
    "宁夏": "宁夏回族自治区", "新疆": "新疆维吾尔自治区",
}
prov_stage_T["Province"] = prov_stage_T["省份"].map(short_to_full)

# Min-max within stage
results_t = []
for stage in ["S1", "S2", "S3"]:
    sub = prov_stage_T[prov_stage_T["stage"] == stage].copy()
    if len(sub) > 0:
        sub["T_star"] = minmax(sub["科技综合指数"].values)
        for _, r in sub.iterrows():
            results_t.append({
                "Province": r["Province"], "Stage": stage,
                "Sci_mean": round(float(r["科技综合指数"]), 4),
                "T_star": round(float(r["T_star"]), 4),
            })
sheets["Ch6_T6_分省阶段科技"] = pd.DataFrame(results_t)

# T7 分省阶段象限
df5 = pd.DataFrame(rows_strength)
df6 = pd.DataFrame(results_t)
merged = df5.merge(df6, on=["Province", "Stage"], how="inner")
results_q = []
for stage in ["S1", "S2", "S3"]:
    sub = merged[merged["Stage"] == stage].copy()
    if len(sub) > 0:
        om = sub["O_star"].median()
        sm = sub["T_star"].median()
        for _, r in sub.iterrows():
            results_q.append({
                "Province": r["Province"], "Stage": stage,
                "O_star": r["O_star"], "T_star": r["T_star"],
                "O_median": round(float(om), 4), "T_median": round(float(sm), 4),
                "Quadrant": quadrant(r["O_star"], r["T_star"], om, sm),
            })
sheets["Ch6_T7_分省阶段象限"] = pd.DataFrame(results_q)

# T8 区域阶段象限
df_q = pd.DataFrame(results_q)
df_q["Region"] = df_q["Province"].apply(prov_to_region)
quad_summary = df_q.groupby(["Region", "Stage", "Quadrant"]).size().unstack(fill_value=0)
sheets["Ch6_T8_区域阶段象限"] = quad_summary.reset_index()

# ----- Methodology -----
print("Building methodology sheets...")
sheets["M1_熵权计算结果"] = entropy_calc
sheets["M2_熵权原始面板"] = tech_panel

# ============================================================
# Write to Excel
# ============================================================
print(f"\nWriting to {OUT}...")
OUT.parent.mkdir(exist_ok=True)
with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    for name, df in sheets.items():
        # Excel sheet names limited to 31 chars
        safe = name[:31]
        df.to_excel(writer, sheet_name=safe, index=False)
        print(f"  ✓ {safe} ({len(df)} rows)")
print(f"\nDONE. Total sheets: {len(sheets)}")
print(f"Output: {OUT}")
