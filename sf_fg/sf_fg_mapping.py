import pandas as pd
import dataiku

# ============================================
# READ INPUT DATASETS
# ============================================

sf = dataiku.Dataset(
    "Position_Download_report"
).get_dataframe()

fg = dataiku.Dataset(
    "FG_JR_Prepared"
).get_dataframe()

# ============================================
# CLEAN POSITION IDS
# ============================================

sf["Position_ID"] = (
    sf["Position Code"]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.strip()
)

fg["Position_ID"] = (
    fg["Position ID"]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.strip()
)

# ============================================
# REMOVE BLANK POSITION IDS
# ============================================

sf = sf[
    sf["Position_ID"].notna() &
    (sf["Position_ID"] != "") &
    (sf["Position_ID"].str.lower() != "nan")
]

fg = fg[
    fg["Position_ID"].notna() &
    (fg["Position_ID"] != "") &
    (fg["Position_ID"].str.lower() != "nan")
]

# ============================================
# DISTINCT POSITION IDS
# ============================================

sf = sf.drop_duplicates(
    subset=["Position_ID"]
)

fg = fg.drop_duplicates(
    subset=["Position_ID"]
)

# ============================================
# FG LOGIC
# ============================================

fg["Reason for Hire from FG"] = fg[
    "Is this request being created to replace an existing NEW?"
].map({
    True: "Replacement",
    False: "New Hire"
})

# ============================================
# SF LOGIC
# ============================================

def normalize_sf(x):

    if pd.isna(x):
        return "New Hire"

    x = str(x).lower().strip()

    if "replacement" in x:
        return "Replacement"

    return "New Hire"

sf["Reason for Hire From SF"] = sf[
    "Reason for Hire"
].apply(normalize_sf)

# ============================================
# MERGE
# ============================================

merged = pd.merge(
    sf,
    fg,
    on="Position_ID",
    how="outer"
)

# ============================================
# FINAL LOGIC
# ============================================

def final_reason(row):

    fg_reason = row.get(
        "Reason for Hire from FG"
    )

    if pd.notna(fg_reason):

        if fg_reason == "Replacement":
            return "Replacement"

        return "New Hire"

    sf_reason = row.get(
        "Reason for Hire From SF"
    )

    if sf_reason == "Replacement":
        return "Replacement"

    return "New Hire"

merged["Final Reason for Hire"] = merged.apply(
    final_reason,
    axis=1
)

# ============================================
# FINAL OUTPUT
# ============================================

merged["Position Code"] = merged[
    "Position_ID"
]

final_df = merged[[
    "Position Code",
    "Reason for Hire From SF",
    "Reason for Hire from FG",
    "Final Reason for Hire"
]]

final_df = final_df.drop_duplicates(
    subset=["Position Code"]
)

final_df["Position Code"] = (
    pd.to_numeric(
        final_df["Position Code"],
        errors="coerce"
    )
    .astype("Int64")
    .astype(str)
)

# ============================================
# CREATE EXCEL FILE
# ============================================

output_path = "/tmp/SF_FG.xlsx"

with pd.ExcelWriter(
    output_path,
    engine="openpyxl"
) as writer:

    final_df.to_excel(
        writer,
        sheet_name="SF_FG_Mapping",
        index=False
    )

# ============================================
# WRITE TO SHAREPOINT FOLDER
# ============================================

folder = dataiku.Folder(
    "SF_FG_Mapping"
)

with folder.get_writer(
    "SF_FG.xlsx"
) as writer:

    with open(output_path, "rb") as f:

        writer.write(f.read())

print("SF_FG.xlsx uploaded successfully")
