"""
train_model.py
==============
Trains and compares three classifiers:
  1. Logistic Regression
  2. Decision Tree
  3. Random Forest  ← primary candidate

Saves the best model as ml/model.pkl.

Usage:
    python train_model.py
"""

import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing   import LabelEncoder
from sklearn.linear_model    import LogisticRegression
from sklearn.tree            import DecisionTreeClassifier
from sklearn.ensemble        import RandomForestClassifier
from sklearn.metrics         import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report,
    roc_auc_score, brier_score_loss,
)

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "dataset_calls.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
TEST_SIZE  = 0.20
SEED       = 42
# ─────────────────────────────────────────────

# ── Load data ─────────────────────────────────
print("\n📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"   Records: {len(df):,}  |  Columns: {df.shape[1]}")

# ── Feature selection ─────────────────────────
CATEGORICAL = ["outcome", "interest", "customer_status"]
NUMERICAL   = ["duration_seconds", "requested_info", "accepted_followup",
               "age", "has_followup"]
TARGET      = "purchased"

encoders = {}
df_ml    = df.copy()
for col in CATEGORICAL:
    le = LabelEncoder()
    df_ml[col + "_enc"] = le.fit_transform(df_ml[col].astype(str))
    encoders[col] = le

FEATURES = NUMERICAL + [c + "_enc" for c in CATEGORICAL]
X = df_ml[FEATURES]
y = df_ml[TARGET]

print(f"\n🔢 Features ({len(FEATURES)}): {FEATURES}")
print(f"🎯 Target: '{TARGET}'  →  {dict(y.value_counts().sort_index())}")

# ── Train / test split ────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=SEED, stratify=y
)
print(f"\n✂️  Train: {len(X_train):,}  |  Test: {len(X_test):,}")

# ── Define models ─────────────────────────────
MODELS = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=SEED),
    "Decision Tree":       DecisionTreeClassifier(max_depth=8, random_state=SEED),
    "Random Forest":       RandomForestClassifier(n_estimators=200, max_depth=10,
                                                   random_state=SEED, n_jobs=-1),
}

# ── Train and evaluate ────────────────────────
def evaluate(name, model, X_tr, y_tr, X_te, y_te) -> dict:
    model.fit(X_tr, y_tr)
    preds = model.predict(X_te)
    return {
        "name":      name,
        "model":     model,
        "accuracy":  accuracy_score(y_te, preds),
        "precision": precision_score(y_te, preds, zero_division=0),
        "recall":    recall_score(y_te, preds, zero_division=0),
        "f1":        f1_score(y_te, preds, zero_division=0),
        "roc_auc":   roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]),
        # Brier score: lower = better calibrated probabilities (they drive High/Medium/Low)
        "brier":     brier_score_loss(y_te, model.predict_proba(X_te)[:, 1]),
        "preds":     preds,
    }

results = []
print("\n🏋️  Training models...\n")
for name, model in MODELS.items():
    print(f"   ⏳ {name}...")
    r = evaluate(name, model, X_train, y_train, X_test, y_test)
    # 5-fold stratified CV on the training set: a more robust F1 than a single split
    cv = cross_val_score(model, X_train, y_train, scoring="f1",
                         cv=StratifiedKFold(5, shuffle=True, random_state=SEED))
    r["cv_f1"], r["cv_std"] = cv.mean(), cv.std()
    results.append(r)
    print(f"      ✅  Accuracy={r['accuracy']:.4f}  F1={r['f1']:.4f}")

# ── Comparison table ──────────────────────────
print("\n" + "=" * 86)
print(f"  {'MODEL':<22} {'ACC':>6} {'PREC':>6} {'REC':>6} {'F1':>6} {'AUC':>6} {'BRIER':>6} {'CV-F1':>13}")
print("=" * 86)
for r in results:
    print(f"  {r['name']:<22} {r['accuracy']:>6.4f} {r['precision']:>6.4f} {r['recall']:>6.4f} "
          f"{r['f1']:>6.4f} {r['roc_auc']:>6.4f} {r['brier']:>6.4f} {r['cv_f1']:>7.4f}+/-{r['cv_std']:.3f}")
print("=" * 86)

# ── Select best model ─────────────────────────
# Rule: keep the models statistically tied with the top cross-validated F1
# (within 1 std), then pick the one with the best-calibrated probabilities
# (lowest Brier score), because High/Medium/Low are derived from the probability.
top        = max(results, key=lambda r: r["cv_f1"])
candidates = [r for r in results if top["cv_f1"] - r["cv_f1"] <= top["cv_std"]]
best       = min(candidates, key=lambda r: r["brier"])
print(f"\n🏆 Best model: {best['name']}  (CV F1 = {best['cv_f1']:.4f}, test F1 = {best['f1']:.4f}, "
      f"AUC = {best['roc_auc']:.4f}, Brier = {best['brier']:.4f})")
print(f"   Tied on CV F1 (within 1 std of {top['name']}): {', '.join(r['name'] for r in candidates)}")
print("   Tie-break: lowest Brier score (best calibrated probabilities).")

# ── Detailed report ───────────────────────────
print(f"\n📊 Detailed report — {best['name']}:")
print(classification_report(y_test, best["preds"], target_names=["No purchase", "Purchase"]))

cm = confusion_matrix(y_test, best["preds"])
print(f"🔲 Confusion matrix:  TN={cm[0,0]}  FP={cm[0,1]}  FN={cm[1,0]}  TP={cm[1,1]}")

# ── Feature importance ────────────────────────
if hasattr(best["model"], "feature_importances_"):
    importances = pd.Series(best["model"].feature_importances_, index=FEATURES).sort_values(ascending=False)
    print(f"\n📌 Feature importance ({best['name']}):")
    for feat, imp in importances.items():
        bar = "█" * int(imp * 40)
        print(f"   {feat:<28} {imp:.4f}  {bar}")

# ── Save model ────────────────────────────────
payload = {
    "model":      best["model"],
    "encoders":   encoders,
    "features":   FEATURES,
    "model_name": best["name"],
    "metrics": {
        "accuracy":  best["accuracy"],
        "precision": best["precision"],
        "recall":    best["recall"],
        "f1":        best["f1"],
        "roc_auc":   best["roc_auc"],
        "brier":     best["brier"],
        "cv_f1":     best["cv_f1"],
    },
}
joblib.dump(payload, MODEL_PATH)
print(f"\n💾 Model saved to: {os.path.abspath(MODEL_PATH)}\n")

