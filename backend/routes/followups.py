from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.connection import get_db
from backend.models.followup import FollowUp
from sqlalchemy.orm import contains_eager

from backend.models.customer import Customer
from backend.schemas.followup import FollowUpCreate, FollowUpUpdate, FollowUpOut
from backend.services.pagination import Page, PageParams, paginate

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


SORTABLE = {
    "scheduled_date": FollowUp.scheduled_date, "customer_name": Customer.name,
    "reason": FollowUp.reason, "status": FollowUp.status,
}


@router.get("/", response_model=Page[FollowUpOut])
def list_followups(
    q: Optional[str] = None,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
):
    """Paginated follow-ups. `q` searches customer name and reason."""
    query = db.query(FollowUp).join(FollowUp.customer).options(contains_eager(FollowUp.customer))
    if q:
        like = f"%{q}%"
        query = query.filter(Customer.name.ilike(like) | FollowUp.reason.ilike(like))
    if status:
        query = query.filter(FollowUp.status == status)
    if customer_id:
        query = query.filter(FollowUp.customer_id == customer_id)
    return paginate(query, params, SORTABLE, "scheduled_date", "asc", FollowUp.id)


@router.get("/{followup_id}", response_model=FollowUpOut)
def get_followup(followup_id: int, db: Session = Depends(get_db)):
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return followup


@router.post("/", response_model=FollowUpOut, status_code=201)
def create_followup(data: FollowUpCreate, db: Session = Depends(get_db)):
    followup = FollowUp(**data.model_dump())
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


@router.put("/{followup_id}", response_model=FollowUpOut)
def update_followup(followup_id: int, data: FollowUpUpdate, db: Session = Depends(get_db)):
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(followup, field, value)
    db.commit()
    db.refresh(followup)
    return followup


@router.delete("/{followup_id}", status_code=204)
def delete_followup(followup_id: int, db: Session = Depends(get_db)):
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    db.delete(followup)
    db.commit()

