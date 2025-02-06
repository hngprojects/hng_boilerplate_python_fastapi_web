import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.v1.models.user import User
from api.v1.models.organisation import Organisation
from api.v1.models.associations import user_organisation_association
from api.db.database import get_db

# create_database()
db = next(get_db())

# Create some organisations
org1 = Organisation(
    name="Tech Corp",
    email="contact@techcorp.com",
    industry="Technology",
    type="Private",
    country="USA",
    state="California",
    address="123 Tech Lane",
    lga="San Francisco"
)
org2 = Organisation(
    name="Health Co",
    email="info@healthco.com",
    industry="Healthcare",
    type="Public",
    country="USA",
    state="New York",
    address="456 Health Blvd",
    lga="Manhattan"
)

# Add organisations to the session
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

# Add users to organisations with roles
stmt = user_organisation_association.insert().values([
    {'user_id': user1.id, 'organisation_id': org1.id, 'role': 'admin', 'status': 'member'},
    {'user_id': user2.id, 'organisation_id': org1.id, 'role': 'user', 'status': 'member'},
    {'user_id': user2.id, 'organisation_id': org2.id, 'role': 'owner', 'status': 'member'},
])

db.execute(stmt)
db.commit()
