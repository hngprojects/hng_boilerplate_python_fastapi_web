from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from api.v1.models import User
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogResponse, DeleteBlogResponse

blogs = APIRouter(prefix="/blogs", tags=["Blog"])
blog = APIRouter(prefix="/blog", tags=["Blog"])

@blogs.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.is_deleted == False).all()
    if not blogs:
        return []
    return blogs


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
