from fastapi import APIRouter, Depends, Request, Header
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.comment import comment_service
from api.v1.services.user import user_service

comment = APIRouter(prefix="/comments", tags=["Comment"])

@comment.post("/{comment_id}/like")
def like_comment(
        comment_id: str, 
        request: Request,
        x_forwarded_for: str = Header(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(user_service.get_current_user)
    ):
    """
    Like a comment on a blog.
    """	
    user_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.client.host	
    like = comment_service.like(db=db,comment_id=comment_id,user_id=current_user.id,user_ip=user_ip)
    return success_response(
        message = "Comment liked successfully!",
        status_code = 201,
        data = jsonable_encoder(like.to_dict())
    )