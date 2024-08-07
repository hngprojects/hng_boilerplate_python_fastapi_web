from pydantic import BaseModel
from typing import List, Dict, Union


class AnalyticsChartsResponse(BaseModel):
    """
    Schema Response for analytics line charts
    """
    status: str
    status_code: int
    message: str
    data: Dict


class MetricData(BaseModel):
    value: int | float
    percentage_increase: float


class SuperAdminMetrics(BaseModel):
    total_revenue: MetricData
    total_products: MetricData
    total_users: MetricData
    lifetime_sales: MetricData

class UserMetrics(BaseModel):
    total_revenue: MetricData
    subscriptions: MetricData
    sales: MetricData
    active_now: MetricData

class AnalyticsSummaryResponse(BaseModel):
    message: str
    status: str
    status_code: int
    data: List[Dict[str, Union[float, int, MetricData]]]
