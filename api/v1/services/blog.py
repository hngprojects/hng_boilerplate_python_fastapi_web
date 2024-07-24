from typing import Any, Optional
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogCreate, BlogUpdate

class BlogService(Service):
    '''Blog service functionality'''

    def create(self, db: Session, schema: BlogCreate, author_id: str):
        '''Create a new blog post'''
        new_blogpost = Blog(**schema.model_dump(), author_id=author_id)
        db.add(new_blogpost)
        db.commit()
        db.refresh(new_blogpost)
        return new_blogpost

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all blog posts with option to search using query parameters'''
        query = db.query(Blog)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Blog, column) and value:
                    query = query.filter(getattr(Blog, column).ilike(f'%{value}%'))

        return query.all()

    def fetch(self, db: Session, id: int):
        '''Fetch a blog post by its id'''
        blog_post = check_model_existence(db, Blog, id)
        return blog_post

    def update(self, db: Session, id: int, schema: BlogUpdate):
        '''Update a blog post'''
        blog_post = self.fetch(db=db, id=id)
        
        # Update the fields with the provided schema data
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(blog_post, key, value)
        
        db.commit()
        db.refresh(blog_post)
        return blog_post

    def delete(self, db: Session, id: int):
        '''Delete a blog post'''
        blog_post = self.fetch(db=db, id=id)
        db.delete(blog_post)
        db.commit()
