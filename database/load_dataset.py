"""
load_dataset.py
===============
Loads data/dataset_calls.csv into PostgreSQL using COPY (bulk load).

Steps:
  1. (optional, --schema) run database/schema.sql to (re)create the structure
  2. TRUNCATE the four tables
  3. COPY customers, calls, follow_ups
  4. Run the trained model over every call and COPY the predictions
  5. Reset the id sequences

Usage (from the project root):
    python -m database.load_dataset --schema
    python -m database.load_dataset            # structure already exists
"""
import argparse
import io
import os

import pandas as pd

from backend.database.connection import engine
from backend.services.ml_service import run_predictions

ROOT        = os.path.join(os.path.dirname(__file__), "..")
CSV_PATH    = os.path.join(ROOT, "data", "dataset_calls.csv")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def copy_df(cur, df: pd.DataFrame, table: str, columns: list[str]) -> None:
    """Bulk-load a DataFrame with COPY ... FROM STDIN (CSV)."""
    buf = io.StringIO()
    df[columns].to_csv(buf, index=False, header=False, na_rep="")
    buf.seek(0)
    cols = ", ".join(columns)
    cur.copy_expert(f"COPY {table} ({cols}) FROM STDIN WITH (FORMAT csv, NULL '')", buf)
    print(f"  {table:<12} {len(df):>7,} rows")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", action="store_true", help="run schema.sql first")
    args = parser.parse_args()

    # keep_default_na=False: values like "None"/"NA" must not become NaN
    df = pd.read_csv(CSV_PATH, keep_default_na=False, na_values=[""])
    print(f"Dataset: {len(df):,} calls")

    raw = engine.raw_connection()
    try:
        cur = raw.cursor()

        if args.schema:
            with open(SCHEMA_PATH, encoding="utf-8") as f:
                cur.execute(f.read())
            print("Schema applied")

        cur.execute("TRUNCATE predictions, follow_ups, calls, customers RESTART IDENTITY CASCADE")

        # Customers: first occurrence of each customer_id
        customers = (
            df.drop_duplicates("customer_id")
              .rename(columns={
                  "customer_id": "id",
                  "customer_status": "status",
                  "customer_registered_at": "registered_at",
              })
        )
        copy_df(cur, customers, "customers",
                ["id", "name", "phone", "email", "company", "age", "registered_at", "status"])

        # Calls
        calls = df.rename(columns={"call_id": "id"})
        calls["id"] = calls["id"].astype(int)
        copy_df(cur, calls, "calls",
                ["id", "customer_id", "called_at", "duration_seconds", "outcome", "interest",
                 "requested_info", "accepted_followup", "notes"])
        # boolean columns were written as 0/1 -> PostgreSQL accepts them in COPY csv for boolean

        # Follow-ups
        fu = df[df["has_followup"] == 1].rename(columns={
            "call_id": "call_id",
            "followup_date": "scheduled_date",
            "followup_reason": "reason",
            "followup_status": "status",
        })
        copy_df(cur, fu, "follow_ups",
                ["customer_id", "call_id", "scheduled_date", "reason", "status"])

        # Predictions: real model output for every call
        status_by_customer = customers.set_index("id")["status"].to_dict()
        age_by_customer    = customers.set_index("id")["age"].to_dict()
        inputs = pd.DataFrame({
            "duration_seconds":  df["duration_seconds"],
            "requested_info":    df["requested_info"],
            "accepted_followup": df["accepted_followup"],
            "age":               df["customer_id"].map(age_by_customer),
            "has_followup":      df["has_followup"],
            "outcome":           df["outcome"],
            "interest":          df["interest"],
            "customer_status":   df["customer_id"].map(status_by_customer),
        }).to_dict("records")
        results = run_predictions(inputs)          # one batch, not 10,000 calls
        predictions = pd.DataFrame(results)
        predictions["customer_id"]  = df["customer_id"].values
        predictions["call_id"]      = df["call_id"].values
        predictions["predicted_at"] = df["called_at"].values
        copy_df(cur, predictions, "predictions",
                ["customer_id", "call_id", "probability", "classification",
                 "recommendation", "predicted_at"])

        # Sequences: ids were inserted explicitly for customers and calls
        for table in ("customers", "calls"):
            cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                        f"(SELECT MAX(id) FROM {table}))")

        raw.commit()
        print("Done.")
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


if __name__ == "__main__":
    main()
