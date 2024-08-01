from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Header
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.comment_like import comment_like_service
from api.v1.services.user import user_service
from api.v1.schemas.comment import (
    DislikeSuccessResponse,
    CommentDislike,
    LikeSuccessResponse,
)
from api.v1.services.comment_dislike import comment_dislike_service
from api.v1.services.comment import comment_service
from api.utils.json_response import JsonResponseDict
from uuid import UUID

comment = APIRouter(prefix="/comments", tags=["Comment"])


@comment.post("/{comment_id}/like", response_model=LikeSuccessResponse)
async def like_comment(
    comment_id: str,
    request: Request,
    x_forwarded_for: str = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
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
    user_ip = (
        x_forwarded_for.split(",")[0].strip()
        if x_forwarded_for
        else request.client.host
    )
    like = comment_like_service.create(
        db=db, comment_id=comment_id, user_id=current_user.id, client_ip=user_ip
    )
    return success_response(
        message="Comment liked successfully!",
        status_code=201,
        data=jsonable_encoder(like),
    )

@comment.post("/{comment_id}/dislike", response_model=DislikeSuccessResponse)
async def dislike_comment(
    request: Request,
    comment_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Post endpoint for authenticated users to dislike a comment.

    Args:
        request: the request object
        comment_id (str): the id of the comment to dislike
        current_user: the current authenticated user
        db: the database session object

    Returns:
        Response: a response object containing details if successful or appropriate errors if not
    """

    user_id = current_user.id

    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip is None or client_ip == "":
        client_ip = request.client.host

    dislike = comment_dislike_service.create(
        db=db, user_id=user_id, comment_id=comment_id, client_ip=client_ip
    )

    return success_response(
        message="Comment disliked successfully!",
        status_code=201,
        data=jsonable_encoder(dislike),
    )

@comment.delete("/{comment_id}", response_model=None)
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
) -> JsonResponseDict:
    try:
        # Validate comment_id as a UUID
        try:
            comment_uuid = UUID(comment_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An invalid request was sent."
            )
        
        # Fetch the comment
        comment = comment_service.fetch(db=db, id=str(comment_uuid))
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment does not exist"
            )
        
        # Check if the current user is the owner of the comment
        if comment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access."
            )

        # Perform the deletion
        comment_service.delete(db=db, id=str(comment_uuid))
        return JsonResponseDict(
            message="Comment deleted successfully.",
            status_code=status.HTTP_200_OK
        )
    except HTTPException as e:
        return JsonResponseDict(
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return JsonResponseDict(
            message="Internal server error.",
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
