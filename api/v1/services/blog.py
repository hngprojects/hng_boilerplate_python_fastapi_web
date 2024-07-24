from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.blog import Blog
from uuid import UUID
from fastapi import HTTPException


class BlogService(Service):
    '''Blog service functionality'''

    def create(self, db: Session, schema):
        '''Create a new blog post'''

        # new_blog = Blog(**schema.model_dump())
        # db.add(new_blog)
        # db.commit()
        # db.refresh(new_blog)

        # return new_blog

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all blog posts with option to search using query parameters'''

        # query = db.query(Blog)

        # # Enable filter by query parameter
        # if query_params:
        #     for column, value in query_params.items():
        #         if hasattr(Blog, column) and value:
        #             query = query.filter(
        #                 getattr(Blog, column).ilike(f'%{value}%'))

        # return query.all()

    def fetch(self, db: Session, id: UUID):
        # Assuming you are using a SQLAlchemy query to fetch the blog
        blog = db.query(Blog).filter(Blog.id == id).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return blog

    def update(self, db: Session, id: int, schema):
        '''Updates a blog post'''

        # blog = self.fetch(db, id=id)

        # # Update the fields with the provided schema data
        # update_data = schema.dict(exclude_unset=True)
        # for key, value in update_data.items():
        #     setattr(blog, key, value)

        # db.commit()
        # db.refresh(blog)
        # return blog

    def delete(self, db: Session, id: int):
        '''Deletes a blog post'''

        # blog = self.fetch(db, id=id)
        # db.delete(blog)
        # db.commit()
