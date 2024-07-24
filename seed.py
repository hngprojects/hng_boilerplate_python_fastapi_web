#!/usr/bin/env python3
""" Populates the database with seed data
"""
from api.v1.models import *
from api.v1.models.base import Base
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
db.commit()

bill_1 = BillingPlan(organization_id=org_1.id, name="Basic", price=5.00, currency="NGN", features=['Free basis'])
bill_2 = BillingPlan(organization_id=org_2.id, name="Upgrade", price=10.00, currency="NGN", features=['Free basis'])
bill_3 = BillingPlan(organization_id=org_3.id, name="Premium", price=15.00, currency="NGN", features=['Free basis'])


db.add_all([bill_1, bill_2, bill_3])
db.commit()


org_1.users.extend([user_1, user_2, user_3])
org_2.users.extend([user_1, user_3])
org_3.users.extend([user_2, user_1])
db.commit()

product_1 = Product(name="bed", price=400000, org_id=org_1.id)
product_2 = Product(name="shoe", price=150000, org_id=org_2.id)

profile_1 = Profile(bio='My name is John Doe', phone_number='09022112233')
user_1.profile = profile_1

db.add_all([product_1, product_2])
db.commit()
users = db.query(Organization).first().users
print("Seed data succesfully")

