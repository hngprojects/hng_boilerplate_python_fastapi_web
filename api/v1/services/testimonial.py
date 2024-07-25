from typing import Any, Optional
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.testimonial import Testimonial


class TestimonialService(Service):
    '''Product service functionality'''

    def create(self, db: Session,  schema):
        '''Create testimonial'''
        pass
    

    def fetch_all(self, db: Session):
        '''Fetch all testimonial'''
        pass

    
    def fetch(self, db: Session, id: str):
        '''Fetches a single testimonial id'''

        return check_model_existence(db, Testimonial, id)
    

    def update(self, db: Session, id: str, schema):
        '''Updates a testimonial'''
        pass
    

    def delete(self, db: Session, id: str):
        '''Deletes a specific testimonial'''
        pass

testimonial_service = TestimonialService()