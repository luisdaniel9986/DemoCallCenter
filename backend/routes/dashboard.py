from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database.connection import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Key performance indicators for the main panel (uses DB view)."""
    row = db.execute(text("SELECT * FROM v_dashboard_metrics")).mappings().first()
    return dict(row) if row else {}


@router.get("/pending-followups")
def get_pending_followups(db: Session = Depends(get_db)):
    """Top 20 pending follow-ups ordered by ML priority."""
    rows = db.execute(
        text("SELECT * FROM v_pending_followups LIMIT 20")
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/customer-summary")
def get_customer_summary(db: Session = Depends(get_db)):
    """Customer summary ordered by conversion probability."""
    rows = db.execute(
        text(
            "SELECT * FROM v_customer_summary "
            "ORDER BY max_conversion_prob DESC NULLS LAST LIMIT 50"
        )
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/calls-per-day")
def get_calls_per_day(days: int = 30, db: Session = Depends(get_db)):
    """Calls per day for the `days` days before the latest call."""
    rows = db.execute(
        text(
            "SELECT called_at::date AS day, COUNT(*) AS total "
            "FROM calls "
            "WHERE called_at >= (SELECT MAX(called_at) FROM calls) - make_interval(days => :days) "
            "GROUP BY day ORDER BY day"
        ),
        {"days": days},
    ).mappings().all()
    return [{"day": str(r["day"]), "total": r["total"]} for r in rows]


@router.get("/call-outcomes")
def get_call_outcomes(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT outcome::text AS name, COUNT(*) AS total FROM calls GROUP BY outcome ORDER BY total DESC")
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/customers-by-status")
def get_customers_by_status(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT status::text AS name, COUNT(*) AS total FROM customers GROUP BY status ORDER BY total DESC")
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/predictions-by-class")
def get_predictions_by_class(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT classification::text AS name, COUNT(*) AS total FROM predictions GROUP BY classification")
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/probability-distribution")
def get_probability_distribution(db: Session = Depends(get_db)):
    """Predictions grouped in 10 probability buckets (0-10%, 10-20%, ...)."""
    rows = db.execute(
        text(
            "SELECT LEAST(FLOOR(probability * 10), 9)::int AS bucket, COUNT(*) AS total "
            "FROM predictions GROUP BY bucket ORDER BY bucket"
        )
    ).mappings().all()
    found = {r["bucket"]: r["total"] for r in rows}
    return [{"range": f"{b * 10}-{b * 10 + 10}%", "total": found.get(b, 0)} for b in range(10)]


@router.get("/priority-customers")
def get_priority_customers(limit: int = 10, db: Session = Depends(get_db)):
    """Customers with the highest conversion probability (latest prediction of each)."""
    rows = db.execute(
        text(
            "SELECT * FROM ("
            "  SELECT DISTINCT ON (c.id) c.id, c.name, c.company, p.probability, "
            "         p.classification::text AS classification "
            "  FROM customers c JOIN predictions p ON p.customer_id = c.id "
            "  ORDER BY c.id, p.predicted_at DESC"
            ") t ORDER BY probability DESC LIMIT :limit"
        ),
        {"limit": limit},
    ).mappings().all()
    return [{**dict(r), "probability": float(r["probability"])} for r in rows]
