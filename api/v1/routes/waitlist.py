from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from api.v1.models.user import User, WaitlistUser
from api.v1.schemas.waitlist import WaitlistUserResponse
from api.db.database import get_db
from api.utils.dependencies import get_current_user

def get_user_by_current(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).filter(User.id == current_user.id).first()

waitlist = APIRouter(prefix='/waitlist', tags=['Waitlist'])
@waitlist.get("/users", response_model=WaitlistUserResponse)
def get_waitlist_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_by_current(db, current_user)
    

    if not user.is_admin:
        raise HTTPException(   
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have admin privileges"
        )
    
    waitlist_emails = [user.email for user in db.query(WaitlistUser).all()]
    
    response = WaitlistUserResponse(
        message= "Waitlist retrieved successfully",
        status_code= 200,
        data= waitlist_emails
    )

    return response