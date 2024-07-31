from api.v1.models.reply import Reply
from fastapi import APIRouter

reply_router = APIRouter('/comments', tags=['comments_reply'])

@reply_router.post('/<string:comment_id>/reply', status_code=200)
async def reply_to_a_comment():
    """
    """
    pass