from sqlalchemy.orm import Session
from api.v1.schemas import testimonial_schema
from api.v1.models import testimonial


def create_testimonial(db: Session, testimonial_create: testimonial_schema.TestimonialCreate, author_id: str):
    db_testimonial = testimonial.Testimonial(
        content=testimonial_create.content,
        client_designation=testimonial_create.client_designation,
        client_name=testimonial_create.client_name,
        ratings=testimonial_create.ratings,
        author_id=author_id
    )
    db.add(db_testimonial)
    db.commit()
    db.refresh(db_testimonial)
    return db_testimonial
