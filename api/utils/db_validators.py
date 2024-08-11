from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.v1.models import User, Organisation


def check_model_existence(db: Session, model, id):
    """Checks if a model exists by its id"""

    # obj = db.query(model).filter(model.id == id).first()
    obj = db.get(model, ident=id)

    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} does not exist")

    return obj


def check_user_in_org(user: User, organisation: Organisation):
    """Checks if a user is a member of an organisation"""

    if user not in organisation.users and not user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this organisation",
        )
