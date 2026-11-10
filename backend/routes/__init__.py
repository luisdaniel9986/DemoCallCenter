from backend.routes.customers  import router as customers_router
from backend.routes.calls      import router as calls_router
from backend.routes.followups  import router as followups_router
from backend.routes.predictions import router as predictions_router
from backend.routes.dashboard  import router as dashboard_router

__all__ = [
    "customers_router",
    "calls_router",
    "followups_router",
    "predictions_router",
    "dashboard_router",
]
