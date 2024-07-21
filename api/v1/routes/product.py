from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from api.v1.models.product import Product
from api.v1.schemas.product import ProductSearchResponse
from api.db.database import get_db
from typing import Optional
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/search", response_model=ProductSearchResponse)
async def search_items(
    q: Optional[str] = Query(None, description="The search term."),
    page: int = Query(1, ge=1, description="The page number for pagination."),
    limit: int = Query(10, ge=1, description="The number of results per page."),
    db: AsyncSession = Depends(get_db)
):
    if q is None or q.strip() == "":
        if q is None:
            raise HTTPException(status_code=400, detail="The query parameter 'q' is required.")
        else:
            raise HTTPException(status_code=400, detail="The query parameter 'q' must be a non-empty string.")

    query = select(Product).where(Product.name.ilike(f"%{q}%") | Product.description.ilike(f"%{q}%"))
    total_results = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_results.scalar()
    
    results = await db.execute(query.offset((page - 1) * limit).limit(limit))
    products = results.scalars().all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "results": products,
        "message": "Results found" if products else "No results found"
    }
