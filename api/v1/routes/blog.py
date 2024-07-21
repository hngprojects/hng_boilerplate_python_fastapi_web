from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.blog import Blog
from api.v1.schemas.blog import DeleteBlogResponseSchema
from api.utils.dependencies import get_current_admin
import logging
import uuid


blog = APIRouter(prefix="/api/v1/blogs", tags=["Blogs"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_uuid(id: str):
    try:
        uuid.UUID(id)
        return True
    except ValueError:
        return False


@blog.delete("/{id}", response_model=DeleteBlogResponseSchema)
async def delete_blog(id: str, db: Session = Depends(get_db), user: str = Depends(get_current_admin)):
    if not validate_uuid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID format")
    try:
        blog_data = db.query(Blog).filter(
            Blog.id == id, Blog.is_deleted == False).first()
        if db.query(Blog).filter(
                Blog.id == id, Blog.is_deleted == True).first():
            logger.warning(f"Blog already deleted.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Blog not active")
        if blog_data is None:
            logger.warning(f"Blog post with ID '{id}' not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Blog with the given Id does not exist")

        blog_data.is_deleted = True
        db.commit()

        return {"message": "Blog successfully deleted", "status_code": 202}
    except HTTPException as e:
        logger.error(f"HTTP exception: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
