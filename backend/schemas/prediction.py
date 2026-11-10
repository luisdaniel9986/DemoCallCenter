from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PredictionRequest(BaseModel):
    """Input data the ML endpoint expects after a call is registered."""
    customer_id:           int
    call_id:           Optional[int]  = None
    duration_seconds:    int
    outcome:            str
    interest:              str
    requested_info: bool
    accepted_followup:   bool
    age:                 int
    customer_status:       str
    has_followup:    Optional[bool] = False


class PredictionOut(BaseModel):
    id:               Optional[int] = None
    customer_name:    Optional[str] = None
    customer_id:      int
    call_id:      Optional[int]
    probability:    float
    classification:   str
    recommendation:   str
    predicted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

