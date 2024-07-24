from sqlalchemy.orm import Session 
from api.v1.models.plans import SubscriptionPlan
from typing import Any, Optional
from api.core.base.services import Service



class BillingPlanService(Service):
    '''Product service functionality'''

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all products with option tto search using query parameters'''

        query = db.query(SubscriptionPlan)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(SubscriptionPlan, column) and value:
                    query = query.filter(getattr(SubscriptionPlan, column).ilike(f'%{value}%'))

        return query.all()

    
billing_plan_service = BillingPlanService()