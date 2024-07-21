from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status
    )
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.v1.models.newsletter import NEWSLETTER
from api.v1.schemas.newsletter_schema import EMAILSCHEMA
from api.db.database import get_db, Base, engine


# Base.metadata.create_all(bind=engine)


router = APIRouter()

@router.post('/api/v1/pages/newsletter', tags=['Newsletter'])
async def sub_newsletter(request: EMAILSCHEMA, db: Session = Depends(get_db)):
    """
    Newsletter subscription endpoint
    """

    # check for duplicate email
    existing_subscriber = db.query(NEWSLETTER).filter(NEWSLETTER.email==request.email).first()
    if existing_subscriber:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    # Save user to the database
    new_subscriber = NEWSLETTER(email=request.email)
    db.add(new_subscriber)
    db.commit()

    return {
        "message": "Thank you for subscribing to our newsletter.",
        "success": True,
        "status": status.HTTP_201_CREATED
    }
