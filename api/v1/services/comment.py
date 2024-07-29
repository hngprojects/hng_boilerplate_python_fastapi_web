# api/v1/services/comment.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.v1.models.comment import Comment
from api.v1.schemas.comment import UpdateCommentRequest, UpdateCommentResponse

class CommentService:
    @staticmethod
    def update_comment(db: Session, comment_id: str, data: UpdateCommentRequest, user_id: str):
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found.")
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to update this comment.")
        comment.content = data.content
        db.commit()
        db.refresh(comment)
        return UpdateCommentResponse(
            status="success",
            message="Comment updated successfully.",
            status_code=200,
            data={"comment_id": comment.id, "content": comment.content, "updated_at": comment.updated_at}
        )
