# ============================================================
# Edinburgh Daylight Data Cleaning Pipeline
# ============================================================

import pandas as pd
import numpy as np
import datetime as dt
import re


# ============================================================
# 1. CONFIGURATION
# ============================================================

EXCEPTIONS = ["", " ", "-", "--", "NaN", "NULL", "None"]
TIME_PATTERN = r"\b\d{1,2}:\d{2}(?::\d{2})?\b"


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def parse_time(value: str):
    """
    Safely extract and parse 'HH:MM' or 'HH:MM:SS' from a messy Excel string.
    Returns datetime.time or NaN.
    """
    if not isinstance(value, str):
        return np.nan

    match = re.search(TIME_PATTERN, value)
    if not match:
        return np.nan

    time_str = match.group(0)

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return dt.datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue

    return np.nan


def clean_column_names(df):
    """Flatten MultiIndex headers into single string names."""
    df.columns = [f"{top} {sub}".strip() for top, sub in df.columns]
    return df


def remove_symbols(df):
    """Remove arrows, degree signs, and brackets."""
    return df.replace(r"[↑↓()°]", "", regex=True)


# ============================================================
# 3. LOAD DATA
# ============================================================

df = pd.read_excel("data/Edinburgh-daytime.xlsx", header=[0, 1])
df = clean_column_names(df)


# ============================================================
# 4. CLEAN RAW DATA
# ============================================================

# Remove symbolic characters
df = remove_symbols(df)

# Convert solar distance to numeric
if "Solar Noon Mil. km" in df.columns:
    df["Solar Noon Mil. km"] = pd.to_numeric(df["Solar Noon Mil. km"], errors="coerce")

# Standardize blank or bad values
df = df.replace(EXCEPTIONS, np.nan)

# Drop rows
