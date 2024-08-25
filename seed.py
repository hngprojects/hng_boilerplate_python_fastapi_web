from api.v1.models import *
from api.v1.models.associations import Base
from api.v1.services.user import user_service
from api.db.database import create_database, get_db

# create_database()
db = next(get_db())


admin_user = User(
    email="Isaacj@gmail.com",
    password=user_service.hash_password("45@&tuTU"),
    first_name="Isaac",
    last_name="John",
    is_active=True,
    is_superadmin=True,
    is_deleted=False,
    is_verified=True,
)
db.add(admin_user)
db.commit()

print("Seed data succesfully")
