from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogResponse
from api.db.database import get_db

blog = APIRouter(prefix="/blogs", tags=["Blog"])

@blog.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.is_deleted == False).all()
    if not blogs:
        return []
    return blogs

