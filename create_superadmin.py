# create_superadmin.py
from api.db.database import get_db
from api.v1.schemas.user import UserCreate
from api.v1.services.user import user_service

def create_superadmin():
    db = next(get_db())
    schema = UserCreate(
        email="admin@gmail.com",  # Use a valid domain
        password="Admin123!@#",
        first_name="Admin",
        last_name="User"
    )
    user = user_service.create_admin(db, schema)
    print(f"Superadmin created: {user.email}")

if __name__ == "__main__":
    create_superadmin()
