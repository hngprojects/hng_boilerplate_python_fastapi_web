
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
        name=fake.company(),
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

applications_for_job = db.query(JobApplication).all()


print("ID's for Job Application")
for _ in applications_for_job:
    print(f"Job aplication ID: {_.id}, Job ID: {_.job_id}")
