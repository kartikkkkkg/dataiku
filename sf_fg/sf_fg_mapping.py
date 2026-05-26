import pandas as pd
import dataiku
from io import BytesIO

# ============================================
# READ DATASETS
# ============================================

sf = dataiku.Dataset("Position_Download_report").get_dataframe()

fg = dataiku.Dataset("FG_JR_Prepared").get_dataframe()

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
# REMOVE BLANK IDS
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
# KEEP ONLY REQUIRED COLUMNS
# ============================================

sf = sf[[
    "Position_ID",
    "Reason for Hire From SF"
]]

fg = fg[[
    "Position_ID",
    "Reason for Hire from FG"
]]

# ============================================
# REMOVE DUPLICATES BEFORE MERGE
# ============================================

sf = sf.drop_duplicates(subset=["Position_ID"])

fg = fg.drop_duplicates(subset=["Position_ID"])

# ============================================
# FULL OUTER JOIN
# ============================================

merged = pd.merge(
    sf,
    fg,
    on="Position_ID",
    how="outer"
)

# ============================================
# FINAL LOGIC
# FG PRIORITY
# ============================================

def final_reason(row):

    fg_reason = row.get("Reason for Hire from FG")

    if pd.notna(fg_reason):

        if fg_reason == "Replacement":
            return "Replacement"

        return "New Hire"

    sf_reason = row.get("Reason for Hire From SF")

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

merged["Position Code"] = merged["Position_ID"]

final_df = merged[[
    "Position Code",
    "Reason for Hire From SF",
    "Reason for Hire from FG",
    "Final Reason for Hire"
]]

# ============================================
# FINAL DISTINCT
# ============================================

final_df = final_df.sort_values(
    by="Final Reason for Hire",
    ascending=False
)

final_df = final_df.drop_duplicates(
    subset=["Position Code"]
)

# ============================================
# CREATE EXCEL IN MEMORY
# ============================================

excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    final_df.to_excel(
        writer,
        sheet_name="SF_FG_Mapped",
        index=False
    )

excel_buffer.seek(0)

# ============================================
# SAVE TO SHAREPOINT FOLDER
# ============================================

output_folder = dataiku.Folder("SF_FG_Mapping")

with output_folder.get_writer("SF_FG.xlsx") as writer:

    writer.write(excel_buffer.read())

print("SF_FG.xlsx overwritten successfully in SharePoint")
