import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import contains_eager

from backend.database.connection import get_db
from backend.models.customer import Customer
from backend.models.call import Call
from backend.schemas.call import CallCreate, CallSimulate, CallOut
from backend.services.pagination import Page, PageParams, paginate

router = APIRouter(prefix="/calls", tags=["Calls"])


SORTABLE = {
    "called_at": Call.called_at, "customer_name": Customer.name,
    "duration_seconds": Call.duration_seconds, "outcome": Call.outcome, "interest": Call.interest,
}


@router.get("/", response_model=Page[CallOut])
def list_calls(
    q: Optional[str] = None,
    customer_id: Optional[int] = None,
    outcome: Optional[str] = None,
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
):
    """Paginated call history. `q` searches customer name and notes."""
    query = db.query(Call).join(Call.customer).options(contains_eager(Call.customer))
    if q:
        like = f"%{q}%"
        query = query.filter(Customer.name.ilike(like) | Call.notes.ilike(like))
    if customer_id:
        query = query.filter(Call.customer_id == customer_id)
    if outcome:
        query = query.filter(Call.outcome == outcome)
    return paginate(query, params, SORTABLE, "called_at", "desc", Call.id)


@router.get("/{call_id}", response_model=CallOut)
def get_call(call_id: int, db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.post("/", response_model=CallOut, status_code=201)
def register_call(data: CallCreate, db: Session = Depends(get_db)):
    call = Call(**data.model_dump())
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


@router.post("/simulate", status_code=200)
def simulate_call(data: CallSimulate, db: Session = Depends(get_db)):
    """
    Simulate an incoming call.
    Returns customer info to display on the Call Center screen.
    If no customer_id is provided, a random customer is selected.
    """
    if data.customer_id:
        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    else:
        total = db.query(Customer).count()
        if total == 0:
            raise HTTPException(status_code=404, detail="No customers in database")
        customer = db.query(Customer).offset(random.randint(0, total - 1)).first()

    return {
        "customer_id": customer.id,
        "name":        customer.name,
        "phone":       customer.phone,
        "company":     customer.company or "—",
        "status":      customer.status,
        "age":         customer.age,
        "message":     "📞 Incoming call simulated",
    }

