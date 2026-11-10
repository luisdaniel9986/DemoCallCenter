from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class CustomerBase(BaseModel):
    name:            str            = Field(..., max_length=100)
    phone:          str            = Field(..., max_length=20)
    email:          Optional[str]  = None
    company:        Optional[str]  = None
    age:             Optional[int]  = Field(None, ge=18, le=100)
    registered_at: Optional[date] = None
    status:         Optional[str]  = "New"


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name:      Optional[str] = None
    phone:    Optional[str] = None
    email:    Optional[str] = None
    company:  Optional[str] = None
    age:       Optional[int] = None
    status:   Optional[str] = None


class CustomerOut(CustomerBase):
    id:             int
    created_at:      Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

