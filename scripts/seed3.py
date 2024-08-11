
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
        is_superadmin=True,
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
        is_superadmin=True,
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

for _ in range(20):
    organisation = Organisation(
        name=fake.company(),
        email=fake.email(),
        industry=fake.job(),
        type=fake.random_element(elements=("Non-profit", "Startup", "Corporation")),
        description=fake.paragraph(),
        country=fake.country(),
        state=fake.state(),
        address=fake.address(),
    )
    db.add(organisation)
    db.commit()

for _ in range(5):
    category = ProductCategory(
        name=fake.word(),
    )
    db.add(category)
    db.commit()

organisations = db.query(Organisation).all()
categories = db.query(ProductCategory).all()

for _ in range(20):
    product = Product(
        name=fake.numerify(text='Intel Core i%-%%##K vs AMD Ryzen % %%##X'),
        description=fake.paragraph(),
        price=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
        org_id=fake.random_element([ i.id for i in organisations ]),
        category_id=fake.random_element([ i.id for i in categories ]),
        quantity=fake.random_int(min=0, max=100),
        image_url=fake.image_url(),
        status=fake.random_element(elements=("in_stock", "out_of_stock", "low_on_stock")),
        archived=fake.boolean(),
        filter_status=fake.random_element(elements=("active", "draft")),
    )
    db.add(product)
    db.commit()

# Commit the changes
products = db.query(Product).all()


print("ID's for Job Application")
for _ in products:
    print(f"Product ID: {_.id}")
