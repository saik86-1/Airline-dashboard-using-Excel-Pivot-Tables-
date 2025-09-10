# play_manipulate.py
from pathlib import Path
import pandas as pd

# ---------- CONFIG ----------
DATA_PATH = Path("2024_cleaned_airline.xlsx")   # or "data/t100_2024.csv"
EXCEL_SHEET = "clean"                           # ignored if CSV
# ----------------------------

# Pretty printing in terminal
pd.set_option("display.width", 140)
pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", None)

def load_any(path: Path, sheet: str | None = None) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    suf = path.suffix.lower()
    if suf in [".xlsx", ".xlsm", ".xls"]:
        return pd.read_excel(path, sheet_name=sheet)
    return pd.read_csv(path, low_memory=False)

df = load_any(DATA_PATH, EXCEL_SHEET).copy()


print(df["CARRIER_NAME"].nunique)

# --- Ensure numeric for common fields (safe casts) ---
for col in ["PASSENGERS", "MONTH", "YEAR"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
