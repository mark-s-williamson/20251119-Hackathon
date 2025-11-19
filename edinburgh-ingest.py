#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import re
import datetime


# ============================================================
# 1. COLUMN SCHEMA
# ============================================================

FINAL_COLUMNS = [
    "date", "sunrise", "sunset", "daylength", "daylength_difference",
    "at_start", "at_end", "nt_start", "nt_end", "ct_start", "ct_end",
    "sn_time", "sn_mil_km"
]

TIME_COLS = [
    "sunrise", "sunset",
    "at_start", "at_end",
    "nt_start", "nt_end",
    "ct_start", "ct_end",
    "sn_time"
]

DURATION_COLS = ["daylength", "daylength_difference"]
FLOAT_COLS = ["sn_mil_km"]


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def parse_sheet_year_month(sheet_name):
    """Convert sheet name 'YYMM' → (year, month)."""
    yy = int(sheet_name[:2])
    mm = int(sheet_name[2:])
    year = 2000 + yy if yy < 50 else 1900 + yy
    return year, mm


def clean_time_string(value):
    """Extract the first HH:MM or HH:MM:SS from the string."""
    if not isinstance(value, str):
        return value
    m = re.search(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", value)
    return m.group(0) if m else ""


def to_time(val):
    """Force any value into a clean datetime.time object."""
    if isinstance(val, datetime.time):
        return val
    if isinstance(val, datetime.datetime):
        return val.time()
    if isinstance(val, float) and pd.isna(val):
        return None
    if isinstance(val, str) and val.strip() == "":
        return None
    try:
        t = pd.to_datetime(val, errors="coerce")
        if pd.isna(t):
            return None
        return t.time()
    except:
        return None


def normalise_signed_duration(val):
    """
    Convert values like '+1:25' or '-0:42' into 'HH:MM:SS'
    before timedelta conversion.
    """
    if isinstance(val, str):
        val = val.strip()
        if val == "":
            return None

        # Matches +H:MM or -H:MM
        m = re.fullmatch(r"([+-]?\d+):(\d{2})", val)
        if m:
            sign = "+" if m.group(1).startswith("+") else "-"
            hours = m.group(1).lstrip("+-")
            minutes = m.group(2)
            return f"{sign}{hours}:{minutes}:00"

    # Direct datetime.time → timedelta
    if isinstance(val, datetime.time):
        return datetime.timedelta(
            hours=val.hour, minutes=val.minute, seconds=val.second
        )

    # datetime.datetime → time → timedelta
    if isinstance(val, datetime.datetime):
        t = val.time()
        return datetime.timedelta(
            hours=t.hour, minutes=t.minute, seconds=t.second
        )

    # Missing
    if pd.isna(val):
        return None

    return val


def safe_to_timedelta(val):
    """Apply pandas timedelta conversion safely."""
    try:
        return pd.to_timedelta(val, errors="coerce")
    except:
        return pd.NaT


# ============================================================
# 3. LOAD EACH SHEET
# ============================================================

def load_single_sheet(path, sheet_name):
    year, month = parse_sheet_year_month(sheet_name)

    df = pd.read_excel(path, sheet_name=sheet_name, header=1)
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]

    day_col = df.columns[0]
    df[day_col] = pd.to_numeric(df[day_col], errors="coerce")
    df = df.dropna(subset=[day_col])

    df["Date"] = pd.to_datetime({
        "year": year,
        "month": month,
        "day": df[day_col].astype(int)
    })

    df = df.drop(columns=[day_col])
    df = df.map(clean_time_string)
    df = df[["Date"] + [c for c in df.columns if c != "Date"]]

    return df


def load_all_sheets(path):
    xls = pd.ExcelFile(path)
    frames = [
        load_single_sheet(path, name)
        for name in xls.sheet_names
        if re.fullmatch(r"\d{4}", name)
    ]
    return pd.concat(frames, ignore_index=True)


# ============================================================
# 4. MAIN PROCESSING
# ============================================================

df = load_all_sheets("data/Edinburgh-daytime.xlsx")

# Rename columns
df.columns = FINAL_COLUMNS[:len(df.columns)]
df = df[FINAL_COLUMNS]

# Date → datetime64 (date only)
df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
df["date"] = pd.to_datetime(df["date"])

# Time columns → datetime.time
for col in TIME_COLS:
    df[col] = df[col].apply(to_time)

# Duration → normalise + timedelta
for col in DURATION_COLS:
    df[col] = df[col].apply(normalise_signed_duration)
    df[col] = df[col].apply(safe_to_timedelta)

# Float columns
for col in FLOAT_COLS:
    df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)


# ============================================================
# 5. SAVE
# ============================================================

output_path = "data/edinburgh-daytime-cleaned.csv"
df.to_csv(output_path, index=False)

print("Saved:", output_path)
