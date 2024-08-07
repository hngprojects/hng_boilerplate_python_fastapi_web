import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.v1.models.user import User
from api.v1.models.organization import Organization
from api.v1.models.associations import user_organization_association
from api.db.database import get_db

# create_database()
db = next(get_db())

# Create some organizations
org1 = Organization(
    name="Tech Corp",
    email="contact@techcorp.com",
    industry="Technology",
    type="Private",
    country="USA",
    state="California",
    address="123 Tech Lane",
    ="San Francisco"
)
org2 = Organization(
    name="Health Co",
    email="info@healthco.com",
    industry="Healthcare",
    type="Public",
    country="USA",
    state="New York",
    address="456 Health Blvd",
    ="Manhattan"
)

# Add organizations to the session
db.add_all([org1, org2])
db.commit()

# Create some users
user1 = User(
    email="john.doe@example.com",
    first_name="John",
    last_name="Doe",
    avatar_url="https://example.com/avatar1.png",
    is_verified=True,
)
user2 = User(
    email="jane.smith@example.com",
    first_name="Jane",
    last_name="Smith",
    avatar_url="https://example.com/avatar2.png",
    is_verified=True,
)

# Add users to the session
db.add_all([user1, user2])
db.commit()

# Add users to organizations with roles
stmt = user_organization_association.insert().values([
    {'user_id': user1.id, 'organization_id': org1.id, 'role': 'admin', 'status': 'member'},
    {'user_id': user2.id, 'organization_id': org1.id, 'role': 'user', 'status': 'member'},
    {'user_id': user2.id, 'organization_id': org2.id, 'role': 'owner', 'status': 'member'},
])

db.execute(stmt)
db.commit()
