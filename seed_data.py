from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.v1 import models
from api.v1.models.base import Base
from api.v1.models.org import Organization
from api.v1.models.preference import OrgPreference
from api.v1.models.user import User  # Update with your actual import path
import bcrypt

#from tests.database import DATABASE_URL

# Database configuration
DATABASE_URL="postgresql://postgres:Admin@localhost:5432/hng_fast_api"
# Replace with your actual database URL

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def hash_password(password: str) -> str:
    # Hash the password using bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def seed_organizations():
    org1 = Organization(name="Organization One", description="Description for Org One")
    org2 = Organization(name="Organization Two", description="Description for Org Two")
    session.add_all([org1, org2])
    session.commit()

def seed_org_preferences():
    org1 = session.query(Organization).filter_by(name="Organization One").first()
    org2 = session.query(Organization).filter_by(name="Organization Two").first()

    preference1 = OrgPreference(key="theme", value="dark", organization_id=org1.id)
    preference2 = OrgPreference(key="language", value="en", organization_id=org2.id)
    session.add_all([preference1, preference2])
    session.commit()

def seed_users():
    password1 = "plaintextpassword1"
    password2 = "plaintextpassword2"
    
    user1 = User(username="user1", email="user1@example.com", password=hash_password(password1), first_name="First", last_name="User")
    user2 = User(username="user2", email="user2@example.com", password=hash_password(password2), first_name="Second", last_name="User")
    session.add_all([user1, user2])
    session.commit()

def main():
    # Create tables
    Base.metadata.create_all(engine)

    # Seed data
    seed_organizations()
    seed_org_preferences()
    seed_users()

if __name__ == "__main__":
    main()
