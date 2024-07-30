import sys, os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.v1.models import *
from api.v1.models.associations import Base
from api.v1.services.user import user_service
from api.db.database import create_database, get_db

# create_database()
db = next(get_db())


admin_user = User(
    email="admin@example.com",
    password=user_service.hash_password("supersecret"),
    first_name="Admin",
    last_name="Habeeb",
    user_name="Habeeb",
    is_active=True,
    is_super_admin=True,
    is_deleted=False,
    is_verified=True,
)
db.add(admin_user)
db.commit()

print("Seed data succesfully")
