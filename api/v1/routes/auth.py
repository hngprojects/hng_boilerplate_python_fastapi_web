from fastapi import APIRouter,Depends,status,HTTPException,Response
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.schemas import schemas

from api.db import database
from api.utils import deps
from api.utils import oauth2




from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=['authentication'])

#here request body are sent through form not json
@router.post('/api/v1/login')
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
    user = db.query(User).filter(User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"invalid credentials")
    
    #r = utils.verify(user_credentials.password,user.password)
    if not deps.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"invalid credentials")
    

    access_token= oauth2.create_access_token(data={"user_id":str(user.id)})
    # access_token= oauth2.create_access_token(data={"user_id":user.id})


    return {"access_token": access_token,"token_type": "bearer"}





