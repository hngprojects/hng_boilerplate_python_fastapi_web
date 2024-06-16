from typing import Union
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Cookie, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_
from jose import JWTError, jwt

from api.v1.schemas import auth as user_schema
from api.v1.services.auth import User
from api.v1.models.auth import User as UserModel

from api.db.database import get_db
from api.core import responses

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def is_authenticated(
    access_token: Union[str, user_schema.Token] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Union[user_schema.User, JWTError]:

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=responses.INVALID_CREDENTIALS)

    userService = User()

    access_token_info = userService.verify_access_token(access_token, db)

    if type(access_token_info) is JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=responses.INVALID_CREDENTIALS)

    user = userService.fetch(id=access_token_info.id,db=db)

    return user


