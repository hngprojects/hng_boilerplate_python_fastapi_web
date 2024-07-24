from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogResponse, BlogPostResponse
from api.db.database import get_db
from api.v1.services.blog import BlogService

blog = APIRouter(prefix="/blogs", tags=["Blog"])
blog_service = BlogService()


@blog.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.is_deleted == False).all()
    if not blogs:
        return []
    return blogs


@blog.get("/{id}", response_model=BlogPostResponse)
def get_blog_by_id(id: str, db: Session = Depends(get_db)):
    blog_post = blog_service.fetch(db, id)
    if not blog_post:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Blog post not found."
            }
        )

    return blog_post
