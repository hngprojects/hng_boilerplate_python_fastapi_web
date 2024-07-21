#!/usr/bin/env python3
""" Populates the database with seed data
"""
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.blog import Blog

payload = {
    "users": [
        {
            "first_name": "John",
            "last_name": "Doe",
        },
        {
            "first_name": "Jane",
            "last_name": "Boyle",
        },
        {
            "first_name": "Bob",
            "last_name": "Dwayne",
        },
    ],
    "organizations": [
        {
            "name": "Python Org",
            "description": "An organization for python develoers",
        },
        {
            "name": "Django Org",
            "description": "An organization of django devs",
        },
        {
            "name": "FastAPI Devs",
            "description": "An organization of Fast API devs",
        },
    ],
    "products": [
        {
            "name": "bed",
            "price": 400000,
        },
        {
            "name": "shoe",
            "price": 150000,
        },
        {
            "name": "bag",
            "price": 50000,
        },
    ],
    "profiles": [
        {
            "bio": "My name is John Doe",
            "phone_number": "09022112233",
        },
        {
            "bio": "My name is Jane Boyle",
            "phone_number": "09022112233",
        },
        {
            "bio": "My name is Bob Dwayne",
            "phone_number": "09022112233",
        },
    ],
}

db = next(get_db())

user_1 = User(**payload["users"][0])
user_2 = User(**payload["users"][1])
user_3 = User(**payload["users"][2])

db.add_all([user_1, user_2, user_3])

# Delete organizations if they exist because they contain unique constraint in the name column
orgs = db.query(Organization).all()
for org in orgs:
    for p in payload["organizations"]:
        if org.name in p["name"]:
            db.delete(org)
    db.commit()

org_1 = Organization(**payload["organizations"][0])
org_2 = Organization(**payload["organizations"][1])
org_3 = Organization(**payload["organizations"][2])

db.add_all([org_1, org_2, org_3])

org_1.users.extend([user_1, user_2, user_3])
org_2.users.extend([user_1, user_3])
org_3.users.extend([user_2, user_1])

product_1 = Product(**payload["products"][0])
product_2 = Product(**payload["products"][1])
product_3 = Product(**payload["products"][2])

profile_1 = Profile(**payload["profiles"][0])
profile_2 = Profile(**payload["profiles"][1])
profile_3 = Profile(**payload["profiles"][2])

user_1.profile = profile_1
user_2.profile = profile_2
user_3.profile = profile_3

db.add_all([product_1, product_2, product_3])
db.commit()

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
users = db.query(Organization).first().users
print("Seed data succesfully")

users = db.query(Organization).first().users
for user in users:
    print(user.first_name)
print(profile_1.user_id)
print(profile_1.user)
