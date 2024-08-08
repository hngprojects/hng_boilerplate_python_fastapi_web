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


class SuperAdminMetrics(BaseModel):
    total_revenue: Dict[str, Union[float, str]]
    total_products: Dict[str, Union[int, str]]
    total_users: Dict[str, Union[int, str]]
    lifetime_sales: Dict[str, Union[float, str]]


class UserMetrics(BaseModel):
    total_revenue: Dict[str, Union[float, str]]
    subscriptions: Dict[str, Union[int, str]]
    sales: Dict[str, Union[int, str]]
    active_now: Dict[str, Union[int, str]]


class AnalyticsSummaryResponse(BaseModel):
    message: str
    status: str
    status_code: int
    data: Union[SuperAdminMetrics, UserMetrics]
