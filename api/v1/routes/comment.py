from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas.comment import UpdateCommentRequest, UpdateCommentResponse
from api.v1.services.comment import CommentService
from api.db.database import get_db
from api.v1.services.user import UserService
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Header
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.comment_like import comment_like_service
from api.v1.services.user import user_service
from api.v1.schemas.comment import DislikeSuccessResponse, CommentDislike, LikeSuccessResponse
from api.v1.services.comment_dislike import comment_dislike_service

comment = APIRouter(prefix="/comments", tags=["Comment"])

@comment.post("/{comment_id}/like", response_model=LikeSuccessResponse)
async def like_comment(
        comment_id: str, 
        request: Request,
        x_forwarded_for: str = Header(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(user_service.get_current_user)
    ) -> Response:
    """
    Description
        Post endpoint for authenticated users to like a comment.

    Args:
        request: the request object 
        comment_id (str): the id of the comment to like
        current_user: the current authenticated user 
        db: the database session object

    Returns:
        Response: a response object containing details if successful or appropriate errors if not
    """	
    user_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.client.host	
    like = comment_like_service.create(db=db,comment_id=comment_id,user_id=current_user.id,client_ip=user_ip)
    return success_response(
        message = "Comment liked successfully!",
        status_code = 201,
        data = jsonable_encoder(like)
    )

@comment.put("/{comment_id}/", response_model=UpdateCommentResponse)
async def update_comment(comment_id: str, request: UpdateCommentRequest, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    return CommentService.update_comment(db, comment_id, request, current_user.id)



@comment.post("/{comment_id}/dislike", response_model=DislikeSuccessResponse)
async def dislike_comment(
    request: Request,
    comment_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    db: Annotated[Session, Depends(get_db)]
    ) -> Response:
    """
    Post endpoint for authenticated users to dislike a comment.
    """
    user_id = current_user.id
    client_ip = request.headers.get("X-Forwarded-For") or request.client.host

    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip is None or client_ip == "":
        client_ip = request.client.host

    dislike = comment_dislike_service.create(
        db=db, user_id=user_id, comment_id=comment_id, client_ip=client_ip
        )

    return success_response(
        message="Comment disliked successfully!",
        status_code=201,
        data=jsonable_encoder(dislike)
    )
