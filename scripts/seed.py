#!/usr/bin/env python3
# """ Populates the database with seed data
# """
# import sys, os
# import warnings

# warnings.filterwarnings("ignore", category=DeprecationWarning)
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.v1.models.user import *
from api.v1.models.organization import *
# from api.v1.models.product import *
# from api.v1.models.profile import *
# from api.v1.models.blog import *
from api.v1.models.permissions.permissions import *
from api.v1.models.permissions.role import *
from api.v1.models.permissions.role_permissions import *
from api.v1.models.permissions.user_org_role import *
from api.v1.models.associations import *
# from api.v1.services.user import user_service
# from api.db.database import create_database, get_db

# # create_database()
# db = next(get_db())

# user_1 = User(
#     email="test@mail",
#     # username="testuser",
#     password=user_service.hash_password("testpass"),
#     first_name="John",
#     last_name="Doe",
# )
# user_2 = User(
#     email="test1@mail",
#     # username="testuser1",
#     password=user_service.hash_password("testpass1"),
#     first_name="Jane",
#     last_name="Boyle",
# )
# user_3 = User(
#     email="test2@mail",
#     # username="testuser2",
#     password=user_service.hash_password("testpass2"),
#     first_name="Bob",
#     last_name="Dwayne",
# )

# db.add_all([user_1, user_2, user_3])

# org_1 = Organization(
#     company_name="Python Org", 
# )
# org_2 = Organization(company_name="Django Org", )
# org_3 = Organization(
#     company_name="FastAPI Devs", 
# )


# db.add_all([org_1, org_2, org_3])


# org_1.users.extend([user_1, user_2, user_3])
# org_2.users.extend([user_1, user_3])
# org_3.users.extend([user_2, user_1])
# db.commit()

# pc = ProductCategory(name='ProductCategory')
# db.add(pc)
# db.commit()
# product_1 = Product(name="bed", price=400000, description="test product 1", org_id=org_1.id,category_id=pc.id)
# product_2 = Product(name="shoe", price=150000, description="test product 2", org_id=org_2.id, category_id=pc.id)
# product_3 = Product(name="choco", price=2000, description="test product 3", org_id=org_3.id, category_id=pc.id)
# product_4 = Product(name="Latte", price=29000, description="test product 4", org_id=org_3.id, category_id=pc.id)

# profile_1 = Profile(bio="My name is John Doe", phone_number="09022112233")
# user_1.profile = profile_1

# blog_1 = Blog(author_id=user_1.id, title="Test 1", content="Test blog one")
# blog_2 = Blog(author_id=user_2.id, title="Test 2", content="Test user two")

# db.add_all([product_1, product_2, product_3, product_4, blog_1, blog_2])
# db.commit()


# admin_user = User(
#     email="admin@example.com",
#     password=user_service.hash_password("supersecret"),
#     first_name="Admin",
#     last_name="User",
#     is_active=True,
#     is_super_admin=True,
#     is_deleted=False,
#     is_verified=True,
# )
# db.add(admin_user)
# db.commit()

# permission_1 = Permission(name='permission 1')
# permission_2 = Permission(name='permission 2')

# role_1 = Role(name='Role 1')
# role_2 = Role(name='Role 2')
# stmt = user_organization_association.insert().values(
#     user_id=user_1.id,
#     organization_id=org_1.id,
#     role='admin'
# )
# db.add_all([permission_1, permission_2, role_1, role_2])
# db.execute(stmt)
# db.commit()
# db.add(role_permissions.insert().values(role_id=role_1.id, permission_id=permission_1.id))
# db.commit()
# users = db.query(Organization).first().users
# print("Seed data succesfully")


import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.v1.models import *

from api.db.database import create_database, get_db
from api.v1.services.user import user_service
from faker import Faker

# create_database()
db = next(get_db())

# Initialize Faker
fake = Faker()
admin_user = db.query(User).filter(User.email == "admin@example.com").first()

if not admin_user:
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

normal_user = db.query(User).filter(User.email == "user@example.com").first()

if not normal_user:
    normal_user = User(
        email="user@example.com",
        password=user_service.hash_password("supersecret"),
        first_name=fake.file_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_super_admin=True,
        is_deleted=False,
        is_verified=True,
    )
    db.add(normal_user)
    db.commit()



# Create some dummy jobs
for _ in range(10):
    job = Job(
        author_id=admin_user.id,
        title=fake.job(),
        description=fake.paragraph(),
        department=fake.word(),
        location=fake.city(),
        salary=fake.random_element(["$50,000 - $70,000", "$70,000 - $90,000", "$90,000+"]),
        job_type=fake.random_element(["Full-time", "Part-time", "Contract"]),
        company_name=fake.company(),
    )
    db.add(job)
    db.commit()


jobs = db.query(Job).all()

# Create some dummy job applications
for _ in range(20):
    application = JobApplication(
        job_id=fake.random_element([i.id for i in jobs]),
        applicant_name=fake.name(),
        applicant_email=fake.email(),
        cover_letter=fake.paragraph(),
        resume_link=fake.url(),
        portfolio_link=fake.url() if fake.boolean(chance_of_getting_true=50) else None,
        application_status=fake.random_element(["pending", "accepted", "rejected"]),
    )
    db.add(application)
    db.commit()

org_1 = Organization(
    company_name="Python Org", 
)
org_2 = Organization(company_name="Django Org", )
org_3 = Organization(
    company_name="FastAPI Devs", 
)


db.add_all([org_1, org_2, org_3])


org_1.users.extend([normal_user, admin_user])
org_2.users.extend([ normal_user])
org_3.users.extend([admin_user ])
db.commit()
applications_for_job = db.query(JobApplication).all()
permission_1 = Permission(name='permission 1')
permission_2 = Permission(name='permission 2')

role_1 = Role(name='Role 1')
role_2 = Role(name='Role 2')
stmt = user_organization_association.insert().values(
    user_id=normal_user.id,
    organization_id=org_1.id,
    role='admin'
)
db.add_all([permission_1, permission_2, role_1, role_2])
db.execute(stmt)
db.commit()
db.add(role_permissions.insert().values(role_id=role_1.id, permission_id=permission_1.id))
db.commit()

roles = db.query(Role).all()
permisions = db.query(Permission).all()
print(roles)
print(permisions)
# roles = db.query(Role).all()
print("ID's for Job Application")
for _ in applications_for_job:
    print(f"Job aplication ID: {_.id}, Job ID: {_.job_id}")
