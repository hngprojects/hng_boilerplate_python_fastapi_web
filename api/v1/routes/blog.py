from fastapi import APIRouter, Depends, Security, HTTPException, Query
from sqlalchemy.orm import Session
from api.db.database import get_db
from .auth import get_current_admin
from api.v1.models.user import User
from api.v1.schemas.blog import BlogCreate
from api.v1.models.blog import Blog
from api.v1.services.blog import BlogService

blog = APIRouter()
blog_service = BlogService()



@blog.post("/api/v1/blogs")
def create_blog(blog: BlogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not Authorized")
    
    new_blogpost = blog_service.create(db=db, schema=blog, author_id=current_user.id)

    return {
        "message": "Post Created Successfully!",
        "status_code": 200,
        "data": new_blogpost
}


   
