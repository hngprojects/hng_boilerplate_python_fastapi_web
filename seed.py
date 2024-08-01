
from api.v1.models import *
from api.v1.models.associations import Base
from api.v1.services.user import user_service
from api.db.database import create_database, get_db
from faker import Faker

fake = Faker()

db = next(get_db())
# try:
#     admin_user = User(
#         email="admin@example.com",
#         password=user_service.hash_password("supersecret"),
#         first_name="Admin",
#         last_name="User",
#         is_active=True,
#         is_super_admin=True,
#         is_deleted=False,
#         is_verified=True,
#     )
#     db.add(admin_user)
#     db.commit()
# except Exception as error:
admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    
def create_dummy_jobs(num_jobs=10):
    dummy_jobs = []
    for _ in range(num_jobs):
        job = Job(
            author_id=admin_user.id,
            title=fake.job(),
            description=fake.paragraph(),
            department=fake.random_element(["Engineering", "Marketing", "Sales"]),
            location=fake.city(),
            salary=fake.random_element(["$60,000 - $80,000", "$80,000 - $100,000"]),
            job_type=fake.random_element(["Full-time", "Contract", "Part-time"]),
            company_name=fake.company(),
        )
        dummy_jobs.append(job)
    return dummy_jobs

# Usage example
dummy_jobs = create_dummy_jobs(num_jobs=20)
db.add_all(dummy_jobs)
db.commit()
print("Seed data succesfully")