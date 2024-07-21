from fastapi import APIRouter
from .routes import categories

api_router = APIRouter()
api_router.include_router(categories.router, prefix="/products", tags=["categories"])