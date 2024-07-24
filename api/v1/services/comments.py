#!/usr/bin/env python3

"""Defines services for comments endpoints"""


from typing import Optional
from sqlalchemy.orm.session import Session
from api.core.base.services import Service
from api.v1.models.comment import Comment


class CommentService(Service):
    """Implements Comment services"""

    def create_comment(self, db: Session, *args, **kwargs) -> Comment:
        """Create a new comment"""
        comment = Comment(**kwargs)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    def update_comment(
        self,
        db: Session,
        id,
        user,
        **kwargs
    ) -> Optional[Comment]:
        """Update user comment"""
        comment: Optional[Comment] = db.query(
            Comment).filter_by(id=id).one_or_none()
        if not comment or user.id != comment.user_id:
            return None
        if isinstance(comment, Comment):
            comment.content = kwargs.get('content')
        db.commit()
        db.refresh(comment)
        return comment

    def create(self):
        """Create user comment"""
        pass

    def fetch(self):
        """Fetch user comment"""
        pass

    def delete(self):
        """Delete user comment"""
        pass

    def update(self):
        """update user comment"""
        pass

    def fetch_all(self):
        """Fetch all user comments"""
        pass


comment_service = CommentService()
