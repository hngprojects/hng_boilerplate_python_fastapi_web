from api.v1.models.reply import Reply
from fastapi import APIRouter
from api.db.database import get_db
from api.v1.schemas.reply import ReplyCreate

reply_router = APIRouter(prefix='/comments', tags=['comments_reply'])

@reply_router.post('/{comment_id}/reply', status_code=200)
async def reply_to_a_comment(comment_id: str, reply: ReplyCreate):
    """
    """
    pass