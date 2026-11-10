from backend.database.connection import Base
from sqlalchemy import Column, Integer, String, SmallInteger, Date, DateTime, func
from sqlalchemy.orm import relationship


class Customer(Base):
    __tablename__ = "customers"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(100), nullable=False)
    phone       = Column(String(20),  nullable=False)
    email          = Column(String(150), unique=True)
    company        = Column(String(100))
    age            = Column(SmallInteger)
    registered_at = Column(Date, default=func.current_date())
    status        = Column(String(10), default="New")
    created_at      = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    calls       = relationship("Call",       back_populates="customer",   cascade="all, delete-orphan", passive_deletes=True)
    followups   = relationship("FollowUp",   back_populates="customer",   cascade="all, delete-orphan", passive_deletes=True)
    predictions = relationship("Prediction", back_populates="customer",   cascade="all, delete-orphan", passive_deletes=True)

