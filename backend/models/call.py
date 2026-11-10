from backend.database.connection import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship


class Call(Base):
    __tablename__ = "calls"

    id                   = Column(Integer, primary_key=True, index=True)
    customer_id           = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    called_at               = Column(DateTime, default=func.now())
    duration_seconds    = Column(Integer, nullable=False, default=0)
    outcome            = Column(String(30), nullable=False)
    interest             = Column(String(15), default="No interest")
    requested_info = Column(Boolean, default=False)
    accepted_followup   = Column(Boolean, default=False)
    notes                = Column(Text)
    created_at            = Column(DateTime, default=func.now())

    customer    = relationship("Customer",   back_populates="calls")
    followups   = relationship("FollowUp",   back_populates="call", passive_deletes=True)
    predictions = relationship("Prediction", back_populates="call", passive_deletes=True)

    @property
    def customer_name(self):
        return self.customer.name if self.customer else None

