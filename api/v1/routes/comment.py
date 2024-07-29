from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas.comment import UpdateCommentRequest, UpdateCommentResponse
from api.v1.services.comment import CommentService
from api.db.database import get_db
from api.v1.services.user import UserService

comment = APIRouter(prefix="/comment", tags=["comment"])

@comment.put("/comments/{comment_id}/", response_model=UpdateCommentResponse)
async def update_comment(comment_id: str, request: UpdateCommentRequest, db: Session = Depends(get_db), current_user=Depends(UserService.get_current_user)):
    return await CommentService.update_comment(db, comment_id, request, current_user.id)
