from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.connection import get_db
from backend.models.prediction import Prediction
from backend.models.followup import FollowUp
from backend.schemas.prediction import PredictionRequest, PredictionOut
from sqlalchemy.orm import contains_eager

from backend.models.customer import Customer
from backend.services.ml_service import run_prediction
from backend.services.pagination import Page, PageParams, paginate

router = APIRouter(prefix="/predictions", tags=["ML Predictions"])


@router.post("/", response_model=PredictionOut, status_code=201)
def create_prediction(data: PredictionRequest, db: Session = Depends(get_db)):
    """
    Run the ML model on the call data, persist the prediction,
    and auto-create a follow-up if classification is High or Medium.
    """
    result = run_prediction({
        "duration_seconds":  data.duration_seconds,
        "requested_info":    int(data.requested_info),
        "accepted_followup": int(data.accepted_followup),
        "age":               data.age,
        "has_followup":      int(data.has_followup or False),
        "outcome":           data.outcome,
        "interest":          data.interest,
        "customer_status":   data.customer_status,
    })

    prediction = Prediction(
        customer_id    = data.customer_id,
        call_id        = data.call_id,
        probability    = result["probability"],
        classification = result["classification"],
        recommendation = result["recommendation"],
    )
    db.add(prediction)
    db.flush()

    # Auto-create follow-up based on classification
    if result["classification"] in ("High", "Medium"):
        days_ahead = 2 if result["classification"] == "High" else 7
        followup = FollowUp(
            customer_id    = data.customer_id,
            call_id        = data.call_id,
            scheduled_date = date.today() + timedelta(days=days_ahead),
            reason         = result["recommendation"],
            status         = "Pending",
        )
        db.add(followup)

    db.commit()
    db.refresh(prediction)
    return prediction


SORTABLE = {
    "predicted_at": Prediction.predicted_at, "customer_name": Customer.name,
    "probability": Prediction.probability, "classification": Prediction.classification,
}


@router.get("/", response_model=Page[PredictionOut])
def list_predictions(
    q: Optional[str] = None,
    customer_id: Optional[int] = None,
    classification: Optional[str] = None,
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
):
    """Paginated predictions. `q` searches customer name and recommendation."""
    query = db.query(Prediction).join(Prediction.customer).options(contains_eager(Prediction.customer))
    if q:
        like = f"%{q}%"
        query = query.filter(Customer.name.ilike(like) | Prediction.recommendation.ilike(like))
    if customer_id:
        query = query.filter(Prediction.customer_id == customer_id)
    if classification:
        query = query.filter(Prediction.classification == classification)
    return paginate(query, params, SORTABLE, "predicted_at", "desc", Prediction.id)
