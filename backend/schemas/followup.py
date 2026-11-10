from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class FollowUpBase(BaseModel):
    customer_id:       int
    call_id:       Optional[int]  = None
    scheduled_date: date
    reason:           Optional[str]  = None
    status:           Optional[str]  = "Pending"


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    reason:           Optional[str]  = None
    status:           Optional[str]  = None


class FollowUpOut(FollowUpBase):
    id:             int
    customer_name:  Optional[str]      = None
    created_at:      Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

