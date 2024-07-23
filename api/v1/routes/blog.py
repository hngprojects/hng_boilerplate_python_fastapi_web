from fastapi import APIRouter, Depends, Security, HTTPException, Query
from sqlalchemy.orm import Session
from api.db.database import get_db
from .auth import get_current_admin
from api.v1.models.user import User
from api.v1.schemas.blog import BlogCreate
from api.v1.models.blog import Blog

blog = APIRouter()




@blog.post("/api/v1/blogs")
def create_blog(blog: BlogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not Authorized")
    db_blog = Blog(
            author_id = current_user.id,
            title = blog.title,
            content = blog.content,
            image_url = blog.image_url,
            tags = blog.tags,
            excerpt = blog.excerpt)
    
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return {
        "message": "Post Created Successfully!",
        "status_code": 200,
        "data": db_blog
}


   
