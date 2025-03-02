from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models import Comment, CommentDislike
from api.v1.models.comment import Comment


class CommentDislikeService(Service):
    """Comment dislike service functionality"""

    def create(self, db: Session, user_id, comment_id, client_ip: Optional[str] = None):
        """
            Function to dislike a comment
            Toggles dislike on a comment (adds or removes dislike).
        """
        # Ensure the comment exists before proceeding
        comment = check_model_existence(db, Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

        # Check if the user has already disliked the comment
        existing_dislike = db.query(CommentDislike).filter_by(user_id=user_id, comment_id=comment_id).first()

        try:
            if existing_dislike:
                db.delete(existing_dislike)
                db.commit()
                return {"message": "Dislike removed successfully"}
            else:
                new_dislike = CommentDislike(
                    comment_id=comment_id,
                    user_id=user_id,
                    ip_address=client_ip
                )
                db.add(new_dislike)
                db.commit()
                db.refresh(new_dislike)
                return {"message": "Dislike added successfully"}

        except Exception:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed.")

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all comment_dislike with option tto search using query parameters"""

        query = db.query(CommentDislike)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(CommentDislike, column) and value:
                    query = query.filter(
                        getattr(CommentDislike, column).ilike(f"%{value}%")
                    )

        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a comment_dislike by id"""

        comment_dislike = check_model_existence(db, CommentDislike, id)
        return comment_dislike

    def update(self, db: Session, id: str, schema):
        """Updates a comment_dislike"""

        comment_dislike = self.fetch(db=db, id=id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(comment_dislike, key, value)

        db.commit()
        db.refresh(comment_dislike)
        return comment_dislike

    def delete(self, db: Session, id: str):
        """Deletes a comment"""

        comment = self.fetch(id=id)
        db.delete(comment)
        db.commit()


comment_dislike_service = CommentDislikeService()
