#!/usr/bin/env python3
""" Populates the database with seed data
"""
from api.v1.models import *
from api.v1.models.base import Base
from api.v1.models.contact import ContactMessage
from api.v1.services.user import user_service
from api.db.database import create_database, get_db







# create_database()
db = next(get_db())

user_1 = User(email="test@mail", username="testuser", password=user_service.hash_password("testpass"), first_name="John", last_name="Doe")
user_2 = User(email="test1@mail", username="testuser1", password=user_service.hash_password("testpass1"), first_name="Jane", last_name="Boyle")
user_3 = User(email="test2@mail", username="testuser2", password=user_service.hash_password("testpass2"), first_name="Bob", last_name="Dwayne")

db.add_all([user_1, user_2, user_3])

org_1 = Organization(name= "Python Org", description="An organization for python develoers")
org_2 = Organization(name="Django Org", description="An organization of django devs")
org_3 = Organization(name="FastAPI Devs", description="An organization of Fast API devs")


db.add_all([org_1, org_2, org_3])


org_1.users.extend([user_1, user_2, user_3])
org_2.users.extend([user_1, user_3])
org_3.users.extend([user_2, user_1])
db.commit()

product_1 = Product(name="bed", price=400000, org_id=org_1.id)
product_2 = Product(name="shoe", price=150000, org_id=org_2.id)

profile_1 = Profile(bio='My name is John Doe', phone_number='09022112233')
user_1.profile = profile_1

# Create Contact Messages
contact_msg_1 = ContactMessage(
    id="1",  # Assuming UUIDs are managed manually or replaced with actual UUIDs
    sender="Alice",
    email="alice@example.com",
    message="Hello, I need help with my account.",
    created_at="2024-07-01T12:00:00Z",
    updated_at="2024-07-01T12:00:00Z"
)

contact_msg_2 = ContactMessage(
    id="2",  # Assuming UUIDs are managed manually or replaced with actual UUIDs
    sender="Bob",
    email="bob@example.com",
    message="Inquiry about product features.",
    created_at="2024-07-02T13:00:00Z",
    updated_at="2024-07-02T13:00:00Z"
)

db.add_all([product_1, product_2, contact_msg_1, contact_msg_2])
db.commit()
users = db.query(Organization).first().users
print("Seed data succesfully")

