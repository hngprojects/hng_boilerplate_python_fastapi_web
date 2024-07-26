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
    
    def get_paginated_testimonials(self, db: Session, page: int, per_page: int):
        # Calculate start and end points for pagination
        start = (page - 1) * per_page
        end = start + per_page

        # Retrieve testimonials from database
        testimonials = db.query(Testimonial).all()

        # Total testimonials pages
        total_pages = (len(testimonials) + per_page - 1) // per_page
        # Total testimonials
        total_testimonial = len(testimonials)

        # Get needed data only
        paginated_testimonials = testimonials[start:end]

        return paginated_testimonials, total_testimonial, total_pages

    def delete_all(self, db: Session):
        '''Delete all testimonials'''
        try:
            db.query(Testimonial).delete()
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
 
testimonial_service = TestimonialService()