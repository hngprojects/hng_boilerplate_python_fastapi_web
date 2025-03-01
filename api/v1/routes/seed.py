# api/v1/routes/seed.py
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.db_utils import seed_user_and_org
from faker import Faker

fake = Faker()

seed = APIRouter(tags=['Seed'])

@seed.post("/seed")
def seed_users(db: Session = Depends(get_db), num_users: int = Query(1, description="Number of fake users to create")):
    """
    Seeds the database with fake users and organizations.
    """
    try:
        users_created = []
        for _ in range(num_users):
            user_data = {
                'email': fake.email(),
                'password': 'testpassword',
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'avatar_url': fake.image_url(),
                'is_superadmin': fake.boolean(),
                'org_name': fake.company(),
                'org_email': fake.company_email(),
                'username': fake.user_name(),
                'pronouns': fake.random_element(elements=('they/them', 'he/him', 'she/her')),
                'job_title': fake.job(),
                'department': fake.random_element(elements=('Engineering', 'Sales', 'Marketing')),
                'social': '{"github": "' + fake.user_name() + '"}',
                'bio': fake.text(),
                'phone_number': fake.phone_number(),
                'profile_avatar_url': fake.image_url(),
                'recovery_email': fake.email(),
                'facebook_link': fake.url(),
                'instagram_link': fake.url(),
                'twitter_link': fake.url(),
                'linkedin_link': fake.url(),
            }
            user, org, profile = seed_user_and_org(db, user_data)
            users_created.append(user.email)

        return {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": f"{num_users} users and organizations seeded successfully.",
            "data": {"users": users_created}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": f"An error occurred: {str(e)}",
                "data": None
            }
        )