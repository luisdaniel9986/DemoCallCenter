from backend.database.connection import Base
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id               = Column(Integer, primary_key=True, index=True)
    customer_id       = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    call_id       = Column(Integer, ForeignKey("calls.id", ondelete="SET NULL"), nullable=True)
    scheduled_date = Column(Date, nullable=False)
    reason           = Column(String(200))
    status          = Column(String(15), default="Pending")
    created_at        = Column(DateTime, default=func.now())
    updated_at   = Column(DateTime, default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="followups")
    call     = relationship("Call",     back_populates="followups")

    @property
    def customer_name(self):
        return self.customer.name if self.customer else None

