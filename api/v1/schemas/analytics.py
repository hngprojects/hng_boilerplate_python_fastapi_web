from pydantic import BaseModel
from typing import List, Dict

class AnalyticsChartsResponse(BaseModel):
    """
    Schema Response for analytics line charts
    """
    status: str
    status_code: int
    message: str
    data: Dict