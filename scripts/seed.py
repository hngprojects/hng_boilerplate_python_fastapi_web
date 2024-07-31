#!/usr/bin/env python3
""" Populates the database with seed data
"""
import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.v1.models import *
from api.v1.models.associations import Base
from api.v1.services.user import user_service
from api.db.database import create_database, get_db

# create_database()
db = next(get_db())

user_1 = User(
    email="test@mail",
    username="testuser",
    password=user_service.hash_password("testpass"),
    first_name="John",
    last_name="Doe",
)
user_2 = User(
    email="test1@mail",
    username="testuser1",
    password=user_service.hash_password("testpass1"),
    first_name="Jane",
    last_name="Boyle",
)
user_3 = User(
    email="test2@mail",
    username="testuser2",
    password=user_service.hash_password("testpass2"),
    first_name="Bob",
    last_name="Dwayne",
)

db.add_all([user_1, user_2, user_3])

org_1 = Organization(
    name="Python Org", description="An organization for python develoers"
)
org_2 = Organization(name="Django Org", description="An organization of django devs")
org_3 = Organization(
    name="FastAPI Devs", description="An organization of Fast API devs"
)


db.add_all([org_1, org_2, org_3])


org_1.users.extend([user_1, user_2, user_3])
org_2.users.extend([user_1, user_3])
org_3.users.extend([user_2, user_1])
db.commit()

product_1 = Product(name="bed", price=400000, description="test product 1", org_id=org_1.id)
product_2 = Product(name="shoe", price=150000, description="test product 2", org_id=org_2.id)
product_3 = Product(name="choco", price=2000, description="test product 3", org_id=org_3.id)
product_4 = Product(name="Latte", price=29000, description="test product 4", org_id=org_3.id)

profile_1 = Profile(bio="My name is John Doe", phone_number="09022112233")
user_1.profile = profile_1

blog_1 = Blog(author_id=user_1.id, title="Test 1", content="Test blog one")
blog_2 = Blog(author_id=user_2.id, title="Test 2", content="Test user two")

db.add_all([product_1, product_2, product_3, product_4, blog_1, blog_2])
db.commit()


admin_user = User(
    email="admin@example.com",
    password=user_service.hash_password("supersecret"),
    first_name="Admin",
    last_name="User",
    is_active=True,
    is_super_admin=True,
    is_deleted=False,
    is_verified=True,
)
db.add(admin_user)
db.commit()

users = db.query(Organization).first().users
print("Seed data succesfully")