#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import re
from datetime import datetime


# In[12]:


def parse_sheet_year_month(sheet_name):
    """Convert sheet name 'YYMM' → (year, month)."""
    yy = int(sheet_name[:2])
    mm = int(sheet_name[2:])
    year = 2000 + yy if yy < 50 else 1900 + yy
    return year, mm


# In[20]:


def clean_time_string(value):
    """Extract the first HH:MM or HH:MM:SS from the string. Remove everything else."""
    if not isinstance(value, str):
        return value

    # Regex for HH:MM or HH:MM:SS
    match = re.search(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", value)
    if match:
        return match.group(0)

    return ""   # For cells that aren't times


# In[21]:


def load_single_sheet(path, sheet_name):
    """Load one sheet cleanly."""
    year, month = parse_sheet_year_month(sheet_name)

    # Use 2nd row as header
    df = pd.read_excel(path, sheet_name=sheet_name, header=1)

    # Remove empty/unnamed columns
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]

    # First column = day
    day_col = df.columns[0]
    df[day_col] = pd.to_numeric(df[day_col], errors="coerce")

    # Drop blank rows
    df = df.dropna(subset=[day_col])

    # Create proper Date
    df["Date"] = pd.to_datetime({
        "year": year,
        "month": month,
        "day": df[day_col].astype(int)
    })

    # Remove the original day column
    df = df.drop(columns=[day_col])

    # Clean all string values in data rows
    df = df.map(clean_time_string)

    # Reorder: Date first
    df = df[["Date"] + [c for c in df.columns if c != "Date"]]

    return df


# In[22]:


def load_all_sheets(path):
    xls = pd.ExcelFile(path)
    frames = []

    for sheet_name in xls.sheet_names:
        # Only process sheets like "1201", "1112", etc.
        if re.fullmatch(r"\d{4}", sheet_name):
            frames.append(load_single_sheet(path, sheet_name))

    return pd.concat(frames, ignore_index=True)


# In[23]:


df = load_all_sheets("data/Edinburgh-daytime.xlsx")

output_path = "data/edinburgh-daytime-cleaned.csv"
df.to_csv(output_path, index=False)

