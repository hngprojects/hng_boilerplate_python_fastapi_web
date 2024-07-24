from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.contact import ContactMessage
from api.v1.schemas.contact import ContactMessageList

router = APIRouter(prefix='/contact-us', tags=['ContactUs'])


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")


@router.get('/messages/', response_model=ContactMessageList)
async def get_contact_messages(db: Session = Depends(get_db)):
    """
    Fetch all contact messages endpoint
    """
    messages = db.query(ContactMessage).all()
    if not messages:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "No contact messages found.",
                "success": False,
                "status_code": 404
            }
        )
    return {"messages": messages}
