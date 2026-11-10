from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CallBase(BaseModel):
    customer_id:           int
    duration_seconds:    int           = Field(0, ge=0)
    outcome:              str
    interest:             Optional[str] = "No interest"
    requested_info: Optional[bool] = False
    accepted_followup:   Optional[bool] = False
    notes:                Optional[str] = None


class CallCreate(CallBase):
    pass


class CallSimulate(BaseModel):
    """Payload to trigger an incoming call simulation."""
    customer_id: Optional[int] = None   # None → system picks a random customer


class CallOut(CallBase):
    id:        int
    customer_name: Optional[str]  = None
    called_at:  Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

