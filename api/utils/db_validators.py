from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.v1.models import User, Organization


def check_model_existence(db: Session, model, id):
    """Checks if a model exists by its id"""

    # obj = db.query(model).filter(model.id == id).first()
    obj = db.get(model, ident=id)

    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} does not exist")

    return obj


def check_user_in_org(user: User, organization: Organization):
    """Checks if a user is a member of an organization"""

    if user not in organization.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )
