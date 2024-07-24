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

        

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all blog posts with option to search using query parameters'''

        
    def fetch(self, db: Session, id: str):
            return db.query(Blog).filter(Blog.id == id, Blog.is_deleted == False).first()

    def update(self, db: Session, id: int, schema):
        '''Updates a blog post'''

        

    def delete(self, db: Session, id: int):
        '''Deletes a blog post'''

        
