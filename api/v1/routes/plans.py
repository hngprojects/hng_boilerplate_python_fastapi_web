# crud.py
from sqlalchemy import insert
from api.db import database
from api.v1.models import plans
from api.v1.schemas import plans

async def create_plan(plan: PlanCreate):
    query = insert(plans).values(plan_name=plan.plan_name, amount=plan.amount)
    record_id = await database.execute(query)
    return {**plan.dict(), "id": record_id}
