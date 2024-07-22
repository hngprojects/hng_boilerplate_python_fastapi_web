from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    status
    )
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
# impot about model
from api.db.database import get_db, Base, engine


Base.metadata.create_all(bind=engine)

class ErrorException(HTTPException):
    """
    Custom error handling
    """
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")

async def error_exception_handler(request: Request, exc: ErrorException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "success": exc.success,
            "status_code": exc.status_code
        }
    )

router = APIRouter()

@router.get('/api/v1/content/about', tags=['About_page'])
async def retrieve_about_page():
    # get data from database
    pass