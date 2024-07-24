from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.v1.models.blog import Blog
from api.v1.models.user import User
from uuid import UUID

def blogUpdateService(blog_id: UUID, title: str, content: str, db: Session, current_user: User):
    if not title or not content:
        raise HTTPException(status_code=400, detail="Title and content cannot be empty")
    
    blog_post = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog_post:
        raise HTTPException(status_code=404, detail="Post not Found")
    
    if blog_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this blog")

    blog_post.title = title
    blog_post.content = content

    try:
        db.commit()
        db.refresh(blog_post)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the blog post")
    
    return blog_post
