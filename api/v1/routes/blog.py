from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from api.v1.schemas.blog import blogResponseModel, blogRequest
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.utils.dependencies import get_current_user
from api.v1.services.blog_services import blogUpdateService
from uuid import UUID

blog_router = APIRouter(prefix="/api/v1", tags=["blogs"])

@blog_router.put("/blog/{blog_id}", response_model=blogResponseModel)
async def updateBlog(blog_id: UUID, blogPost: blogRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        updated_blog_post = blogUpdateService(blog_id, blogPost.title, blogPost.content, db, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        # Catch any other exceptions and raise an HTTP 500 error
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    return {
        "status": "200",
        "message": "Blog post updated successfully",
        "data": {"post": jsonable_encoder(updated_blog_post)}
    }
