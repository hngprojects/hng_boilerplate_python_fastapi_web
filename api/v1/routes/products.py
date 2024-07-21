from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..schemas.category import CategoryList, Category
from ..services import category as category_service
from ...db.database import get_db
from api.utils.json_response import JsonResponseDict

# from ..auth.jwt import get_current_user

router = APIRouter()

# Existing product routes...

@router.get("/categories", response_model=CategoryList)
async def read_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    parent_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
    # current_user: str = Depends(get_current_user)
):

    
    
    try:
        orm_categories = category_service.get_categories(db, skip=skip, limit=limit, parent_id=parent_id)
        pydantic_categories = [Category.from_orm(cat) for cat in orm_categories]
        return CategoryList(status_code=200, categories=pydantic_categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
