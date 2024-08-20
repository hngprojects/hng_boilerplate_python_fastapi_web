import datetime
from uuid_extensions import uuid7
from api.db.database import get_db
from api.v1.models import *
from api.v1.services.user import user_service

# create_database()
db = next(get_db())

# Add sample organisations
org_1 = Organisation(id=str(uuid7()), name="Python Org", description="An organisation for Python developers")
org_2 = Organisation(id=str(uuid7()), name="JavaScript Org", description="An organisation for JavaScript developers")
org_3 = Organisation(id=str(uuid7()), name="GoLang Org", description="An organisation for GoLang developers")

db.add_all([org_1, org_2, org_3])
db.commit()

plan1 = BillingPlan(
    id=str(uuid7()),
    name='Basic',
    price=200,
    currency='$',
    features=['email', 'messaging'],
    organisation_id=org_1.id
)
db.add_all([plan1])
db.commit()

# Add sample users
user_1 = User(
    id=str(uuid7()),
    username="user1",
    email="user1@example.com",
    password=user_service.hash_password("password1"),
    first_name="User",
    last_name="One",
    is_active=True,
    organisations=[org_1, org_2]
)

user_2 = User(
    id=str(uuid7()),
    username="user2",
    email="user2@example.com",
    password=user_service.hash_password("password2"),
    first_name="User",
    last_name="Two",
    is_active=True,
    organisations=[org_2, org_3]
)

user_3 = User(
    id=str(uuid7()),
    username="user3",
    email="user3@example.com",
    password=user_service.hash_password("password3"),
    first_name="User",
    last_name="Three",
    is_active=True,
    organisations=[org_1, org_3]
)

db.add_all([user_1, user_2, user_3])
db.commit()


# Add sample profiles
profile_1 = Profile(
    id=str(uuid7()),
    user_id=user_1.id,
    bio="This is user one's bio",
    phone_number="1234567890",
    avatar_url="http://example.com/avatar1.png"
)

profile_2 = Profile(
    id=str(uuid7()),
    user_id=user_2.id,
    bio="This is user two's bio",
    phone_number="0987654321",
    avatar_url="http://example.com/avatar2.png"
)

profile_3 = Profile(
    id=str(uuid7()),
    user_id=user_3.id,
    bio="This is user three's bio",
    phone_number="1122334455",
    avatar_url="http://example.com/avatar3.png"
)

db.add_all([profile_1, profile_2, profile_3])
db.commit()

# Add sample products
product_1 = Product(
    id=str(uuid7()),
    name="Product 1",
    description="Description for product 1",
    price=19.99
)

product_2 = Product(
    id=str(uuid7()),
    name="Product 2",
    description="Description for product 2",
    price=29.99
)

product_3 = Product(
    id=str(uuid7()),
    name="Product 3",
    description="Description for product 3",
    price=39.99
)

db.add_all([product_1, product_2, product_3])
db.commit()

# Add sample invitations
invitation_1 = Invitation(
    id=str(uuid7()),
    user_id=user_1.id,
    organisation_id=org_1.id,
    expires_at=datetime.datetime.now() + datetime.timedelta(days=7)
)

invitation_2 = Invitation(
    id=str(uuid7()),
    user_id=user_2.id,
    organisation_id=org_2.id,
    expires_at=datetime.datetime.now() + datetime.timedelta(days=7)
)

invitation_3 = Invitation(
    id=str(uuid7()),
    user_id=user_3.id,
    organisation_id=org_3.id,
    expires_at=datetime.datetime.now() + datetime.timedelta(days=7)
)

db.add_all([invitation_1, invitation_2, invitation_3])
db.commit()

# Close the db
db.close()

print("Sample data inserted successfully.")
