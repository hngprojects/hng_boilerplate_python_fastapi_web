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
from api.v1.services.newsletter import NewsletterService

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

newsletter = APIRouter(tags=['Newsletter'])

@newsletter.post('/newsletters')
async def sub_newsletter(request: EMAILSCHEMA, db: Session = Depends(get_db)):
    """
    Newsletter subscription endpoint
    """

    # check for duplicate email
    existing_subscriber = NewsletterService.check_existing_subscriber(db, request)
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
    NewsletterService.create(db, request)

    return {
        "message": "Thank you for subscribing to our newsletter.",
        "success": True,
        "status": status.HTTP_201_CREATED
    }
