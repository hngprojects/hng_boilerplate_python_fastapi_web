from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..schemas.category import CategoryList
from ..services import category as category_service
from ...db.database import get_db
from ..services.cache import cache

# from ..auth.jwt import get_current_user    (Add your jwt auth to get current logged in user)

router = APIRouter()

@router.get("/categories", response_model=CategoryList)
@cache
async def read_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    parent_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
    # current_user: str = Depends(get_current_user)  # Add this line for getting curent logged in user
):
    categories = category_service.get_categories(db, skip=skip, limit=limit, parent_id=parent_id)
    return {"status_code": 200, "categories": categories}