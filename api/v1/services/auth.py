import passlib.hash as _hash
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from fastapi import HTTPException, status
from datetime import datetime,timedelta
from typing import Annotated, Union
from uuid import uuid4
from decouple import config

from api.v1.models.auth import User as UserModel, BlackListToken
from api.v1.schemas import auth as user_schema
from api.core import responses
from api.core.base.services import Service


SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config("ALGORITHM")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_REFRESH_EXPIRY = int(config("JWT_REFRESH_EXPIRY"))


class User(Service):

    def __init__(self) -> None:
        pass

    def create(self, user: user_schema.CreateUser, db: Session):
        created_user = UserModel(unique_id=user.unique_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email,
                            date_created=user.date_created,
                            last_updated=user.last_updated,
                            is_active=user.is_active,
                            password=self.hash_password(user.password))
        db.add(created_user)
        db.commit()

        return created_user

    @staticmethod
    def fetch(db: Session, id: int = None, unique_id: str = None) -> user_schema.User:
        if id is None and unique_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=responses.ID_OR_UNIQUE_ID_REQUIRED)
            
        user = db.query(UserModel).filter(UserModel.id==id).filter(UserModel.is_deleted==False).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=responses.NOT_FOUND)
        
        return user

    @staticmethod
    def fetch_all():
        pass
    
    @staticmethod
    def fetch_by_email(email: str, db: Session) -> user_schema.User:
        user = db.query(UserModel).filter(UserModel.email == email, UserModel.is_deleted==False).first()

        return user
           
    def update(self):
        pass

    @classmethod
    def delete(cls,db: Session, id: int=None, unique_id: str=None) -> user_schema.User:
        user =  cls.fetch(id=id, unique_id=unique_id, db=db)
        user.is_deleted = True
        db.commit()
        return user

    @classmethod
    async def get_current_user(cls, token: Annotated[str, Depends(oauth2_scheme)], db:Session) -> user_schema.User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=responses.COULD_NOT_VALIDATE_CRED,
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            id: str = payload.get("id")
            if id is None:
                raise credentials_exception
            token_data = id
        except JWTError:
            raise credentials_exception
        user = cls.fetch(id=token_data,db=db)
        if user is None:
            raise credentials_exception
        return user

    @classmethod
    def authenticate_user(cls, db: Session, password: str,email: str) -> user_schema.User:
        user = cls.fetch_by_email(email=email, db=db)
        if not user:
            return False
        if not cls.verify_password(password, user.password):
            return False
        return user

    @staticmethod
    def verify_password(password, hashed_password):
        return pwd_context.verify(password, hashed_password)

    @staticmethod
    def hash_password(password) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, db: Session, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        db.commit()

        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict, db: Session) -> str:
        to_encode = data.copy()

        expire = datetime.utcnow() + timedelta(seconds=int(JWT_REFRESH_EXPIRY))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    @classmethod
    def verify_access_token(cls, token: str, db: Session) -> user_schema.TokenData:
        try:  
            invalid_token = cls.check_token_blacklist(db=db, token=token)
            if invalid_token == True:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=responses.INVALID_CREDENTIALS,
                                     headers={"WWW-Authenticate": "Bearer"})

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            id: int = payload.get("id")

            if id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=responses.INVALID_CREDENTIALS,
                                     headers={"WWW-Authenticate": "Bearer"})

            user = cls.fetch(db=db,id=id)

            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=responses.INVALID_CREDENTIALS,
                                    headers={"WWW-Authenticate": "Bearer"})

            
            token_data = user_schema.TokenData(email=user.email, id=id)

            return token_data

        except JWTError as error:
            print(error, 'error')
            return JWTError(HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=responses.INVALID_CREDENTIALS,
                                     headers={"WWW-Authenticate": "Bearer"}))

    @classmethod
    def verify_refresh_token(cls, refresh_token: str, db: Session) ->  user_schema.TokenData:
        try:
            if not refresh_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=responses.EXPIRED)

            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            id: str = payload.get("id")

            if id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=responses.INVALID_CREDENTIALS,
                                     headers={"WWW-Authenticate": "Bearer"})

            user = cls.fetch(id=id, db=db)

            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=responses.INVALID_CREDENTIALS)

            
            token_data = user_schema.TokenData(email=user.email, id=id)

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=responses.INVALID_CREDENTIALS,
                                     headers={"WWW-Authenticate": "Bearer"})

        return token_data
    
    @staticmethod
    def check_token_blacklist(token: str, db:Session)-> bool:
        fetched_token = db.query(BlackListToken).filter(BlackListToken.token == token).first()

        if fetched_token:
            return True
        else:
            return False

    @staticmethod
    def logout(token: str, user: user_schema.ShowUser, db:Session) -> str:
        blacklist_token = BlackListToken(
            token=token.split(' ')[1],
            created_by=user.id
        )

        db.add(blacklist_token)
        db.commit()

        return token


        




    


    










