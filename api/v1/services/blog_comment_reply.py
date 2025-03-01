from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from api.v1.models.comment import Comment, Reply
from api.v1.schemas.comment import ReplyCreate
from api.utils.db_validators import check_model_existence


class ReplyService:
    """Handles reply creation for blog comments"""

    @staticmethod
    def create(db: Session, schema: ReplyCreate, user_id: str, comment_id: str):
        """Create a new reply to a blog comment"""

        # Validate comment existence
        comment = check_model_existence(db, Comment, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found."
            )

        # Prevent empty replies
        if not schema.content.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Reply content cannot be empty."
            )

        # Create and store the reply
        try:
            new_reply = Reply(**schema.model_dump(), user_id=user_id, comment_id=comment_id)
            db.add(new_reply)
            db.commit()
            db.refresh(new_reply)
            return new_reply
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create reply: {str(e)}"
            ) from e


reply_service = ReplyService()
