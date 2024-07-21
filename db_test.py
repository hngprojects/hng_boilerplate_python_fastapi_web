#!/usr/bin/env python3
""" Populates the database with seed data
"""
from datetime import datetime
from api.db.database import create_database, get_db
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.testimonials import Testimonial

create_database()
db = next(get_db())
db.expunge_all()
db.reset()
db.flush()
user_1 = User(email="test@mail", username="testuser", password="testpass", first_name="John", last_name="Doe")
user_2 = User(email="test1@mail", username="testuser1", password="testpass1", first_name="Jane", last_name="Boyle")
user_3 = User(email="test2@mail", username="testuser2", password="testpass2", first_name="Bob", last_name="Dwayne")

db.add_all([user_1, user_2, user_3])

org_1 = Organization(name="Python Org", description="An organization for python develoers")
org_2 = Organization(name="Django Org", description="An organization of django devs")
org_3 = Organization(name="FastAPI Devs", description="An organization of Fast API devs")

db.add_all([org_1, org_2, org_3])

org_1.users.extend([user_1, user_2, user_3])
org_2.users.extend([user_1, user_3])
org_3.users.extend([user_2, user_1])

product_1 = Product(name="bed", price=400000)
product_2 = Product(name="shoe", price=150000)

profile_1 = Profile(bio='My name is John Doe', phone_number='09022112233')
user_1.profile = profile_1

db.add_all([product_1, product_2])


testimonials = [
    Testimonial(client_name="Jane Smith", client_designation="Freelance Designer", testimonial="Excellent service and support!", rating=5, date=datetime.now()),
    Testimonial(client_name="John Doe", client_designation="Developer", testimonial="Great experience!", rating=4, date=datetime.now()),
    Testimonial(client_name="Alice Johnson", client_designation="Manager", testimonial="Very helpful!", rating=5, date=datetime.now()),
    Testimonial(client_name="Bob Brown", client_designation="CEO", testimonial="Highly recommend!", rating=5, date=datetime.now()),
    Testimonial(client_name="Charlie Davis", client_designation="CTO", testimonial="Professional service!", rating=4, date=datetime.now()),
    Testimonial(client_name="Dana Lee", client_designation="CFO", testimonial="Excellent support!", rating=5, date=datetime.now()),

]

db.add_all(testimonials)
db.commit()
users = db.query(Organization).first().users
for user in users:
    print(user.password)
print(profile_1.user_id)
print(profile_1.user)
#
#