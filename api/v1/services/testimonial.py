from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.testimonial import Testimonial
from api.v1.models.user import User
from api.v1.schemas.testimonial import CreateTestimonial
from fastapi import HTTPException, status
from sqlalchemy import desc


class TestimonialService(Service):
    """Product service functionality"""

    def create(self, db: Session,  user: User, data: CreateTestimonial):
        '''Create testimonial'''
        new_testimonial = Testimonial(
            content=data.content,
            ratings=data.ratings,
            author_id=user.id
        )
        db.add(new_testimonial)
        db.commit()
        db.refresh(new_testimonial)
        return new_testimonial


    def fetch_all(self, page :int , page_size : int, db: Session):
        '''Fetch all testimonial with pagination'''
        offset = (page - 1) * page_size
        testimonials = db.query(Testimonial).offset(offset).limit(page_size).all()

        return testimonials

    def fetch(self, db: Session, id: str):
        """Fetches a single testimonial id"""

        return check_model_existence(db, Testimonial, id)

    def update(self, db: Session, id: str, schema):
        """Updates a testimonial"""
        pass

    def delete(self, db: Session, id: str):
        """Deletes a specific testimonial"""

        testimonial = check_model_existence(db, Testimonial, id)

        db.delete(testimonial)
        db.commit()

    def delete_all(self, db: Session):
        """Delete all testimonials"""
        try:
            db.query(Testimonial).delete()
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
    
    def top_rated_testimonials(self, db: Session, page: int = 1, per_page: int = 10):
        """
        Fetch testimonials with the highest ratings and paginates the results.
        """
        if page < 1 or per_page < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")

        offset = (page - 1) * per_page
    
        testimonials = (
            db.query(Testimonial)
            .order_by(desc(Testimonial.ratings))
            .offset(offset)
            .limit(per_page)
            .all()
        )

        return testimonials


testimonial_service = TestimonialService()
