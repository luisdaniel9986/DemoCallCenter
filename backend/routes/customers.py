from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.connection import get_db
from backend.models.customer import Customer
from backend.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from backend.services.pagination import Page, PageParams, paginate

router = APIRouter(prefix="/customers", tags=["Customers"])


SORTABLE = {
    "id": Customer.id, "name": Customer.name, "company": Customer.company,
    "age": Customer.age, "status": Customer.status, "registered_at": Customer.registered_at,
}


@router.get("/", response_model=Page[CustomerOut])
def list_customers(
    q: Optional[str] = None,
    status: Optional[str] = None,
    params: PageParams = Depends(),
    db: Session = Depends(get_db),
):
    """Paginated customers. `q` searches name, company, email and phone."""
    query = db.query(Customer)
    if q:
        like = f"%{q}%"
        query = query.filter(
            Customer.name.ilike(like) | Customer.company.ilike(like)
            | Customer.email.ilike(like) | Customer.phone.ilike(like)
        )
    if status:
        query = query.filter(Customer.status == status)
    return paginate(query, params, SORTABLE, "id", "asc", Customer.id)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()

