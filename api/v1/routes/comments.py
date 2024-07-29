#!/usr/bin/env python3

"""Defines endpoints for comments"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm.session import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.comments import Comment, CommentResponse, UpdateComment
from api.v1.services.comments import comment_service
from api.v1.services.user import user_service


comment = APIRouter(prefix='/comments', tags=['Comments'])


@comment.patch(
    '/edit/{comment_id}',
    status_code=status.HTTP_200_OK,
    response_model=CommentResponse
)
async def update_comment(
        comment_id: Annotated[str, Path(description="The comment ID")],
        user: Annotated[User, Depends(user_service.get_current_user)],
        db: Annotated[Session, Depends(get_db)],
        request: UpdateComment
):
    """Endpoint to update a comment"""
    comment = comment_service.update_comment(
        db, comment_id, user, **dict(request))

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return CommentResponse(
        success=True,
        status_code=200,
        message="Comment fetch successfully",
        data=Comment(
            id=str(comment.id),
            content=str(comment.content),
            created_at=str(comment.created_at),
            updated_at=str(comment.updated_at),
            user=comment.user.to_dict() if comment.user else None
        )
    )
