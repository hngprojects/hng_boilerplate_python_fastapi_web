from api.v1.models.user import User
from api.v1.models.profile import Profile


def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()


def get_user_profile(db, user_id):
    return db.query(Profile).filter(Profile.user_id == user_id).first()
