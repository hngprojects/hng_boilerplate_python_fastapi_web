from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    status
    )
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.v1.models.newsletter import Newsletter
from api.v1.schemas.newsletter import EMAILSCHEMA
from api.db.database import get_db, Base, engine

from api.utils.exceptions import CustomException

newsletter = APIRouter(prefix='/pages', tags=['Newsletter'])

@newsletter.post('/newsletter')
async def sub_newsletter(request: EMAILSCHEMA, db: Session = Depends(get_db)):
    """
    Newsletter subscription endpoint
    """

    # check for duplicate email
    existing_subscriber = db.query(Newsletter).filter(Newsletter.email==request.email).first()
    if existing_subscriber:
        raise CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Email already exists",
                "success": False,
                "status_code": 400
            }
        )

    # Save user to the database
    new_subscriber = Newsletter(email=request.email)
    db.add(new_subscriber)
    db.commit()

    return {
        "message": "Thank you for subscribing to our newsletter.",
        "success": True,
        "status": status.HTTP_201_CREATED
    }
