# api/utils/db_utils.py
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.organisation import Organisation
from api.v1.models.profile import Profile
from api.v1.models.permissions.user_org_role import user_organisation_roles
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def seed_user_and_org(db: Session, user_data: dict):
    # Seed user
    hashed_password = hash_password(user_data['password'])
    user = User(
        email=user_data['email'],
        password=hashed_password,
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        avatar_url=user_data.get('avatar_url'),
        is_superadmin=user_data.get('is_superadmin', False),
        username=user_data.get('username') #add username to user table
    )
    db.add(user)
    db.commit()

    # Seed organization
    org = Organisation(name=user_data['org_name'], email=user_data['org_email'])
    db.add(org)
    db.commit()

    # Seed profile
    profile = Profile(
        user_id=user.id,
        username=user_data.get('username'),
        pronouns=user_data.get('pronouns'),
        job_title=user_data.get('job_title'),
        department=user_data.get('department'),
        social=user_data.get('social'),
        bio=user_data.get('bio'),
        phone_number=user_data.get('phone_number'),
        avatar_url=user_data.get('profile_avatar_url'),
        recovery_email=user_data.get('recovery_email'),
        facebook_link=user_data.get('facebook_link'),
        instagram_link=user_data.get('instagram_link'),
        twitter_link=user_data.get('twitter_link'),
        linkedin_link=user_data.get('linkedin_link'),
    )
    db.add(profile)
    db.commit()

    # Seed association
    db.execute(user_organisation_roles.insert().values(user_id=user.id, organisation_id=org.id, is_owner=True, status='active'))
    db.commit()

    return user, org, profile