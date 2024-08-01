from api.v1.models import *
from api.v1.models.associations import Base
from api.v1.services.user import user_service
from api.db.database import create_database, get_db

# create_database()
db = next(get_db())


admin_user = User(
    email="habeeb@example.com",
    password=user_service.hash_password("supersecret"),
    first_name="Habeeb",
    last_name="Habeeb",
    is_active=True,
    is_super_admin=True,
    is_deleted=False,
    is_verified=True,
)
db.add(admin_user)
db.commit()

print("Seed data succesfully")
