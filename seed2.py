import datetime
from uuid_extensions import uuid7
from api.db.database import create_database, get_db
from api.utils.auth import hash_password
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
from api.v1.models.base import user_organization_association as UserOrganization
from api.v1.models.base import user_role_association as UserRole
from api.v1.models.base import role_permission_association as RolePermission

# create_database()
db = next(get_db())

# Add sample organizations
org_1 = Organization(id=uuid7(), name="Python Org", description="An organization for Python developers")
org_2 = Organization(id=uuid7(), name="JavaScript Org", description="An organization for JavaScript developers")
org_3 = Organization(id=uuid7(), name="GoLang Org", description="An organization for GoLang developers")

db.add_all([org_1, org_2, org_3])
db.commit()

# Add sample users
user_1 = User(
    id=uuid7(),
    username="user1",
    email="user1@example.com",
    password=hash_password("password1"),
    first_name="User",
    last_name="One",
    is_active=True,
    organizations=[org_1, org_2]
)

user_2 = User(
    id=uuid7(),
    username="user2",
    email="user2@example.com",
    password=hash_password("password2"),
    first_name="User",
    last_name="Two",
    is_active=True,
    organizations=[org_2, org_3]
)

user_3 = User(
    id=uuid7(),
    username="user3",
    email="user3@example.com",
    password=hash_password("password3"),
    first_name="User",
    last_name="Three",
    is_active=True,
    organizations=[org_1, org_3]
)

db.add_all([user_1, user_2, user_3])
db.commit()

# Add sample roles
role_1 = Role(id=uuid7(), role_name="Admin", organization_id=org_1.id)
role_2 = Role(id=uuid7(), role_name="Member", organization_id=org_1.id)
role_3 = Role(id=uuid7(), role_name="Admin", organization_id=org_2.id)
role_4 = Role(id=uuid7(), role_name="Member", organization_id=org_2.id)

db.add_all([role_1, role_2, role_3, role_4])
db.commit()

# Add sample permissions
perm_1 = Permission(id=uuid7(), name="read")
perm_2 = Permission(id=uuid7(), name="write")
perm_3 = Permission(id=uuid7(), name="delete")

db.add_all([perm_1, perm_2, perm_3])
db.commit()

# Add sample user roles
user_role_1 = UserRole(user_id=user_1.id, role_id=role_1.id)
user_role_2 = UserRole(user_id=user_2.id, role_id=role_3.id)
user_role_3 = UserRole(user_id=user_3.id, role_id=role_2.id)

db.add_all([user_role_1, user_role_2, user_role_3])
db.commit()

# Add sample role permissions
role_perm_1 = RolePermission(role_id=role_1.id, permission_id=perm_1.id)
role_perm_2 = RolePermission(role_id=role_1.id, permission_id=perm_2.id)
role_perm_3 = RolePermission(role_id=role_3.id, permission_id=perm_3.id)

db.add_all([role_perm_1, role_perm_2, role_perm_3])
db.commit()

# Add sample profiles
profile_1 = Profile(
    id=uuid7(),
    user_id=user_1.id,
    bio="This is user one's bio",
    phone_number="1234567890",
    avatar_url="http://example.com/avatar1.png"
)

profile_2 = Profile(
    id=uuid7(),
    user_id=user_2.id,
    bio="This is user two's bio",
    phone_number="0987654321",
    avatar_url="http://example.com/avatar2.png"
)

profile_3 = Profile(
    id=uuid7(),
    user_id=user_3.id,
    bio="This is user three's bio",
    phone_number="1122334455",
    avatar_url="http://example.com/avatar3.png"
)

db.add_all([profile_1, profile_2, profile_3])
db.commit()

# Add sample products
product_1 = Product(
    id=uuid7(),
    name="Product 1",
    description="Description for product 1",
    price=19.99
)

product_2 = Product(
    id=uuid7(),
    name="Product 2",
    description="Description for product 2",
    price=29.99
)

product_3 = Product(
    id=uuid7(),
    name="Product 3",
    description="Description for product 3",
    price=39.99
)

db.add_all([product_1, product_2, product_3])
db.commit()

# Add sample invitations
invitation_1 = Invitation(
    id=uuid7(),
    user_id=user_1.id,
    organization_id=org_1.id,
    expires_at=datetime.datetime.now() + datetime.timedelta(days=7)
)

invitation_2 = Invitation(
    id=uuid7(),
    user_id=user_2.id,
    organization_id=org_2.id,
    expires_at=datetime.datetime.now() + datetime.timedelta(days=7)
)

invitation_3 = Invitation(
    id=uuid7(),
    user_id=user_3.id,
    organization_id=org_3.id,
    expires_at=datetime.datetime.now() + datetime.timedelta(days=7)
)

db.add_all([invitation_1, invitation_2, invitation_3])
db.commit()

# Close the db
db.close()

print("Sample data inserted successfully.")
