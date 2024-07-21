from fastapi import Depends, HTTPException, APIRouter, Request
from jose import JWTError
import jwt
from sqlalchemy.orm import Session

from api.core.dependencies.email import mail_service
from api.utils.auth import create_access_token

from api.utils.config import SECRET_KEY, ALGORITHM
from ..models.user import User
from api.v1.schemas.user import DeactivateUserSchema
from api.db.database import get_db
from api.utils.dependencies import get_current_user


user = APIRouter(prefix='/api/v1/users', tags=['Users'])

@user.patch('/accounts/deactivate', status_code=200)
async def deactivate_account(request: Request, schema: DeactivateUserSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    '''Endpoint to deactivate a user account'''

    # Generate an access token containing user credentials
    token = create_access_token(data={'username': f'{user.username}'})

    if not user.is_active:
        raise HTTPException(400, 'User is inactive')
    
    if schema.confirmation == False:
        raise HTTPException(400, 'Confirmation required to deactivate account')

    user.is_active = False

    # Send aail to user
    mail_service.send_mail(
        to=user.email, 
        subject='Account deactivation', 
        body=f'Hello, {user.first_name},\n\nYour account has been deactivated successfully.\nTo reactivate your account if this was a mistake, please click the link below:\n{request.url.hostname}/api/users/accounts/reactivate?token={token}\n\nThis link expires after 15 minutes.'
    )

    # Commit changes to deactivate the user
    db.commit()

    return {"status_code": 200, "message": "Account deactivated successfully. Check email for confirmation"}


@user.get('/accounts/reactivate', status_code=200)
async def reactivate_account(request: Request, db: Session = Depends(get_db)):
    '''Endpoint to reactivate a user account'''

    # Get access token from query
    token = request.query_params.get('token')

    # Validate the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('username')

        if username is None:
            raise HTTPException(400, 'Invalid token')
        
    except JWTError:
        raise HTTPException(400, 'Invalid token')
    
    user = db.query(User).filter(User.username == username).first()

    if user.is_active:
        raise HTTPException(400, 'User is already active')

    user.is_active = True

    # Send aail to user
    mail_service.send_mail(
        to=user.email, 
        subject='Account reactivation', 
        body=f'Hello, {user.first_name},\n\nYour account has been reactivated successfully'
    )

    # Commit changes to deactivate the user
    db.commit()

    return {"status_code": 200, "message": "Account reactivated successfully. Check email for confirmation"}
