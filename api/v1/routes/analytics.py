from fastapi import status, Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2
from datetime import datetime, timedelta
from api.db.database import get_db
from api.v1.services.user import oauth2_scheme
from api.v1.services.analytics import analytics_service, AnalyticsServices

analytics = APIRouter(prefix='/analytics')


@analytics.get('/line-chart-data', status_code=status.HTTP_200_OK)
async def get_analytics_line_chart_data(token: Annotated[OAuth2, Depends(oauth2_scheme)],
                                        db: Annotated[Session, Depends(get_db)]):
    """
    Retrieves analytics line-chart-data for an organisation or super admin.
    Args:
        token: access_token
        db: database Session object
    Retunrs:
        analytics response: contains the analytics data
    """
    return analytics_service.get_analytics_line_chart(token, db)
