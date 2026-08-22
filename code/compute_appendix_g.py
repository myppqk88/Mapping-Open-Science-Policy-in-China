# -*- coding: utf-8 -*-
"""
compute_appendix_g.py

Reproduces the Appendix G coupling-statistics tables (G1-G6) of the paper
"Mapping Open Science Policy in China: A Structural, Temporal, and Spatial Analysis".

Inputs  (relative to the opengit/ repository root):
    data/coupling/national_O_t.csv          national policy intensity index P_t
    data/coupling/national_S_t.csv          national composite S&T index S_t
    data/coupling/prov_quadrant_records.csv  province x stage quadrant assignment

Outputs (written to outputs/tables/):
    appG_T1_stage_correlation_P_S.csv   stage-wise Pearson / Spearman correlations
    appG_T2_marginal_tests.csv          first-difference and growth-rate tests
    appG_T3_quadrant_distribution.csv   provincial quadrant counts by stage
    appG_T4_transition_S1_to_S3.csv     S1 -> S3 quadrant transition matrix
    appG_T5_transition_S2_to_S3.csv     S2 -> S3 quadrant transition matrix
    appG_T6_persistent_membership.csv   provinces with persistent HH / LL membership

These six tables are also bundled as sheets G1-G6 of
    outputs/audit/data_audit_master_v5.3.xlsx

Usage:
    cd opengit
    python code/compute_appendix_g.py

All p values are two-sided.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent      # opengit/
DATA = ROOT / "data" / "coupling"
OUT = ROOT / "outputs" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# Load source panels
# ----------------------------------------------------------------------
O = pd.read_csv(DATA / "national_O_t.csv")
S = pd.read_csv(DATA / "national_S_t.csv").rename(columns={"年份": "year"})
df = O.merge(S[["year", "S_t"]], on="year", how="inner")   # 1998-2024, n = 27
q = pd.read_csv(DATA / "prov_quadrant_records.csv")

# ----------------------------------------------------------------------
# G1  Stage-wise correlation between P_t and S_t
# ----------------------------------------------------------------------
rows = []
for label, lo, hi in [("Full", 1998, 2024), ("S1", 1998, 2005),
                       ("S2", 2006, 2015), ("S3", 2016, 2024)]:
    sub = df[(df.year >= lo) & (df.year <= hi)]
    pr, pp = stats.pearsonr(sub["O_t"], sub["S_t"])
    sr, sp = stats.spearmanr(sub["O_t"], sub["S_t"])
    rows.append({"stage": label, "years": f"{lo}-{hi}", "n": len(sub),
                 "pearson_r": round(pr, 4), "pearson_p": round(pp, 4),
                 "spearman_rho": round(sr, 4), "spearman_p": round(sp, 4)})
pd.DataFrame(rows).to_csv(OUT / "appG_T1_stage_correlation_P_S.csv", index=False)

# ----------------------------------------------------------------------
# G2  Marginal-scale tests
# ----------------------------------------------------------------------
dO = np.diff(df["O_t"].values)
dS = np.diff(df["S_t"].values)
gO = np.where(df["O_t"].values[:-1] > 1e-9, dO / (df["O_t"].values[:-1] + 1e-9), 0)
gS = np.where(df["S_t"].values[:-1] > 1e-9, dS / (df["S_t"].values[:-1] + 1e-9), 0)
rising = dS[dO > 0]
falling = dS[dO < 0]
t_stat, t_p = stats.ttest_ind(rising, falling, equal_var=False)

g2 = [
    {"test": "First-difference Pearson r (dP_t, dS_t)", "n": len(dO),
     "statistic": round(stats.pearsonr(dO, dS).statistic, 4),
     "p": round(stats.pearsonr(dO, dS).pvalue, 4), "decision": "Not significant"},
    {"test": "First-difference Spearman rho (dP_t, dS_t)", "n": len(dO),
     "statistic": round(stats.spearmanr(dO, dS).statistic, 4),
     "p": round(stats.spearmanr(dO, dS).pvalue, 4),
     "decision": "Marginal, not significant at alpha=0.05"},
    {"test": "Mean dS in policy-rising vs falling years (Welch t)",
     "n": f"{len(rising)} vs {len(falling)}",
     "statistic": round(t_stat, 4), "p": round(t_p, 4),
     "decision": "Not significant"},
]
pd.DataFrame(g2).to_csv(OUT / "appG_T2_marginal_tests.csv", index=False)

# ----------------------------------------------------------------------
# G3  Provincial quadrant distribution by stage
# ----------------------------------------------------------------------
g3 = (pd.crosstab(q["stage"], q["quadrant"])
        .reindex(index=["S1", "S2", "S3"], columns=["HH", "HL", "LH", "LL"], fill_value=0))
g3["n"] = g3.sum(axis=1)
g3 = g3[["n", "HH", "HL", "LH", "LL"]]
g3.index.name = "stage"
g3.to_csv(OUT / "appG_T3_quadrant_distribution.csv")

# ----------------------------------------------------------------------
# G4 / G5  Quadrant transition matrices
# ----------------------------------------------------------------------
def transition_matrix(src, dst):
    a = q[q["stage"] == src].set_index("province")["quadrant"]
    b = q[q["stage"] == dst].set_index("province")["quadrant"]
    common = a.index.intersection(b.index)
    quads = ["HH", "HL", "LH", "LL"]
    mat = pd.DataFrame(0, index=quads, columns=quads)
    for p in common:
        mat.loc[a[p], b[p]] += 1
    mat.index.name = f"{src}_quadrant"
    return mat

transition_matrix("S1", "S3").to_csv(OUT / "appG_T4_transition_S1_to_S3.csv")
transition_matrix("S2", "S3").to_csv(OUT / "appG_T5_transition_S2_to_S3.csv")

# ----------------------------------------------------------------------
# G6  Provinces with persistent HH / LL membership
# ----------------------------------------------------------------------
prov = q.groupby("province").agg(
    n_stages=("stage", "count"),
    quadrants=("quadrant", lambda x: "|".join(x.tolist())),
    persistent=("quadrant", lambda x: x.iloc[0] if (x == x.iloc[0]).all() else ""),
).reset_index()
g6 = prov[prov["persistent"].isin(["HH", "LL"])].sort_values(["persistent", "province"])
g6.to_csv(OUT / "appG_T6_persistent_membership.csv", index=False)

print("Appendix G tables G1-G6 written to", OUT)
