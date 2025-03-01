from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models import Comment, CommentDislike


class CommentDislikeService(Service):
    """Comment dislike service functionality"""

    def create(self, db: Session, user_id: str, comment_id: str, client_ip: Optional[str] = None) -> dict:
        """Function to dislike a comment"""
        # Check if the user has already disliked the comment.
        existing_dislike = (
            db.query(CommentDislike)
            .filter_by(user_id=user_id, comment_id=comment_id)
            .first()
        )
        if existing_dislike:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only dislike once",
            )
        # Verify that the comment exists.
        comment = check_model_existence(db, Comment, comment_id)

        # Create and add the new comment dislike to the database.
        new_dislike = CommentDislike(
            comment_id=comment_id, user_id=user_id, ip_address=client_ip
        )
        db.add(new_dislike)
        db.commit()
        db.refresh(new_dislike)
        # Return a consistent response structure.
        return {"message": "Comment disliked successfully!", "data": new_dislike}

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all comment dislikes with optional query parameters for filtering."""
        query = db.query(CommentDislike)
        if query_params:
            for column, value in query_params.items():
                if hasattr(CommentDislike, column) and value:
                    query = query.filter(getattr(CommentDislike, column).ilike(f"%{value}%"))
        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetch a comment dislike by id."""
        comment_dislike = check_model_existence(db, CommentDislike, id)
        return comment_dislike

    def update(self, db: Session, id: str, schema):
        """Update a comment dislike."""
        comment_dislike = self.fetch(db=db, id=id)
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(comment_dislike, key, value)
        db.commit()
        db.refresh(comment_dislike)
        return {"message": "Comment dislike updated successfully!", "data": comment_dislike}

    def delete(self, db: Session, id: str):
        """Delete a comment dislike."""
        comment_dislike = self.fetch(db=db, id=id)
        db.delete(comment_dislike)
        db.commit()
        return {"message": "Comment dislike deleted successfully!"}


comment_dislike_service = CommentDislikeService()




