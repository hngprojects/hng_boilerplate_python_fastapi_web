from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.dependencies import get_current_user, get_super_admin
from api.v1.models.blog import Blog
from api.v1.models.user import User
from api.v1.schemas.blog import (BlogRequest, BlogResponse,
                                 BlogUpdateResponseModel)
from api.v1.services.blog import BlogService

blogs = APIRouter(prefix="/blogs", tags=["Blog"])
blog = APIRouter(prefix="/blog", tags=["Blog"])

@blogs.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.is_deleted == False).all()
    if not blogs:
        return []
    return blogs

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
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    return {
        "status": "200",
        "message": "Blog post updated successfully",
        "data": {"post": jsonable_encoder(updated_blog_post)}
    }
@blog.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_blog(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_super_admin)):
    if not current_user:
        return {"status_code":403, "message":"Unauthorized User"}
    post = db.query(Blog).filter_by(Blog.id == id, Blog.is_deleted == False).first()
    
    if not  post:
        return {"status_code":status.HTTP_404_NOT_FOUND, "message": "Blog with the given ID does not exist"}
    
    post.is_deleted = True
    # db.delete(post)
    db.commit()
    
    return {"message": "Blog post deleted successfully", "status_code": 200}
