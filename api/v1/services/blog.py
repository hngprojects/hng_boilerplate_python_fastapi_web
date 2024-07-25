from api.v1.models.user import User
from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.blog import Blog
from uuid import UUID
from fastapi import HTTPException


# class BlogService(Service):
#     '''Blog service functionality'''

#     def create(self, schema):
#         '''Create a new blog post'''

#     def fetch_all(self, **query_params: Optional[Any]):
#         '''Fetch all blog posts with option to search using query parameters'''

#     def fetch(self, db: Session, id: str):
#         return db.query(Blog).filter(Blog.id == id, Blog.is_deleted == False).first()

#     def update(self, db:Session, blog_id: str, title: Optional[str] = None, content: Optional[str] = None, current_user: User = None):
#         '''Updates a blog post'''
#         if not title or not content:
#             raise HTTPException(
#                 status_code=400, detail="Title and content cannot be empty")

#         blog_post = self.fetch(db, blog_id)

#         if blog_post.author_id != current_user.id:
#             raise HTTPException(
#                 status_code=403, detail="Not authorized to update this blog")

#         # Update the fields with the provided data
#         blog_post.title = title
#         blog_post.content = content

#         try:
#             self.db.commit()
#             self.db.refresh(blog_post)
#         except Exception as e:
#             self.db.rollback()
#             raise HTTPException(
#                 status_code=500, detail="An error occurred while updating the blog post")

#         return blog_post

#     def delete(self, db: Session, id: int):
#         '''Deletes a blog post'''


# # class BlogService:
# #     '''Blog service functionality'''

# #     def __init__(self, db: Session):
# #         self.db = db

# #     def fetch(self, blog_id: str):
# #         '''Fetch a blog post by its ID'''
# #         blog_post = self.db.query(Blog).filter(Blog.id == blog_id).first()
# #         if not blog_post:
# #             raise HTTPException(status_code=404, detail="Post not Found")
# #         return blog_post

# #     def update(self, blog_id: str, title: Optional[str] = None, content: Optional[str] = None, current_user: User = None):
# #         '''Updates a blog post'''


class BlogService:
    '''Blog service functionality'''

    def __init__(self, db: Session):
        self.db = db

    def fetch(self, blog_id: str):
        '''Fetch a blog post by its ID'''
        blog_post = self.db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog_post:
            raise HTTPException(status_code=404, detail="Post not Found")
        return blog_post

    def update(self, blog_id: str, title: Optional[str] = None, content: Optional[str] = None, current_user: User = None):
        '''Updates a blog post'''

        if not title or not content:
            raise HTTPException(
                status_code=400, detail="Title and content cannot be empty")

        blog_post = self.fetch(blog_id)

        if blog_post.author_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this blog")

        # Update the fields with the provided data
        blog_post.title = title
        blog_post.content = content

        try:
            self.db.commit()
            self.db.refresh(blog_post)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail="An error occurred while updating the blog post")

        return blog_post
