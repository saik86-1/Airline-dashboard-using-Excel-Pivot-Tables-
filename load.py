from pathlib import Path
import pandas as pd
import re

# ---- point to your CSV (rename if needed) ----
src = Path("2024_airlinedata.csv")

# ---- load ----
df = pd.read_csv(src, low_memory=False)
df.columns = [c.strip() for c in df.columns]

# normalize a few header variants
rename_map = {}
if "CARRIER_NAME" not in df.columns and "UNIQUE_CARRIER_NAME" in df.columns:
    rename_map["UNIQUE_CARRIER_NAME"] = "CARRIER_NAME"
if "ORIGIN_COUNTRY_NAME" not in df.columns and "ORIGIN_COUNTRY" in df.columns:
    rename_map["ORIGIN_COUNTRY"] = "ORIGIN_COUNTRY_NAME"
if "DEST_COUNTRY_NAME" not in df.columns and "DEST_COUNTRY" in df.columns:
    rename_map["DEST_COUNTRY"] = "DEST_COUNTRY_NAME"
df = df.rename(columns=rename_map)

# coerce types we rely on
df["PASSENGERS"] = pd.to_numeric(df.get("PASSENGERS"), errors="coerce")
df["MONTH"] = pd.to_numeric(df.get("MONTH"), errors="coerce").astype("Int64")

# derive YEAR from filename (fallback 2024)
m = re.search(r"(\d{4})", src.stem)
year = int(m.group(1)) if m else 2024
df["YEAR"] = year

# DomInt (US perspective); if countries missing, mark Unknown
if {"ORIGIN_COUNTRY_NAME", "DEST_COUNTRY_NAME"}.issubset(df.columns):
    df["DomInt"] = (
        (df["ORIGIN_COUNTRY_NAME"] == "United States") &
        (df["DEST_COUNTRY_NAME"] == "United States")
    ).map({True: "Domestic", False: "International"})
else:
    df["DomInt"] = "Unknown"

# ---- keep only the requested columns ----
keep_cols_all = [
    "YEAR","MONTH","DomInt","CARRIER_NAME","PASSENGERS",
    "ORIGIN_STATE_NM","ORIGIN_COUNTRY_NAME",
    "DEST_STATE_NM","DEST_COUNTRY_NAME"
]
keep_cols = [c for c in keep_cols_all if c in df.columns]
missing = [c for c in keep_cols_all if c not in df.columns]
if missing:
    print("Note: missing columns (skipped):", missing)

df = df[keep_cols].copy()

# basic sanity (optional): month range and positive passengers
df = df[df["MONTH"].between(1, 12)]
df = df[df["PASSENGERS"] > 0]

# ---- drop any row with NA in THESE columns ----
before = len(df)
df = df.dropna(how="any", subset=keep_cols)
dropped = before - len(df)
print(f"Dropped rows with NA in keep columns: {dropped} (kept {len(df)})")

# ---- save to Excel (.xlsx) ----
out = Path("2024_cleaned_airline.xlsx")
df.to_excel(out, index=False, sheet_name="clean")
print(f"Saved → {out}")
print("Columns saved:", list(df.columns))
print("Preview:\n", df.head(8).to_string(index=False))
