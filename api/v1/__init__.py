from fastapi import APIRouter
from api.v1 import jobs

router = APIRouter()
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
