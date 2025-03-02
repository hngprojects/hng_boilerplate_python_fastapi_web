from api.v1.models import *
from api.v1.models.associations import Base
from api.v1.services.user import user_service
from api.v1.models.job import JobApplication, Job
from api.db.database import create_database, get_db

# create_database()
db = next(get_db())


admin_user = User(
    email="adsolae@gmail.com",
    password=user_service.hash_password("45@&tuTU"),
    first_name="adesola",
    last_name="Busari",
    is_active=True,
    is_superadmin=True,
    is_deleted=False,
    is_verified=True,
)
db.add(admin_user)
db.commit()


job_posting = Job(
    title="QA Engineer",
    description="Develop and maintain web applications.",
    department="Engineering",
    location="Remote",
    salary="$100,000 - $150,000",
    job_type="Full-time",
    company_name="TechCorp",
    author_id=admin_user.id,  # Associate with the admin user

)
db.add(job_posting)
db.commit()

job_application = JobApplication(
    job_id=job_posting.id,  # Use the ID of the created job
    applicant_name="Alice Smith",
    applicant_email="alice.smith@example.com",
    resume_link="https://example.com/alice_resume.pdf",
    portfolio_link="https://example.com/alice_portfolio",
    cover_letter="Dear Hiring Manager...",
    application_status="Applied"
)
db.add(job_application)
db.commit()


print("Seed data succesfully")
