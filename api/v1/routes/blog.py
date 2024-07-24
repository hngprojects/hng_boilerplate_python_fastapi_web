from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Annotated

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogResponse
from api.v1.services.user import user_service
from api.v1.models.blog_dislike import BlogDislike
from api.utils.dependencies import get_current_user

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
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status_code": f"{status.HTTP_401_UNAUTHORIZED}", 
                "message": "Could not validate credentials"
            }

        # GET blog post
        blog_p = db.query(Blog).filter_by(id=blog_id).first()
        if not blog_p:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status_code": f"{status.HTTP_404_NOT_FOUND}", 
                "message": "Blog post not found"
            }
        
        # CONFIRM current user has not disliked before
        if db.query(BlogDislike).filter_by(user_id=current_user.id, blog_id=blog_p.id).first():
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

