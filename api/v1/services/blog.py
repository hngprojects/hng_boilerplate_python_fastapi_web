from typing import Generic, TypeVar, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.blog import Blog, BlogDislike, BlogLike
from api.v1.models.comment import Comment
from api.v1.models.user import User
from api.v1.schemas.blog import BlogCreate

ModelType = TypeVar("ModelType")

class BaseBlogInteractionService(Generic[ModelType]):
    """Base service for blog interactions (likes/dislikes)"""
    
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def fetch(self, item_id: str) -> ModelType:
        """Generic fetch method for interaction models"""
        return check_model_existence(self.db, self.model, item_id)

    def delete(self, item_id: str, user_id: str) -> None:
        """Generic delete method with owner verification"""
        item = self.fetch(item_id)
        
        if item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Insufficient permission"
            )
            
        self.db.delete(item)
        self.db.commit()

class BlogService:
    """Blog service functionality"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, schema: BlogCreate, author_id: str):
        """Create a new blog post"""

        new_blogpost = Blog(**schema.model_dump(), author_id=author_id)
        self.db.add(new_blogpost)
        self.db.commit()
        self.db.refresh(new_blogpost)
        return new_blogpost

    def fetch_all(self):
        """Fetch all blog posts"""

        blogs = self.db.query(Blog).filter(Blog.is_deleted == False).all()
        return blogs

    def fetch(self, blog_id: str):
        """Fetch a blog post by its ID"""
        blog_post = self.db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog_post:
            raise HTTPException(status_code=404, detail="Post not found")
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

    def create_blog_like(self, blog_id: str, user_id: str, ip_address: str = None):
        """Create new blog like."""

        blog_like = BlogLike(blog_id=blog_id, user_id=user_id, ip_address=ip_address)
        self.db.add(blog_like)
        self.db.commit()
        self.db.refresh(blog_like)
        return blog_like

    def create_blog_dislike(self, blog_id: str, user_id: str, ip_address: str = None):
        """Create new blog dislike."""
        
        blog_dislike = BlogDislike(blog_id=blog_id, user_id=user_id, ip_address=ip_address)
        self.db.add(blog_dislike)
        self.db.commit()
        self.db.refresh(blog_dislike)
        return blog_dislike

    def fetch_blog_like(self, blog_id: str, user_id: str):
        """Fetch a blog like by blog ID & ID of user who liked it"""
        blog_like = (
            self.db.query(BlogLike)
            .filter_by(blog_id=blog_id, user_id=user_id)
            .first()
        )
        return blog_like

    def fetch_blog_dislike(self, blog_id: str, user_id: str):
        """Fetch a blog dislike by blog ID & ID of user who disliked it"""
        blog_dislike = (
            self.db.query(BlogDislike)
            .filter_by(blog_id=blog_id, user_id=user_id)
            .first()
        )
        return blog_dislike
    
    def check_user_already_liked_blog(self, blog: Blog, user: User):
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        existing_like = self.fetch_blog_like(blog.id, user.id)
        if isinstance(existing_like, BlogLike):
            raise HTTPException(
                detail="You have already liked this blog post",
                status_code=status.HTTP_403_FORBIDDEN,
            )

    def check_user_already_disliked_blog(self, blog: Blog, user: User):
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        existing_dislike = self.fetch_blog_dislike(blog.id, user.id)
        if isinstance(existing_dislike, BlogDislike):
            raise HTTPException(
                detail="You have already disliked this blog post",
                status_code=status.HTTP_403_FORBIDDEN,
            )
    
    def delete_opposite_blog_like_or_dislike(self, blog: Blog, user: User, creating: str):
        """
        This method checks if there's a BlogLike by `user` on `blog` when a BlogDislike 
        is being created and deletes the BlogLike. The same for BlogLike creation. \n

        :param blog: `Blog` The blog being liked or disliked
        :param user: `User` The user liking or disliking the blog
        :param creating: `str` The operation being performed by the user. One of "like", "dislike"
        """
        if creating == "like":
            existing_dislike = self.fetch_blog_dislike(blog.id, user.id)
            if existing_dislike:
                self.db.delete(existing_dislike)
                self.db.commit()  
        elif creating == "dislike":
            existing_like = self.fetch_blog_like(blog.id, user.id)
            if existing_like:
                self.db.delete(existing_like)
                self.db.commit() 
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid `creating` value for blog like/dislike"
            )

    def num_of_likes(self, blog_id: str) -> int:
        """Get the number of likes a blog post has"""
        return self.db.query(BlogLike).filter_by(blog_id=blog_id).count()

    def num_of_dislikes(self, blog_id: str) -> int:
        """Get the number of dislikes a blog post has"""
        return self.db.query(BlogDislike).filter_by(blog_id=blog_id).count()

    def delete(self, blog_id: str):
        post = self.fetch(blog_id=blog_id)

        if post:
            try:
                post.is_deleted = True
                self.db.commit()
                self.db.refresh(post)
            except Exception as e:
                self.db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="An error occurred while updating the blog post",
                )
    def fetch_and_increment_view(self, blog_id: str):
        """Fetch a blog post and increment its view count"""
        try:
            blog = self.fetch(blog_id)
            
            if isinstance(blog, dict):
                if "views" not in blog:
                    blog["views"] = 0
                blog["views"] += 1
                return blog
            else:
                blog.views = blog.views + 1 if blog.views else 1
                self.db.refresh(blog)
                self.db.commit()
                return blog
                
        except HTTPException as e:
            raise e
        except Exception as e:
            self.db.rollback()
            from api.utils.logger import logger
            logger.error(f"Error incrementing view count for blog {blog_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to increment view count: {str(e)}"
            )

    def update_blog_comment(
        self,
        blog_id: str,
        comment_id: str,
        content: Optional[str] = None,
        current_user: User = None,
    ):
        """Updates a blog comment

        Args:
            - blog_id: the blog ID
            - comment_id: the comment ID
            - content: the blog content to be updateed. Defaults to None.
            - current_user: the current authenticated user. Defaults to None.

        Raises:
            - HTTPException: 400 error if comment is null
            - HTTPException: 403 error if the current user_id is not the comment user_id
            - HTTPException: 500 error if the database operation fails

        Returns:
            dict: updated comment response
        """

        db = self.db

        if not content:
            raise HTTPException(
                status_code=400, detail="Blog comment cannot be empty"
            )

        # check if the blog and comment exist
        blog_post = check_model_existence(db, Blog, blog_id)

        comment = check_model_existence(db, Comment, comment_id)

        if comment.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to update this comment"
            )

        # Update the comment content
        comment.content = content

        try:
            db.commit()
            db.refresh(comment)
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"An error occurred while updating the blog comment; {exc}"
            )

        return comment


#BlogLikeService and BlogDislikeService inherits from baseclass BaseBlogInteractionService
class BlogLikeService(BaseBlogInteractionService[BlogLike]):
    """BlogLike service functionality"""

    def __init__(self, db: Session):
        super().__init__(db, BlogLike)
        


class BlogDislikeService(BaseBlogInteractionService[BlogDislike]):
    """BlogDislike service functionality"""

    def __init__(self, db: Session):
        super().__init__(db, BlogDislike)