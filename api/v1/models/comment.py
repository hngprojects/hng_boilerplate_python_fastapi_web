from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Comment(BaseTableModel):
    __tablename__ = "comments"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blog_id = Column(String, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="comments")
    blog = relationship("Blog", back_populates="comments")
    likes = relationship(
        "CommentLike", back_populates="comment", cascade="all, delete-orphan"
    )
    dislikes = relationship(
        "CommentDislike", back_populates="comment", cascade="all, delete-orphan"
    )


class CommentLike(BaseTableModel):
    __tablename__ = "comment_likes"

    comment_id = Column(
        String, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=True)

    comment = relationship("Comment", back_populates="likes")
    user = relationship("User", back_populates="comment_likes")


class CommentDislike(BaseTableModel):
    __tablename__ = "comment_dislikes"

    comment_id = Column(
        String, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=True)

    comment = relationship("Comment", back_populates="dislikes")
    user = relationship("User", back_populates="comment_dislikes")
