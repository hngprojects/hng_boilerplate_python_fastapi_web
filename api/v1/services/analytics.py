from fastapi import Depends
from fastapi.security import OAuth2
from sqlalchemy.orm import Session
from  sqlalchemy import cast, extract, Integer, func
from typing import Annotated, List
import calendar

from api.db.database import get_db
from api.v1.services.user import user_service
from api.core.base.services import Service
from api.v1.services.user import oauth2_scheme
from api.v1.models.user import user_organization_association
from api.v1.models.sales import Sales
from api.v1.schemas.analytics import( AnalyticsChartsResponse)

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
        if not user.is_super_admin:
            user_organization: object = (db.query(user_organization_association)
                                         .filter_by(user_id=user.id).first())
            if not user_organization:
                return AnalyticsChartsResponse(
                    message='User is not part of Any organization yet.',
                    status='success',
                    status_code=200,
                    data={month: 0 for month in DATA.values()}
                )
            data = self.get_line_chart_data(db, super_admin=False,
                                            org_id=user_organization.organization_id)
            message: str = 'Successfully retrieved line-charts'

        # check if user is a super admin
        elif user.is_super_admin:
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
            organization_id: the organization id of the user
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
            organization_id: the organization id of the user
        Returns:
            query result: a list conatining the rows of months(int) and revenue(int)
        """
        query = db.query(
            cast(extract('month', Sales.created_at), Integer).label('month'),
            func.sum(getattr(Sales, 'amount')).label('total')
        )

        if not super_admin:
            query = query.filter(Sales.organization_id == org_id)

        query = query.group_by(
            cast(extract('month', Sales.created_at), Integer)
        ).order_by(
            cast(extract('month', Sales.created_at), Integer)
        )
       
        revenue_result = query.all()
        if not revenue_result:
            revenue_result = [(0, 0), (0, 0)]

        return revenue_result

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