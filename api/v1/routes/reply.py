from api.v1.models.reply import Reply
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status
from api.db.database import get_db
from api.v1.schemas.reply import ReplyCreate
from sqlalchemy.orm import Session
from api.v1.services.reply import ReplyService
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.utils.success_response import success_response


reply_router = APIRouter(prefix='/comments', tags=['comments_reply'])

@reply_router.post('/{comment_id}/reply', response_model=success_response, status_code=status.HTTP_201_CREATED)
async def reply_to_a_comment(comment_id: str, reply: ReplyCreate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """
    """
    # calling current user just to ensure user is validated
    current_user
    
    new_reply = ReplyService.create(db=db, schema=reply, comment_id=comment_id)
    
    # Possible Python Bug Alert!
    # for some reason, the below line is needed to enable data to be included in response
    print(new_reply)
    
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message='Reply added successfully',
        data=jsonable_encoder(new_reply),
    )