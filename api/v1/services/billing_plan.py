from sqlalchemy.orm import Session
from api.v1.models.billing_plan import BillingPlan
from typing import Any, Optional
from api.core.base.services import Service
from api.v1.schemas.plans import CreateSubscriptionPlan


class BillingPlanService(Service):
	'''Product service functionality'''

	def create(db: Session, request: CreateSubscriptionPlan):
		"""
		Create and return a new billing plan
		"""

		plan = BillingPlan(**request.dict())
		db.add(plan)
		db.commit()
		db.refresh(plan)

		return plan

	def delete():
		pass

	def fetch():
		pass

	def update():
		pass

	def fetch_all(db: Session, **query_params: Optional[Any]):
		'''Fetch all products with option tto search using query parameters'''

		query = db.query(BillingPlan)

		# Enable filter by query parameter
		if query_params:
			for column, value in query_params.items():
				if hasattr(BillingPlan, column) and value:
					query = query.filter(getattr(BillingPlan, column).ilike(f'%{value}%'))

		return query.all()


billing_plan_service = BillingPlanService