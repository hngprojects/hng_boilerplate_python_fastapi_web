from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User  # Assuming User model exists in models folder
from api.v1.models.password_reset import OTP  # Import the new OTP model
from api.v1.schemas.password_reset import EMAILSCHEMA
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from random import randint

# Custom Exception Class
class CustomException(HTTPException):
    """
    Custom error handling
    """
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")

# Custom Exception Handler
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "success": exc.success,
            "status_code": exc.status_code
        }
    )

# APIRouter Instance
password_reset = APIRouter(prefix='/api/v1/auth', tags=['Password Reset'])

# Endpoint to Reset Password
@password_reset.post('/password/reset')
async def reset_password(request: EMAILSCHEMA, db: Session = Depends(get_db)):
    """
    Password reset endpoint
    """

    # Check if the user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "User with this email does not exist.",
                "success": False,
                "status_code": 404
            }
        )

    # Generate OTP
    otp_code = randint(100000, 999999)
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=10)

    # Save the OTP in the database
    new_otp = OTP(email=request.email, otp_code=otp_code)
    db.add(new_otp)
    db.commit()

    # Send OTP to user's email
    try:
        send_otp_email(request.email, otp_code)
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "OTP code could not be sent successfully",
                "success": False,
                "status_code": 500
            }
        )

    return {
        "message": f"OTP password reset code sent successfully to {request.email}",
        "success": True,
        "status_code": status.HTTP_200_OK
    }

