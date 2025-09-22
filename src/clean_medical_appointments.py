# clean_medical_appointments.py
# Place this in the same folder as medical_appointments.csv
# Run: python clean_medical_appointments.py

import pandas as pd
import numpy as np
from pathlib import Path

# --- Step 1: Paths ---
input_path = Path(r"C:\C\JSSATEB\ElevateLabs Internship\Task 1\September 2025\data\raw\medical_appointments.csv").parent / "medical_appointments.csv"
output_path = Path(r"C:\C\JSSATEB\ElevateLabs Internship\Task 1\September 2025\data\cleaned\medical_appointments_cleaned.csv").parent / "medical_appointments_cleaned.csv"

# --- Step 2: Load dataset ---
df = pd.read_csv(input_path)

# --- Step 3: Clean data ---

# (a) Remove duplicate rows
df = df.drop_duplicates()

# (b) Standardize column names
df.columns = (df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
                .str.replace("-", "_"))

# (c) Handle date columns
if "scheduledday" in df.columns:
    df["scheduledday"] = pd.to_datetime(df["scheduledday"], errors="coerce")
if "appointmentday" in df.columns:
    df["appointmentday"] = pd.to_datetime(df["appointmentday"], errors="coerce")

# Create wait_days and drop invalid ones
if "scheduledday" in df.columns and "appointmentday" in df.columns:
    df["wait_days"] = (df["appointmentday"] - df["scheduledday"]).dt.days
    df = df[df["wait_days"] >= 0]  # remove negative wait times

# (d) Age cleaning (remove unrealistic ages)
if "age" in df.columns:
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df.loc[df["age"] < 0, "age"] = np.nan
    df.loc[df["age"] > 120, "age"] = np.nan

# (e) Gender standardization
if "gender" in df.columns:
    df["gender"] = df["gender"].astype(str).str.upper().str.strip()
    df.loc[~df["gender"].isin(["M", "F"]), "gender"] = np.nan

# (f) No-show standardization
if "no_show" in df.columns:
    df["no_show"] = df["no_show"].astype(str).str.strip().str.lower()
    df["no_show"] = df["no_show"].replace({
        "no": 0, "yes": 1,
        "n": 0, "y": 1,
        "0": 0, "1": 1,
        "false": 0, "true": 1
    }).astype("Int64")

# (g) Convert other binary-like columns (0/1 stored as strings) to integers
for col in df.columns:
    unique_vals = df[col].dropna().unique()
    if set(map(str, unique_vals)).issubset({"0", "1"}):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

# (h) Handle missing values
for col in df.columns:
    if df[col].isnull().any():
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())  # numeric → median
        else:
            df[col] = df[col].fillna(df[col].mode()[0])  # categorical → mode

# --- Step 4: Save cleaned file ---
df.to_csv(output_path, index=False)
print(f"✅ Cleaned file saved as {output_path}")
