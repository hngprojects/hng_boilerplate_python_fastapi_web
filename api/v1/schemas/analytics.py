from pydantic import BaseModel
from typing import List

class SummaryResponse(BaseModel):
    status: bool
    status_code: int
    total_users: int
    active_users: int
    new_users: int
    total_revenue: float

class ChartResponse(BaseModel):
    status: bool
    status_code: int
    labels: List[str]
    data: List[float]

class BarChartResponse(ChartResponse):
    categories: List[str]

class PieChartResponse(ChartResponse):
    segments: List[str]
    values: List[float]

class ErrorResponse(BaseModel):
    status: bool
    status_code: int
    error: str
    message: str
    details: dict

class RealtimeUpdate(BaseModel):
    status: bool
    status_code: int
    type: str
    data: dict