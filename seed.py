#!/usr/bin/env python3
"""Populates the database with seed data"""

from api.db.database import create_database, get_db, engine
from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.invitation import Invitation
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from datetime import datetime, timedelta

# Drop all tables and recreate them
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = next(get_db())

user_1 = User(
    email="test@mail",
    username="testuser",
    password="testpass",
    first_name="John",
    last_name="Doe",
)
user_2 = User(
    email="test1@mail",
    username="testuser1",
    password="testpass1",
    first_name="Jane",
    last_name="Boyle",
)
user_3 = User(
    email="test2@mail",
    username="testuser2",
    password="testpass2",
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

# user_role = Role()

db.add_all([org_1, org_2, org_3])


org_1.users.extend([user_1, user_2, user_3])
org_2.users.extend([user_1, user_3])
org_3.users.extend([user_2, user_1])

product_1 = Product(name="bed", price=400000)
product_2 = Product(name="shoe", price=150000)

profile_1 = Profile(bio="My name is John Doe", phone_number="09022112233")
user_1.profile = profile_1

db.add_all([product_1, product_2])

db.commit()  # commit now to ensure user is saved so as to be used when creating a blog

# Create blog posts
blog_1 = Blog(
    author_id=user_1.id,
    title="My First Blog",
    content="This is the content of my first blog.",
    image_url="https://example.com/image1.jpg",
    tags=["python", "coding"],
    is_deleted=False,
    excerpt="This is an excerpt from my first blog.",
)

blog_2 = Blog(
    author_id=user_2.id,
    title="Jane's Blog",
    content="Jane's thoughts on coding.",
    image_url="https://example.com/image2.jpg",
    tags=["django", "webdev"],
    is_deleted=False,
    excerpt="This is an excerpt from Jane's blog.",
)

blog_3 = Blog(
    author_id=user_3.id,
    title="Bob's Adventures",
    content="Adventures in software development.",
    image_url="https://example.com/image3.jpg",
    tags=["fastapi", "adventures"],
    is_deleted=False,
    excerpt="This is an excerpt from Bob's adventures.",
)

db.add_all([blog_1, blog_2, blog_3])

db.commit()

expiry = datetime.now() + timedelta(hours=24)
invite_1 = Invitation(user_id=user_1.id, organization_id=org_1.id, expires_at=expiry)
invite_2 = Invitation(user_id=user_2.id, organization_id=org_2.id, expires_at=expiry)

db.add_all([invite_1, invite_2])
db.commit()


users = db.query(Organization).first().users
print("Seed data succesfully")
