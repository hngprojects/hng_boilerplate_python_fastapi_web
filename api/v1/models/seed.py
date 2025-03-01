from api.v1.models.user import User
from api.v1.models.organisation import Organisation
from api.v1.models.permissions.user_org_role import user_organisation_roles
from sqlalchemy.orm import Session
from faker import Faker

fake = Faker()

def seed_user_and_org(db: Session):
    # Create a user
    user = User(email=fake.email(), password=fake.password(), first_name=fake.first_name(), last_name=fake.last_name())
    db.add(user)
    db.commit()

    # Create an organization
    org = Organisation(name=fake.company(), email=fake.company_email())
    db.add(org)
    db.commit()

    # Link the user and organization in the association table
    db.execute(user_organisation_roles.insert().values(
        user_id=user.id,
        organisation_id=org.id,
        is_owner=True, #make the user the owner.
        status='active'
    ))
    db.commit()

    return user, org