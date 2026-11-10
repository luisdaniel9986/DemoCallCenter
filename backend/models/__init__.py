# Import all models so SQLAlchemy registers them before create_all()
from backend.models.customer   import Customer
from backend.models.call       import Call
from backend.models.followup   import FollowUp
from backend.models.prediction import Prediction

__all__ = ["Customer", "Call", "FollowUp", "Prediction"]
