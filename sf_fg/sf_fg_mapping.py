import pandas as pd
import dataiku

# ============================================
# READ DATASETS
# ============================================

sf = dataiku.Dataset("SF_Report").get_dataframe()

fg = dataiku.Dataset("FG_Report").get_dataframe()

# ============================================
# CLEAN POSITION IDs
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
# REMOVE BLANK POSITION IDs
# ============================================

sf = sf[
    sf["Position_ID"].notna()
]

sf = sf[
    sf["Position_ID"].str.strip() != ""
]

sf = sf[
    sf["Position_ID"].str.lower() != "nan"
]

fg = fg[
    fg["Position_ID"].notna()
]

fg = fg[
    fg["Position_ID"].str.strip() != ""
]

fg = fg[
    fg["Position_ID"].str.lower() != "nan"
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
# KEEP DISTINCT POSITION IDs
# ============================================

sf = sf.drop_duplicates(
    subset=["Position_ID"],
    keep="first"
)

fg = fg.drop_duplicates(
    subset=["Position_ID"],
    keep="first"
)

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
# FG HAS PRIORITY
# ============================================

def final_reason(row):

    fg_reason = row.get("Reason for Hire from FG")

    # FG priority
    if pd.notna(fg_reason):

        if fg_reason == "Replacement":
            return "Replacement"

        return "New Hire"

    # Else use SF
    if row.get("Reason for Hire From SF") == "Replacement":
        return "Replacement"

    return "New Hire"

merged["Final Reason for Hire"] = merged.apply(
    final_reason,
    axis=1
)

# ============================================
# FINAL POSITION CODE
# ============================================

merged["Position Code"] = merged["Position_ID"]

# ============================================
# FINAL DISTINCT CLEANUP
# ============================================

merged = merged.drop_duplicates(
    subset=["Position Code"],
    keep="first"
)

# ============================================
# KEEP ONLY REQUIRED COLUMNS
# ============================================

final_df = merged[[
    "Position Code",
    "Reason for Hire From SF",
    "Reason for Hire from FG",
    "Final Reason for Hire"
]]

# ============================================
# CONVERT POSITION CODE TO INTEGER
# ============================================

final_df["Position Code"] = pd.to_numeric(
    final_df["Position Code"],
    errors="coerce"
).astype("Int64")

# ============================================
# WRITE OUTPUT
# ============================================

output = dataiku.Dataset("SF_FG")

output.write_with_schema(final_df)

print("SF_FG Mapping Created Successfully")
