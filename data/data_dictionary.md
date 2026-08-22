# Data Dictionary

Field-by-field documentation for every dataset in `data/`. Column names match exactly what is in the Excel sheets (Chinese column headers are reproduced verbatim).

---

## 1. `policy_entries_v5_3.xlsx` — clause-level policy entries

Primary unit of analysis. One row per clause-level policy entry; 21,242 entries.

### Sheets

| Sheet | Rows × Cols | Description |
|---|---|---|
| `政策条目` | 21,242 × 18 | The 21,242 entries (main analytical table) |
| `政策文件` | 10,416 × 19 | Document-level metadata, also reproduced in `policy_files_v5_3.xlsx` |
| `数据说明` | 11 × 2 | Version notes |

### Columns of sheet `政策条目`

| # | Column | Type | Description |
|---|---|---|---|
| 1 | `entry_id` | str | Stable entry identifier |
| 2 | `policy_file_id` | str | FK to `政策文件` and `policy_files_v5_3.xlsx` |
| 3 | `governance_level` | str | `中央` / `省级` / `地市级` |
| 4 | `province_raw` | str | Province of issuance (empty for central) |
| 5 | `city_raw` | str | Prefectural-level city (empty for central / provincial) |
| 6 | `issuing_authority` | str | Authority name(s), joined by `；` if multiple |
| 7 | `policy_title` | str | Full title of the source document |
| 8 | `issue_year` | int | Publication year (1998–2026) |
| 9 | `issue_date` | date | Full publication date when available |
| 10 | `provision_text` | str | Clause text after character normalisation |
| 11 | `category_codes` | str | One or more of `OA;OD;OSS;OERs;CS;OPR;OI;ORM;OS_general` joined by `；` |
| 12 | `category_names` | str | Chinese category names corresponding to `category_codes` |
| 13 | `n_categories` | int | Number of distinct categories (1, 2 or 3) |
| 14 | `has_explicit_open_science` | bool | True if clause contains "开放科学" literally |
| 15 | `stage_id` | str | `S1` / `S2` / `S3` (or blank for 2026 partial year) |
| 16 | `stage_name_zh` | str | Chinese stage label |
| 17 | `central_local` | str | `central` / `local` (provincial + prefectural collapsed) |
| 18 | `is_joint_issuance` | bool | True if the source document has multiple issuing authorities |

### Coding conventions

- `category_codes` containing `OS_general` flags the 44 umbrella entries that mention open science without resolving to any specific sub-category; these are tracked separately and **not** counted toward the eight-category breakdown in the paper.
- Multi-category entries (~ 2.4% of the sample) have categories joined by `；`; entry-level counts in the paper apportion the entry to every category it carries (e.g., a `OD；OI` entry counts once toward OD and once toward OI).
- The 16 false-positive entries identified in cleaning are not present in this file; the 14 entries with back-filled `issue_year` are flagged in the audit workbook (`outputs/audit/`).

---

## 2. `policy_files_v5_3.xlsx` — document-level metadata

One row per unique policy document; 10,413 documents.

### Sheets

| Sheet | Description |
|---|---|
| `Sheet1` | 10,413 documents with metadata |
| `联合发文-分类说明` | Eight-class co-issuing classification scheme |
| `联合发文-文件清单` | 1,108 jointly issued documents tagged with classes |
| `联合发文-类型分布` | Class-level frequency table |
| `联合发文-共现矩阵` | 8 × 8 co-occurrence matrix |
| `联合发文-Jaccard矩阵` | 8 × 8 Jaccard similarity matrix |

### Columns of sheet `Sheet1`

| # | Column | Type | Description |
|---|---|---|---|
| 1 | `policy_file_id` | str | Document identifier |
| 2 | `policy_title` | str | Full title |
| 3 | `governance_level` | str | `中央` / `省级` / `地市级` |
| 4 | `province` | str | Province (empty for central) |
| 5 | `city` | str | Prefectural-level city (empty for central / provincial) |
| 6 | `issuing_authority` | str | Authority name(s), joined by `；` |
| 7 | `issue_year` | int | Publication year |
| 8 | `issue_date` | date | Full date |
| 9 | `n_entries` | int | Number of entries this document contributes |
| 10 | `n_categories` | int | Number of distinct categories across the document |
| 11 | `category_codes` | str | Union of category codes for the document |
| 12 | `category_names` | str | Union of Chinese category names |
| 13 | `is_multi_category_file` | bool | True if `n_categories` > 1 |
| 14 | `has_explicit_open_science` | bool | True if any clause contains "开放科学" literally |
| 15 | `stage_id` | str | `S1` / `S2` / `S3` |
| 16 | `stage_name_zh` | str | Chinese stage label |
| 17 | `central_local` | str | `central` / `local` |
| 18 | `is_joint_issuance` | bool | True if document has multiple issuing authorities |
| 19 | `legal_force` | str | Source database status: `现行有效` / `已被修改` / `尚未施行` |

---

## 3. `tech_indicators_panel_1998_2024.xlsx` — provincial S&T panel

Raw indicator panel feeding the composite index.

### Sheets

| Sheet | Rows × Cols | Description |
|---|---|---|
| `分省面板数据` | 837 × 6 | Province-year panel, 31 provinces × 27 years |
| `元数据` | — | Source and unit information |

### Columns of `分省面板数据`

| # | Column | Unit | Description |
|---|---|---|---|
| 1 | `省份` | — | Provincial-level region (31 in total) |
| 2 | `年份` | — | 1998–2024 |
| 3 | `R&D人员全时当量` | person-years | R&D personnel, full-time equivalent |
| 4 | `R&D经费内部支出` | 100 million yuan | Internal R&D expenditure |
| 5 | `专利授权数` | count | Patent grants |
| 6 | `技术市场成交额` | 100 million yuan | Technology-market contract value |

Source: *China Statistics Yearbook on Science and Technology*, multiple editions (compiled by the National Bureau of Statistics of China and the Ministry of Science and Technology). No missing values across the 837 observations.

---

## 4. `tech_composite_index_1998_2024.xlsx` — entropy-weighted composite index

### Sheets

| Sheet | Rows × Cols | Description |
|---|---|---|
| `分省科技综合指数` | 837 × 7 | Province × year raw values + final composite score |
| `熵权计算` | 4 × 5 | Information entropy, divergence, weights per indicator |
| `方法说明` | — | Step-by-step formula description |

### Columns of `分省科技综合指数`

| # | Column | Description |
|---|---|---|
| 1 | `省份` | Province |
| 2 | `年份` | 1998–2024 |
| 3–6 | Four raw indicators | Same as in panel data |
| 7 | `科技综合指数` | Final composite score, min–max-rescaled to [0, 1] |

### Columns of `熵权计算`

| Column | Description |
|---|---|
| `指标` | Indicator name |
| `信息熵` | Information entropy `e_j` |
| `差异系数` | Divergence coefficient `1 - e_j` |
| `熵权` | Normalised weight `w_j` |
| `权重百分比` | `w_j` expressed as % |

### Final weights

| Indicator | Weight |
|---|---|
| 技术市场成交额 (technology-market contract value) | 0.344 |
| 专利授权数 (patent grants) | 0.271 |
| R&D 经费内部支出 (internal R&D expenditure) | 0.222 |
| R&D 人员全时当量 (R&D personnel, FTE) | 0.163 |

### Composite construction (summary)

1. Each raw indicator is min–max-standardised across the 837 observations.
2. Information entropy `e_j = -k Σ p_ij ln(p_ij)`.
3. Weight `w_j = (1 - e_j) / Σ(1 - e_k)`.
4. Composite `S = Σ w_j × x_ij_std`, then min–max-rescaled to [0, 1].

Full formulas are in sheet `方法说明` and Appendix B / §3.3.3 of the paper.

---

## 5. `coupling/national_O_t.csv`

National annual policy intensity series, 1998–2025.

| Column | Description |
|---|---|
| `year` | 1998–2025 |
| `F_t` | Annual document count |
| `E_t` | Annual entry count |
| `logF`, `logE` | `log(1 + count)` transforms |
| `logF_mm`, `logE_mm` | Min–max-standardised log values across the 28-year window |
| `O_star` | Intermediate sum before final normalisation |
| `O_t` | Final policy intensity index used in §4.2.2 (denoted `P_t` in the paper) |

## 6. `coupling/national_S_t.csv`

National annual S&T composite series, 1998–2024 (aggregated across 31 provinces).

| Column | Description |
|---|---|
| `年份` | 1998–2024 |
| Four raw indicators | National totals (sum of 31 provinces) |
| `*_std` (4 columns) | Min–max-standardised across years |
| `S_raw` | Entropy-weighted sum |
| `S_t` | Final composite, min–max-rescaled to [0, 1] |

## 7. `coupling/prov_stage_panel.csv`

Province × stage panel for the spatial coupling analysis (§4.3.2).

| Column | Description |
|---|---|
| `province` | One of 31 provinces |
| `stage` | `S1` / `S2` / `S3` |
| `O_std` | Within-stage min–max-standardised policy intensity |
| `T_std` | Within-stage min–max-standardised S&T composite |

## 8. `coupling/prov_quadrant_records.csv`

Quadrant assignment by province × stage (§4.3.2).

| Column | Description |
|---|---|
| `province` | One of 31 provinces |
| `stage` | `S1` / `S2` / `S3` |
| `O_std`, `T_std` | Same as above |
| `quadrant` | One of `HH` (synergistic-leading), `HL` (policy-driven), `LH` (S&T-leading), `LL` (low-low lagging) |

Median thresholds are computed within each stage across the 31 provinces.

---

## 9. `geo/` — administrative boundary files

| File | Description |
|---|---|
| `china_provinces.geojson` | Province-level polygons, used for Fig. 6a |
| `china_cities.geojson` | Prefectural-level polygons, used for Fig. 6b |

Both are derived from publicly available administrative boundary data; equivalent files can be sourced from the National Catalogue Service for Geographic Information or the OpenStreetMap derivative datasets.

---

## Stage definitions (used throughout the paper)

| Stage | Period | Files | Entries | Avg files / year |
|---|---|---|---|---|
| S1 | 1998–2005 | 143 | 330 | 17.9 |
| S2 | 2006–2015 | 2,516 | 4,982 | 251.6 |
| S3 | 2016–2025 | 7,687 | 15,815 | 768.7 |
| 2026 (partial, excluded) | 2026 | 67 | 115 | — |

Stage boundary justification (Dynp diagnostics + maximum year-on-year jumps + five-year plan milestones, verified by ANOVA) is documented in Appendix B.5 of the paper (file `docs/appendix.docx`) and in the audit workbook sheets `Ch5_T1_年度时序` and `Ch5_T3_断点检测`.

## Open science category codes (used throughout the paper)

| Code | English | Chinese |
|---|---|---|
| OA | Open Access | 开放获取 |
| OD | Open Data | 开放数据 |
| OSS | Open-Source Software | 开源软件 |
| OERs | Open Educational Resources | 开放教育资源 |
| CS | Citizen Science | 公众科学 |
| OPR | Open Peer Review | 开放同行评议 |
| OI | Open Infrastructure | 开放基础设施 |
| ORM | Open Research Methods | 开放研究方法 |
| OS_general | Umbrella reference to "open science" (not counted in 8-category breakdown) | 开放科学（总括） |
