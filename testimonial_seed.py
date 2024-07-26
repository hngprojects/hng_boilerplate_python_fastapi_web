#!/usr/bin/env python3
""" Populates the database with seed data for testimonials
"""
import uuid
from api.v1.models import *
from api.v1.models.base import Base
from api.v1.services.user import user_service
from api.db.database import create_database, get_db
from sqlalchemy.orm import Session

# Uncomment if you need to create the database
# create_database()

db: Session = next(get_db())

# Create a user to associate with testimonials
user = User(
    email="testimonial_user@mail.com",
    username="testimonial_user",
    password=user_service.hash_password("securepassword"),
    first_name="Test",
    last_name="User"
)

db.add(user)
db.commit()

# Create testimonials using the user's ID
testimonials = [
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="Manager",
        client_name="Alice Johnson",
        author_id=user.id,
        comments="Great service!",
        content="The service was excellent and met all my expectations.",
        ratings=4.5
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="Director",
        client_name="Bob Smith",
        author_id=user.id,
        comments="Satisfied with the results",
        content="I am very satisfied with the results of the project.",
        ratings=4.7
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="CEO",
        client_name="Charlie Brown",
        author_id=user.id,
        comments="Exceeded expectations",
        content="The team exceeded my expectations in every way.",
        ratings=5.0
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="CTO",
        client_name="Diana Prince",
        author_id=user.id,
        comments="Good work",
        content="The project was completed on time and within budget.",
        ratings=4.0
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="HR Manager",
        client_name="Ethan Hunt",
        author_id=user.id,
        comments="Professional team",
        content="The team was professional and easy to work with.",
        ratings=4.6
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="Product Owner",
        client_name="Fiona Gallagher",
        author_id=user.id,
        comments="Highly recommend",
        content="I highly recommend their services to anyone.",
        ratings=4.8
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="Marketing Lead",
        client_name="George Michael",
        author_id=user.id,
        comments="Exceptional quality",
        content="The quality of work was exceptional.",
        ratings=4.9
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="Developer",
        client_name="Hannah Montana",
        author_id=user.id,
        comments="Very happy",
        content="I am very happy with the outcome of the project.",
        ratings=4.4
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="Analyst",
        client_name="Ian Malcolm",
        author_id=user.id,
        comments="Thoroughly impressed",
        content="I am thoroughly impressed by their professionalism.",
        ratings=5.0
    ),
    Testimonial(
        id=str(uuid.uuid4()),
        client_designation="Designer",
        client_name="Jenny Lee",
        author_id=user.id,
        comments="Wonderful experience",
        content="Working with them was a wonderful experience.",
        ratings=4.3
    )
]

db.add_all(testimonials)
db.commit()

print("Testimonials seed data successfully added.")
