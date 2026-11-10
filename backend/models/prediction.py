from backend.database.connection import Base
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship


class Prediction(Base):
    __tablename__ = "predictions"

    id               = Column(Integer, primary_key=True, index=True)
    customer_id       = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    call_id       = Column(Integer, ForeignKey("calls.id", ondelete="SET NULL"), nullable=True)
    probability     = Column(Numeric(5, 4), nullable=False)
    classification    = Column(String(10), nullable=False)
    recommendation    = Column(String(200))
    predicted_at = Column(DateTime, default=func.now())

    customer = relationship("Customer", back_populates="predictions")
    call     = relationship("Call",     back_populates="predictions")

    @property
    def customer_name(self):
        return self.customer.name if self.customer else None

