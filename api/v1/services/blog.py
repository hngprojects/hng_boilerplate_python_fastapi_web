from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from api.v1.models.blog import Blog
from api.v1.models.blog_like import BlogLike


class BlogService:
    def __init__(self, db: Session):
        self.db = db

    async def like_blog_service(self, blog_id: UUID, request: Request, current_user):
        """
        Service to handle liking a blog post.
        """
        # Validate the blog ID
        blog_post = self.db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found.")

        # Check if the user has already liked the blog post
        blog_like = self.db.query(BlogLike).filter(BlogLike.blog_id == str(blog_id),
                                                   BlogLike.user_id == str(current_user.id)).first()
        if blog_like:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have already liked this blog post.")

        # Record the like and audit trail
        new_blog_like = BlogLike(
            blog_id=str(blog_id),
            user_id=str(current_user.id),
            ip_address=request.client.host
        )
        self.db.add(new_blog_like)

        # Update the like count in the blog post
        blog_post.like_count += 1
        self.db.commit()

        return {"status_code": status.HTTP_200_OK, "message": "Like recorded successfully."}
