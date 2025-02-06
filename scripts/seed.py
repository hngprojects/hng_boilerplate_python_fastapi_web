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
from uuid_extensions import uuid7

# create_database()
db = next(get_db())

user_1 = User(
    id=str(uuid7()),
    email="test@email.com",
    password=user_service.hash_password("testpass"),
    first_name="John",
    last_name="Doe",
)
user_2 = User(
    id=str(uuid7()),
    email="test1@mail",
    password=user_service.hash_password("testpass1"),
    first_name="Jane",
    last_name="Boyle",
)
user_3 = User(
    id=str(uuid7()),
    email="test2@mail",
    password=user_service.hash_password("testpass2"),
    first_name="Bob",
    last_name="Dwayne",
)

db.add_all([user_1, user_2, user_3])

org_1 = Organisation(
    name="Python Org", type="An organisation for python develoers"
)
org_2 = Organisation(name="Django Org", type="An organisation of django devs")
org_3 = Organisation(
    name="FastAPI Devs", type="An organisation of Fast API devs"
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
    is_superadmin=True,
    is_deleted=False,
    is_verified=True,
)
db.add(admin_user)

newsletter_1 = Newsletter(
    title="test newsletter 1",
    description="a test newsletter"
)

newsletter_2 = Newsletter(
    title="test newsletter 2",
    description="a test newsletter"
)

db.add_all([newsletter_1, newsletter_2])
db.commit()

job_1 = Job(id=str(uuid7()), author_id=user_1.id, description="Test job one", title="Engineer")
job_2 = Job(id=str(uuid7()), author_id=user_2.id, description="Test job two", title="title")

application_1 = JobApplication(id=str(uuid7()), job_id=job_1.id, applicant_name=user_1.first_name, applicant_email=user_1.email,
                                resume_link="lakjfoaldflaf")
application_2 = JobApplication(id=str(uuid7()), job_id=job_2.id, applicant_name=user_2.first_name, applicant_email=user_2.email,
                                resume_link="lakjfoaldflaf")

db.add_all([job_1, job_2, application_1, application_2])
db.commit()

users = db.query(Organisation).first().users
print("Seed data succesfully")