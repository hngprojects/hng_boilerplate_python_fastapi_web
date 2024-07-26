from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.services.user import user_service
from api.v1.models.blog_dislike import BlogDislike
from api.v1.schemas.blog import BlogUpdateResponseModel, BlogRequest, BlogResponse, BlogPostResponse
from api.v1.services.blog import BlogService
from api.utils.dependencies import get_current_user
from api.db.database import get_db

blog = APIRouter(prefix="/blogs", tags=["Blog"])


@blog.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):

    blogs = db.query(Blog).filter(Blog.is_deleted == False).all()
    if not blogs:
        return []
    return blogs


@blog.put("/{blog_id}/dislike")
def dislike_blog_post(blog_id: str,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
    ):
    
    try:
        if not current_user:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {
                "status_code": f"{status.HTTP_401_UNAUTHORIZED}", 
                "message": "Could not validate credentials"
            }

        # GET blog post
        blog_p = db.query(Blog).filter(Blog.id == blog_id).first()
        if not isinstance(blog_p, Blog):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status_code": f"{status.HTTP_404_NOT_FOUND}", 
                "message": "Blog post not found"
            }
        
        # CONFIRM current user has NOT disliked before
        blog_dislike = db.query(BlogDislike).filter_by(user_id=current_user.id, blog_id=blog_p.id).first()
        if isinstance(blog_dislike, BlogDislike):
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                "status_code": f"{status.HTTP_403_FORBIDDEN}", 
                "message": "You have already disliked this blog post"
            }

        # UPDATE disikes
        dislike = BlogDislike(
            user_id=current_user.id,
            blog_id=blog_p.id,
        )
        db.add(dislike)
        db.commit()
        db.refresh(dislike)

        # Return success response
        response.status_code = status.HTTP_200_OK
        return {
            "status_code": f"{status.HTTP_200_OK}", 
            "message": "Dislike recorded successfully."
        }
    except HTTPException:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status_code": f"{status.HTTP_400_BAD_REQUEST}", 
            "message": "Unable to record dislike."
        }


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
