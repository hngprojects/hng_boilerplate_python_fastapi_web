from fastapi import APIRouter
from api.routes.greetings import greetings_router


api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(greetings_router)