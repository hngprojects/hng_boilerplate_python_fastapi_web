from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    status
    )
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.v1.models.newsletter import NEWSLETTER
from api.v1.schemas.newsletter_schema import EMAILSCHEMA
from api.db.database import get_db
from api.db.database import create_database, get_db
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product

create_database()


class CustomException(HTTPException):
    """
    Custom error handling
    """
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")

async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "success": exc.success,
            "status_code": exc.status_code
        }
    )

router = APIRouter()

@router.post('/api/v1/pages/newsletter', tags=['Newsletter'])
async def sub_newsletter(request: EMAILSCHEMA, db: Session = Depends(get_db)):
    """
    Newsletter subscription endpoint
    """

    # check for duplicate email
    existing_subscriber = db.query(NEWSLETTER).filter(NEWSLETTER.email==request.email).first()
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
    new_subscriber = NEWSLETTER(email=request.email)
    db.add(new_subscriber)
    db.commit()

    return {
        "message": "Thank you for subscribing to our newsletter.",
        "success": True,
        "status": status.HTTP_201_CREATED
    }
