"""
evaluate_model.py
=================
Evaluates the saved model (ml/model.pkl) on the same held-out test split used
by train_model.py (same seed, test size and stratification), so the numbers
are real and reproducible. Metrics are also written to ml/reports/evaluation.json.

Usage:
    python evaluate_model.py
"""
import json
import os

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
)
from sklearn.model_selection import train_test_split

HERE       = os.path.dirname(__file__)
DATA_PATH  = os.path.join(HERE, "..", "data", "dataset_calls.csv")
MODEL_PATH = os.path.join(HERE, "model.pkl")
REPORT_DIR = os.path.join(HERE, "reports")
TEST_SIZE  = 0.20
SEED       = 42          # must match train_model.py
TARGET     = "purchased"

payload  = joblib.load(MODEL_PATH)
model    = payload["model"]
encoders = payload["encoders"]
features = payload["features"]

df = pd.read_csv(DATA_PATH)
for col, encoder in encoders.items():
    df[col + "_enc"] = encoder.transform(df[col].astype(str))

X, y = df[features], df[TARGET]
_, X_test, _, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=SEED, stratify=y)

pred  = model.predict(X_test)
proba = model.predict_proba(X_test)[:, 1]
cm    = confusion_matrix(y_test, pred)

metrics = {
    "model":     payload["model_name"],
    "test_rows": int(len(y_test)),
    "accuracy":  accuracy_score(y_test, pred),
    "precision": precision_score(y_test, pred),
    "recall":    recall_score(y_test, pred),
    "f1":        f1_score(y_test, pred),
    "roc_auc":   roc_auc_score(y_test, proba),
    "confusion_matrix": {"TN": int(cm[0, 0]), "FP": int(cm[0, 1]), "FN": int(cm[1, 0]), "TP": int(cm[1, 1])},
}

print(f"\nModel: {metrics['model']}   (test rows: {metrics['test_rows']:,})\n")
for name in ("accuracy", "precision", "recall", "f1", "roc_auc"):
    print(f"  {name:<10} {metrics[name]:.4f}")
print("\nConfusion matrix")
print("                    Pred: No   Pred: Yes")
print(f"  Actual: No      {cm[0, 0]:>9}   {cm[0, 1]:>9}")
print(f"  Actual: Yes     {cm[1, 0]:>9}   {cm[1, 1]:>9}")
print("\n" + classification_report(y_test, pred, target_names=["No purchase", "Purchase"]))

# Sanity check: stored training metrics should match this evaluation
stored_f1 = payload["metrics"]["f1"]
print(f"F1 stored in model.pkl: {stored_f1:.4f}  |  F1 recomputed here: {metrics['f1']:.4f}")
if abs(stored_f1 - metrics["f1"]) > 1e-6:
    print("WARNING: mismatch - the dataset changed after training. Re-run train_model.py.")

os.makedirs(REPORT_DIR, exist_ok=True)
out = os.path.join(REPORT_DIR, "evaluation.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)
print(f"\nReport saved to {os.path.abspath(out)}")
