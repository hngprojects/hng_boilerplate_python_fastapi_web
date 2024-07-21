from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    status
    )
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.v1.models.user import User, WaitlistUser
from api.v1.models.blog import BlogCategory
from api.v1.schemas.blog_category_schema import BlogCategoryCreate, BlogCategoryResponse
from api.db.database import get_db, Base, engine
from api.utils.dependencies import get_current_admin



blog_category = APIRouter(prefix="/blog-categories", tags=["Blog Categories"])

@blog_category.post("/", response_model=BlogCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_blog_category(
    category: BlogCategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
  
    if not category.name or len(category.name) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data. Please provide a valid category name.",
        )
    
    existing_category = db.query(BlogCategory).filter(BlogCategory.name == category.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists.",
        )

    new_category = BlogCategory(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return BlogCategoryResponse(
        status= "success",
        message= "Blog category created successfully.",
        status_code = 201
    )
