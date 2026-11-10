"""
explore_data.py
===============
Exploratory analysis of data/dataset_calls.csv before training:
  - structure, missing values, duplicates
  - distributions of the numerical and categorical variables
  - relationship of every candidate variable with the target ('purchased')
  - features selected for the model

Usage:
    python explore_data.py
"""
import os

import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset_calls.csv")
TARGET    = "purchased"

# Same selection used by train_model.py
CATEGORICAL = ["outcome", "interest", "customer_status"]
NUMERICAL   = ["duration_seconds", "requested_info", "accepted_followup", "age", "has_followup"]


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


# keep_default_na=False so that text values are never silently turned into NaN
df = pd.read_csv(DATA_PATH, keep_default_na=False, na_values=[""])

section("1. STRUCTURE")
print(f"Rows: {len(df):,}   Columns: {df.shape[1]}")
print(df.dtypes.to_string())

section("2. MISSING VALUES")
missing = df.isna().sum()
missing = missing[missing > 0]
print(missing.to_string() if len(missing) else "None")
print("\n(followup_* columns are empty when the call has no follow-up; notes may be empty.)")

section("3. DUPLICATES")
print(f"Duplicated call_id: {df['call_id'].duplicated().sum()}")
print(f"Fully duplicated rows: {df.duplicated().sum()}")
print(f"Unique customers: {df['customer_id'].nunique():,}")

section("4. NUMERICAL VARIABLES")
print(df[NUMERICAL].describe().round(2).T.to_string())

section("5. CATEGORICAL VARIABLES")
for col in CATEGORICAL:
    print(f"\n{col}:")
    print(df[col].value_counts(normalize=True).mul(100).round(1).astype(str).add(" %").to_string())

section("6. TARGET")
counts = df[TARGET].value_counts().sort_index()
print(f"0 = No purchase: {counts[0]:,} ({counts[0] / len(df):.1%})")
print(f"1 = Purchase   : {counts[1]:,} ({counts[1] / len(df):.1%})")

section("7. PURCHASE RATE BY CATEGORY")
for col in CATEGORICAL:
    print(f"\n{col}:")
    print(df.groupby(col)[TARGET].mean().mul(100).round(1).sort_values(ascending=False)
            .astype(str).add(" %").to_string())

section("8. CORRELATION OF NUMERICAL VARIABLES WITH THE TARGET")
print(df[NUMERICAL + [TARGET]].corr()[TARGET].drop(TARGET).sort_values(ascending=False).round(3).to_string())

section("9. FEATURES SELECTED FOR THE MODEL")
print(f"X (predictors) : {NUMERICAL + CATEGORICAL}")
print(f"y (target)     : {TARGET}")
print("Excluded: identifiers, contact data (name, phone, email), dates, notes and")
print("'estimated_probability' (it is derived from the target logic -> data leakage).")
