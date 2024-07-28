from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.comment import CommentCreate, CommentSuccessResponse
from api.v1.services.comment import comment_service 
from api.v1.services.user import user_service

comment = APIRouter(prefix="/comments", tags=["Comments"])

@comment.post("/{blog_id}", response_model=CommentSuccessResponse)
def add_comment(
    blog_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    comment: CommentCreate, 
    db: Annotated[Session, Depends(get_db)]
    ):

    if not blog_id:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request, blog id required")
    
    user_id = current_user.id
    new_comment = comment_service.create(db=db, schema=comment, user_id=user_id, blog_id=blog_id)

    return success_response(
        message = "Comment added successfully!",
        status_code = 201,
        data = jsonable_encoder(new_comment)
    )