from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List

from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogUpdateResponseModel, BlogRequest, BlogResponse, BlogPostResponse
from api.v1.services.blog import BlogService
from api.utils.dependencies import get_current_user
from api.db.database import get_db
from api.v1.models.user import User

blog = APIRouter(prefix="/blogs", tags=["Blog"])


@blog.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):

    blogs = db.query(Blog).filter(Blog.is_deleted == False).all()
    if not blogs:
        return []
    return blogs


@blog.get("/{id}", response_model=BlogPostResponse)
def get_blog_by_id(id: str, db: Session = Depends(get_db)):
    """
    Retrieve a blog post by its Id.

    Args:
        id (str): The ID of the blog post.
        db (Session): The database session.

    Returns:
        BlogPostResponse: The blog post data.

    Raises:
        HTTPException: If the blog post is not found.
    """
    blog_service = BlogService(db)

    blog_post = blog_service.fetch(id)
    if not blog_post:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Post not Found"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "status_code": status.HTTP_200_OK,
            "message": "Blog post retrieved successfully",
            "data": jsonable_encoder(blog_post)
        }
    )


@blog.put("/{id}", response_model=BlogUpdateResponseModel)
async def update_blog(id: str, blogPost: BlogRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog_service = BlogService(db)
    try:
        updated_blog_post = blog_service.update(
            blog_id=id,
            title=blogPost.title,
            content=blogPost.content,
            current_user=current_user
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        # Catch any other exceptions and raise an HTTP 500 error
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred")

    return {
        "status": "200",
        "message": "Blog post updated successfully",
        "data": {"post": jsonable_encoder(updated_blog_post)}
    }
