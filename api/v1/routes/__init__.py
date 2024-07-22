from fastapi import APIRouter
from api.v1.routes.roles import role
from api.v1.routes.plans import plans
from api.v1.routes.job import job

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(role)
api_version_one.include_router(job)
api_version_one.include_router(plans)
