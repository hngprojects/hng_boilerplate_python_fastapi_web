from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogCreate
from api.v1.models.user import User


class BlogService:
    """Blog service functionality"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, db: Session, schema: BlogCreate, author_id: str):
        """Create a new blog post"""
        new_blogpost = Blog(**schema.model_dump(), author_id=author_id)
        db.add(new_blogpost)
        db.commit()
        db.refresh(new_blogpost)
        return new_blogpost

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all blog posts with option to search using query parameters"""
        query = db.query(Blog)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Blog, column) and value:
                    query = query.filter(getattr(Blog, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, blog_id: str):
        """Fetch a blog post by its ID"""
        blog_post = self.db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog_post:
            raise HTTPException(status_code=404, detail="Post not Found")
        return blog_post

    def update(
        self,
        blog_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        current_user: User = None,
    ):
        """Updates a blog post"""

        if not title or not content:
            raise HTTPException(
                status_code=400, detail="Title and content cannot be empty"
            )

        blog_post = self.fetch(blog_id)

        if blog_post.author_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this blog"
            )

        # Update the fields with the provided data
        blog_post.title = title
        blog_post.content = content

        try:
            self.db.commit()
            self.db.refresh(blog_post)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail="An error occurred while updating the blog post"
            )

        return blog_post
