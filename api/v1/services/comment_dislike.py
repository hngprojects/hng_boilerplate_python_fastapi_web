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
        """Function to dislike a comment"""
        # check if the user_id has disliked the comment, return error is so
        dislike_data = db.query(CommentDislike).filter_by(user_id=user_id, comment_id=comment_id).first()
        if dislike_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only dislike once",
            )
        # check if comment exists
        comment = check_model_existence(db, Comment, comment_id)

        # create and add the new commentDislike to the database
        new_dislike = CommentDislike(
            comment_id=comment_id, user_id=user_id, ip_address=client_ip
        )
        db.add(new_dislike)
        db.commit()
        db.refresh(new_dislike)
        return new_dislike

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
