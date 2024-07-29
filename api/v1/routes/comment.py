from typing import Annotated

from fastapi import (APIRouter, Depends, HTTPException, Path, Request,
                     Response, status)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.comment import (Comment, CommentDislike, CommentResponse,
                                    DislikeSuccessResponse, UpdateComment)
from api.v1.services.comment import comment_service
from api.v1.services.comment_dislike import comment_dislike_service
from api.v1.services.user import user_service

comment = APIRouter(prefix="/comments", tags=["Comments"])


@comment.post("/{comment_id}/dislike", response_model=DislikeSuccessResponse)
async def dislike_comment(
    request: Request,
    comment_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> Response:
    """Post endpoint for authenticated users to dislike a comment.

    Args:
        request: the request object
        comment_id (str): the id of the comment to dislike
        current_user: the current authenticated user
        db: the database session object

    Returns:
        Response: a response object containing details if successful or
        appropriate errors if not
    """

    user_id = current_user.id

    client_ip = request.headers.get("X-Forwarded-For")
    # check if none and return Request.client.host instead
    if client_ip is None or client_ip == "":
        client_ip = request.client.host

    # create the dislike using the create method in comment_dislike_service
    dislike = comment_dislike_service.create(
        db=db, user_id=user_id, comment_id=comment_id, client_ip=client_ip
    )

    return success_response(
        message="Comment disliked successfully!",
        status_code=201,
        data=jsonable_encoder(dislike)
    )


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
        message="Comment updated successfully",
        data=Comment(
            id=str(comment.id),
            content=str(comment.content),
            created_at=str(comment.created_at),
            updated_at=str(comment.updated_at),
            user=comment.user.to_dict() if comment.user else None
        )
    )
