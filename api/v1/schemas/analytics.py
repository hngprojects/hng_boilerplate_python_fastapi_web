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


class Metrics(BaseModel):
    """
    Base schema for metrics with current and previous month values and percentage difference.
    """
    current_month: Union[float, int]
    previous_month: Union[float, int]
    percentage_difference: str


class ActiveUsersMetrics(BaseModel):
    """
    Schema for active users metrics with the current value and the difference from an hour ago.
    """
    current: int
    difference_an_hour_ago: int


class SuperAdminMetrics(BaseModel):
    total_revenue: Metrics
    total_products: Metrics
    total_users: Metrics
    lifetime_sales: Metrics


class UserMetrics(BaseModel):
    revenue: Metrics
    subscriptions: Metrics
    orders: Metrics
    active_users: ActiveUsersMetrics


class AnalyticsSummaryResponse(BaseModel):
    message: str
    status: str
    status_code: int
    data: Union[SuperAdminMetrics, UserMetrics]
