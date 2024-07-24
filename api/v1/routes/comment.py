from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status
    )
from sqlalchemy.orm import Session
from api.core import responses
from api.utils.json_response import JsonResponseDict
from api.v1.models.comment import Comment
from api.v1.schemas.comment import CommentResponse
from api.v1.services.comment import comment_service
from api.db.database import get_db


comment = APIRouter(prefix="/comments", tags=['Comment'])


@comment.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: str, db: Session = Depends(get_db)):
    comment = comment_service.fetch(db=db, id=comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail=responses.NOT_FOUND)
    return JsonResponseDict(
        message="<message>",
        data={"comment": comment.to_dict()},
        status_code=status.HTTP_200_OK
    )