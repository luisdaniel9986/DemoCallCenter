"""
generate_dataset.py
===================
Generates a synthetic but logically coherent call-center dataset.
Correlations are realistic:
  High interest + accepts follow-up + requests info → higher purchase probability

Configuration:
    NUM_RECORDS = 10_000   ← change here to generate more/less data

Outputs:
    ../data/dataset_calls.csv
    ../data/dataset_calls.xlsx
"""

import os
import random
import unicodedata
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
NUM_RECORDS = 10_000
SEED        = 42
# ─────────────────────────────────────────────

random.seed(SEED)
np.random.seed(SEED)

# ── Catalogs ─────────────────────────────────
NAMES = [
    "María García", "Carlos López", "Ana Martínez", "Luis Rodríguez",
    "Laura Hernández", "Jorge Pérez", "Sofía González", "Miguel Torres",
    "Valentina Díaz", "Andrés Flores", "Daniela Reyes", "Santiago Morales",
    "Isabella Jiménez", "Mateo Ruiz", "Camila Vargas", "Sebastián Castro",
    "Lucía Ramírez", "Nicolás Álvarez", "Mariana Romero", "Diego Soto",
]

COMPANIES = [
    "TechCorp SA", "Innova SRL", "GlobalTech", "DataSystems",
    "FutureBiz", "MegaVentas", "ProSoluciones", "AlphaGroup",
    "BetaServices", "NexusComercial", "Apex Consulting", "BlueStar",
    "RedGroup SA", "GreenSoft", "PrimeLogistics", "MaxTrade",
    "SunCorp", "MoonTech", "StarBusiness", "PlanetSolutions",
]

OUTCOMES        = ["Interested", "Not interested", "No answer", "Busy", "Wrong number"]
INTEREST_LEVELS = ["High", "Medium", "Low", "No interest"]
CUSTOMER_STATUSES = ["New", "Active", "Inactive", "VIP"]
FOLLOWUP_REASONS = [
    "Commercial follow-up",
    "Proposal delivery",
    "Technical inquiry",
    "Deal closing",
    "Satisfaction check",
]

START_DATE = datetime(2025, 1, 1)
END_DATE   = datetime(2026, 11, 10)
TODAY      = END_DATE.date()   # reference "today" for follow-up statuses


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


# ── Build records ─────────────────────────────
records = []

for i in range(1, NUM_RECORDS + 1):
    # Customer
    customer_id    = random.randint(1, NUM_RECORDS // 5)
    name           = random.choice(NAMES)
    phone          = f"9{random.randint(10_000_000, 99_999_999)}"
    first_name     = unicodedata.normalize("NFKD", name.split()[0].lower()).encode("ascii", "ignore").decode()
    email          = f"{first_name}{customer_id}@email.com"
    company        = random.choice(COMPANIES)
    age            = random.randint(22, 65)
    customer_status = random.choices(CUSTOMER_STATUSES, weights=[30, 45, 15, 10], k=1)[0]
    registered_at  = random_date(START_DATE, END_DATE)

    # Call
    called_at    = random_date(START_DATE, END_DATE)
    duration_sec = random.randint(10, 900)
    outcome      = random.choices(OUTCOMES, weights=[35, 25, 20, 15, 5], k=1)[0]

    # Interest correlates with outcome
    if outcome == "Interested":
        interest = random.choices(INTEREST_LEVELS, weights=[50, 35, 10, 5],  k=1)[0]
    elif outcome == "Not interested":
        interest = random.choices(INTEREST_LEVELS, weights=[2,  8,  30, 60], k=1)[0]
    else:
        interest = random.choices(INTEREST_LEVELS, weights=[5,  15, 40, 40], k=1)[0]

    interest_weight    = {"High": 0.80, "Medium": 0.50, "Low": 0.20, "No interest": 0.05}[interest]
    requested_info     = int(random.random() < interest_weight)
    accepted_followup  = int(random.random() < interest_weight * 0.9)

    notes_options = [
        "Very receptive customer",
        "Asked for more time to decide",
        "Not the decision maker",
        "Comparing with competitors",
        "Ready to buy",
        "No interest at this time",
        "Limited budget",
        "Very interested in the product",
        "",
    ]
    notes = random.choice(notes_options)

    # Follow-up
    has_followup     = accepted_followup or (outcome == "Interested" and random.random() < 0.4)
    followup_date    = called_at + timedelta(days=random.randint(1, 14)) if has_followup else None
    followup_reason  = random.choice(FOLLOWUP_REASONS) if has_followup else None
    # Follow-ups already in the past are resolved; only upcoming ones stay pending.
    if not has_followup:
        followup_status = None
    elif followup_date.date() < TODAY:
        followup_status = random.choices(["Completed", "Cancelled"], weights=[80, 20], k=1)[0]
    else:
        followup_status = "Pending"

    # Target variable: purchase
    score  = 0
    score += {"High": 40, "Medium": 20, "Low": 5, "No interest": 0}[interest]
    score += 20 * requested_info
    score += 20 * accepted_followup
    score += 10 if duration_sec > 180 else 0
    score += 10 if customer_status in ("VIP", "Activo") else 0
    score += random.gauss(0, 8)

    purchase_probability = max(0.0, min(1.0, score / 100))
    purchased            = int(random.random() < purchase_probability)

    records.append({
        "call_id":                i,
        "customer_id":            customer_id,
        "name":                   name,
        "phone":                  phone,
        "email":                  email,
        "company":                company,
        "age":                    age,
        "customer_status":         customer_status,
        "customer_registered_at": registered_at.strftime("%Y-%m-%d"),
        "called_at":              called_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds":       duration_sec,
        "outcome":                outcome,
        "interest":               interest,
        "requested_info":         requested_info,
        "accepted_followup":      accepted_followup,
        "notes":                  notes,
        "has_followup":           int(bool(has_followup)),
        "followup_date":          followup_date.strftime("%Y-%m-%d") if followup_date else None,
        "followup_reason":        followup_reason,
        "followup_status":        followup_status,
        "estimated_probability":  round(purchase_probability, 4),
        "purchased":              purchased,
    })

# ── Save files ────────────────────────────────
df      = pd.DataFrame(records)
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

csv_path  = os.path.join(OUT_DIR, "dataset_calls.csv")
xlsx_path = os.path.join(OUT_DIR, "dataset_calls.xlsx")

df.to_csv(csv_path,  index=False, encoding="utf-8-sig")
df.to_excel(xlsx_path, index=False)

# ── Summary ───────────────────────────────────
print(f"\n{'='*52}")
print(f"  Dataset generated successfully")
print(f"{'='*52}")
print(f"  Records          : {len(df):,}")
print(f"  Unique customers : {df['customer_id'].nunique():,}")
print(f"  CSV              : {os.path.abspath(csv_path)}")
print(f"  XLSX             : {os.path.abspath(xlsx_path)}")
print(f"\n  'purchased' distribution:")
print(df["purchased"].value_counts().rename({0: "No (0)", 1: "Yes (1)"}).to_string(header=False))
print(f"\n  'interest' distribution:")
print(df["interest"].value_counts().to_string())
print(f"\n  Average call duration: {df['duration_seconds'].mean():.0f} sec")
print(f"{'='*52}\n")

