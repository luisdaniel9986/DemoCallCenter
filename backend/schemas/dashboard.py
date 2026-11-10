from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_calls:          int
    answered_calls:      int
    info_requests:        int
    accepted_followups:      int
    avg_duration_sec:   int
    pending_followups: int
    total_customers:          int
    high_predictions:       int

