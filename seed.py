
from api.v1.models import *
from api.v1.models.associations import Base
from api.v1.services.user import user_service
from api.db.database import create_database, get_db

# create_database()
db = next(get_db())


# Create a new user
new_user = User(email="john@example.com", first_name="John", last_name="Doe")
admin_user = User(
    email="admin@example.com",
    password=user_service.hash_password("supersecret"),
    first_name="Admin",
    last_name="User",
    is_active=True,
    is_super_admin=True,
    is_deleted=False,
    is_verified=True,
)
db.add(admin_user)
db.add(new_user)
db.commit()

# Create a new testimonial
new_testimonial = Testimonial(
    client_designation="CEO",
    client_name="Company X",
    content="Great service!",
    ratings=4.5,
    author=new_user,  # Associate the testimonial with the user
)
db.add(new_testimonial)

# Commit the changes to the database
db.commit()

# Close the db
db.close()
