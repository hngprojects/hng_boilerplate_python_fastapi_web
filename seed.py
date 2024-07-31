from api.v1.models import User
from api.v1.services.user import user_service
from api.db.database import create_database, get_db

# Create the database (uncomment if needed)
# create_database()

db = next(get_db())

# Create an admin user
admin_user = User(
    email="admin@example.com",
    password=user_service.hash_password("supersecret"),  # Ensure this method exists and works correctly
    first_name="Admin",
    last_name="Habeeb",
    is_active=True,
    is_super_admin=True,
    is_deleted=False,
    is_verified=True,
)

# Add and commit the admin user to the database
try:
    db.add(admin_user)
    db.commit()
    print("Seed data successfully added")
except Exception as e:
    db.rollback()
    print(f"An error occurred: {e}")
finally:
    db.close()
