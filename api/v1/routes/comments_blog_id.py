from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from api.db.database import get_db
from api.v1.models.comment import Comment


router = APIRouter(prefix="/comments", tags=["Comment"])

@router.get("/comments/{blog_id}", response_model=List[Comment])
def get_comments(blog_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.blog_id == blog_id).all()
    if not comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    return comments
