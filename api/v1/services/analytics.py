from fastapi import Depends, HTTPException
from fastapi.security import OAuth2
from sqlalchemy.orm import Session
from sqlalchemy import cast, extract, Integer, func, and_
from typing import Annotated, List, Union
import calendar
from datetime import datetime, timedelta
from api.db.database import get_db
from api.v1.services.user import user_service
from api.core.base.services import Service
from api.v1.services.user import oauth2_scheme
from api.v1.models.user import user_organisation_association
from api.v1.models.sales import Sales
from api.v1.models.product import Product
from api.v1.models.user import User
from api.v1.models.billing_plan import BillingPlan
from api.v1.schemas.analytics import (
    AnalyticsChartsResponse, AnalyticsSummaryResponse, SuperAdminMetrics, UserMetrics)

DATA: dict = {idx: month_name for idx,
              month_name in enumerate(calendar.month_name) if month_name}

MONTHS_AND_DATA: dict = {month: 0 for month in DATA.values()}


class AnalyticsServices(Service):
    """
    Handles services related to analytis
    """

    def get_analytics_line_chart(self, token: Annotated[OAuth2, Depends(oauth2_scheme)],
                                 db: Annotated[Session, Depends(get_db)]) -> AnalyticsChartsResponse:
        """
        Get analytics data for the line chart.


        Args:
            token: access_token from header
            db: database Session object
        Retuns:
            AnalyticsChartsResponse: reponse object to the user
        """
        user: object = user_service.get_current_user(access_token=token, db=db)

        # check if the analytics-line-data is for org admin
        if not user.is_superadmin:
            user_organisation: object = (db.query(user_organisation_association)
                                         .filter_by(user_id=user.id).first())
            if not user_organisation:
                return AnalyticsChartsResponse(
                    message='User is not part of Any organisation yet.',
                    status='success',
                    status_code=200,
                    data={month: 0 for month in DATA.values()}
                )
            data = self.get_line_chart_data(db, super_admin=False,
                                            org_id=user_organisation.organisation_id)
            message: str = 'Successfully retrieved line-charts'

        # check if user is a super admin
        elif user.is_superadmin:
            data = self.get_line_chart_data(db)
            message: str = 'Successfully retrieved line-charts for super_admin'

        return AnalyticsChartsResponse(message=message,
                                       status='success',
                                       status_code=200,
                                       data=data)

    def get_line_chart_data(self, db: Annotated[Session, Depends(get_db)],
                            super_admin: bool = True, org_id: str = '') -> tuple:
        """
        Rearranges the data for the line-chart.
        Args:
            db: database session object
            super_admin: boolean signifying revenues for super admin
            organisation_id: the organisation id of the user
        Returns:
            MONTHS_AND_DATA: a dict conatining the months(str) and revenue(float) for each month
        """
        global DATA, MONTHS_AND_DATA

        results = self.get_year_revenue(db, super_admin, org_id)
        try:
            mapped_result = {DATA[result[0]]: result[1] for result in results}
        except KeyError:
            pass

        for month, value in mapped_result.items():
            MONTHS_AND_DATA[month] = value

        return MONTHS_AND_DATA

    def get_year_revenue(self, db: Annotated[Session, Depends(get_db)],
                         super_admin: bool = True,
                         org_id: str = None) -> List[tuple]:
        """
        Get revenue data grouped by month.

        Args:
            db: database session object
            super_admin: boolean signifying revenues for super admin
            organisation_id: the organisation id of the user
        Returns:
            query result: a list conatining the rows of months(int) and revenue(int)
        """
        query = db.query(
            cast(extract('month', Sales.created_at), Integer).label('month'),
            func.sum(getattr(Sales, 'amount')).label('total')
        )

        if not super_admin:
            query = query.filter(Sales.organisation_id == org_id)

        query = query.group_by(
            cast(extract('month', Sales.created_at), Integer)
        ).order_by(
            cast(extract('month', Sales.created_at), Integer)
        )

        revenue_result = query.all()
        if not revenue_result:
            revenue_result = [(0, 0), (0, 0)]

        return revenue_result

    def get_analytics_summary(self, token: Annotated[OAuth2, Depends(oauth2_scheme)],
                              db: Annotated[Session, Depends(get_db)],
                              start_date: datetime,
                              end_date: datetime) -> AnalyticsSummaryResponse:
        """
        Get analytics summary data.

        Args:
            token: access_token from header
            db: database Session object
            start_date: start date for filtering
            end_date: end date for filtering
        Returns:
            AnalyticsSummaryResponse: response object to the user
        """
        user: object = user_service.get_current_user(access_token=token, db=db)

        if user.is_superadmin:
            data = self.get_summary_data_super_admin(db, start_date, end_date)
            message = "Admin Statistics Fetched"
        else:
            user_organisation = db.query(
                user_organisation_association).filter_by(user_id=user.id).first()
            if not user_organisation:
                data = {
                    "revenue": {
                        "current_month": 0,
                        "previous_month": 0,
                        "percentage_difference": "0.00%"
                    },
                    "subscriptions": {
                        "current_month": 0,
                        "previous_month": 0,
                        "percentage_difference": "0.00%"
                    },
                    "orders": {
                        "current_month": 0,
                        "previous_month": 0,
                        "percentage_difference": "0.00%"
                    },
                    "active_users": {
                        "current": 0,
                        "difference_an_hour_ago": 0
                    }
                }
                message = "User is not part of any organisation"
            else:
                data = self.get_summary_data_organisation(
                    db, user_organisation.organisation_id, start_date, end_date)
                message = "User Statistics Fetched"

        return AnalyticsSummaryResponse(
            message=message,
            status='success',
            status_code=200,
            data=data
        )

    def get_summary_data_super_admin(self, db: Session, start_date: datetime, end_date: datetime) -> dict:
        total_revenue = db.query(func.sum(Sales.amount)).filter(
            Sales.created_at.between(start_date, end_date)).scalar() or 0
        total_products = db.query(func.count(Product.id)).scalar() or 0
        total_users = db.query(func.count(User.id)).scalar() or 0
        lifetime_sales = db.query(func.sum(Sales.amount)).filter(
            Sales.created_at <= end_date).scalar() or 0

        last_month_start = start_date - timedelta(days=30)
        last_month_revenue = db.query(func.sum(Sales.amount)).filter(
            Sales.created_at.between(last_month_start, start_date)).scalar() or 0
        last_month_products = db.query(func.count(Product.id)).filter(
            Product.created_at < start_date).scalar() or 0
        last_month_users = db.query(func.count(User.id)).filter(
            User.created_at < start_date).scalar() or 0
        last_month_lifetime_sales = db.query(func.sum(Sales.amount)).filter(
            Sales.created_at < start_date).scalar() or 0

        return {
            "total_revenue": {
                "current_month": total_revenue,
                "previous_month": last_month_revenue,
                "percentage_difference": f"{self.calculate_percentage_increase(last_month_revenue, total_revenue)}%"
            },
            "total_users": {
                "current_month": total_users,
                "previous_month": last_month_users,
                "percentage_difference": f"{self.calculate_percentage_increase(last_month_users, total_users)}%"
            },
            "total_products": {
                "current_month": total_products,
                "previous_month": last_month_products,
                "percentage_difference": f"{self.calculate_percentage_increase(last_month_products, total_products)}%"
            },
            "lifetime_sales": {
                "current_month": lifetime_sales,
                "previous_month": last_month_lifetime_sales,
                "percentage_difference": f"{self.calculate_percentage_increase(last_month_lifetime_sales, lifetime_sales)}%"
            }
        }

    def get_summary_data_organisation(self, db: Session, org_id: str, start_date: datetime, end_date: datetime) -> dict:
        total_revenue = db.query(func.sum(Sales.amount)).filter(and_(
            Sales.organisation_id == org_id, Sales.created_at.between(start_date, end_date))).scalar() or 0
        subscriptions = db.query(func.count(BillingPlan.id)).filter(and_(
            BillingPlan.organisation_id == org_id, BillingPlan.created_at.between(start_date, end_date))).scalar() or 0
        sales = db.query(func.count(Sales.id)).filter(and_(
            Sales.organisation_id == org_id, Sales.created_at.between(start_date, end_date))).scalar() or 0

        last_month_start = start_date - timedelta(days=30)
        last_month_revenue = db.query(func.sum(Sales.amount)).filter(and_(
            Sales.organisation_id == org_id, Sales.created_at.between(last_month_start, start_date))).scalar() or 0
        last_month_subscriptions = db.query(func.count(BillingPlan.id)).filter(and_(
            BillingPlan.organisation_id == org_id, BillingPlan.created_at.between(last_month_start, start_date))).scalar() or 0
        last_month_sales = db.query(func.count(Sales.id)).filter(and_(
            Sales.organisation_id == org_id, Sales.created_at.between(last_month_start, start_date))).scalar() or 0

        last_hour = datetime.utcnow() - timedelta(hours=1)
        active_now = db.query(func.count(User.id)).filter(and_(
            User.is_active == True,
            User.organisations.any(id=org_id)
        )).scalar() or 0
        previous_hour = last_hour - timedelta(hours=1)
        active_previous_hour = db.query(func.count(User.id)).filter(and_(
            User.is_active == True,
            User.organisations.any(id=org_id),
            User.created_at >= last_hour - timedelta(hours=1),
            User.created_at < last_hour
        )).scalar() or 0

        return {
            "revenue": {
                "current_month": total_revenue,
                "previous_month": last_month_revenue,
                "percentage_difference": f"{self.calculate_percentage_increase(last_month_revenue, total_revenue)}%"
            },
            "subscriptions": {
                "current_month": subscriptions,
                "previous_month": last_month_subscriptions,
                "percentage_difference": f"{self.calculate_percentage_increase(last_month_subscriptions, subscriptions)}%"
            },
            "orders": {
                "current_month": sales,
                "previous_month": last_month_sales,
                "percentage_difference": f"{self.calculate_percentage_increase(last_month_sales, sales)}%"
            },
            "active_users": {
                "current": active_now,
                "difference_an_hour_ago": active_now - active_previous_hour
            }
        }

    def calculate_percentage_increase(self, previous_value: Union[float, int], current_value: Union[float, int]) -> float:
        """
        Calculate the percentage increase from previous_value to current_value.

        Args:
            previous_value: The previous value.
            current_value: The current value.

        Returns:
            float: The percentage increase.
        """
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        return ((current_value - previous_value) / previous_value) * 100

    def create(self):
        """
        Create
        """
        pass

    def update(self):
        """
        Update
        """
        pass

    def fetch(self):
        """
        Fetch
        """
        pass

    def fetch_all(self):
        """
        Fetch All
        """
        pass

    def delete(self):
        """
        Delete
        """
        pass


analytics_service = AnalyticsServices()
