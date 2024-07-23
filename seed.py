#!/usr/bin/env python3
""" Populates the database with seed data
"""
from api.db.database import create_database, get_db
from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission

# create_database()
db = next(get_db())

user_1 = User(email="test@mail", username="testuser", password="testpass", first_name="John", last_name="Doe")
user_2 = User(email="test1@mail", username="testuser1", password="testpass1", first_name="Jane", last_name="Boyle")
user_3 = User(email="test2@mail", username="testuser2", password="testpass2", first_name="Bob", last_name="Dwayne")

db.add_all([user_1, user_2, user_3])

org_1 = Organization(name= "Python Org", description="An organization for python develoers")
org_2 = Organization(name="Django Org", description="An organization of django devs")
org_3 = Organization(name="FastAPI Devs", description="An organization of Fast API devs")

# user_role = Role()

db.add_all([org_1, org_2, org_3])


org_1.users.extend([user_1, user_2, user_3])
org_2.users.extend([user_1, user_3])
org_3.users.extend([user_2, user_1])

product_1 = Product(name="bed", price=400000)
product_2 = Product(name="shoe", price=150000)

profile_1 = Profile(bio='My name is John Doe', phone_number='09022112233')
user_1.profile = profile_1

db.add_all([product_1, product_2])
db.commit()
users = db.query(Organization).first().users
print("Seed data succesfully")

