from fastapi import Depends, Cookie, HTTPException, APIRouter, Depends, status, Response, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Union
from decouple import config
from api.v1.schemas import auth as user_schema
from api.db.database import get_db
from api.v1.services.auth import User
from api.v1.models.auth import User as UserModel
from api.core import responses
from api.core.dependencies.user import is_authenticated

ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))
JWT_REFRESH_EXPIRY = int(config('JWT_REFRESH_EXPIRY'))
IS_REFRESH_TOKEN_SECURE = True if config('PYTHON_ENV') == "production" else False


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = APIRouter(tags=["Auth"])


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    response: Response,
    user:user_schema.CreateUser,
    db:Session = Depends(get_db)
):

    """
    Endpoint to create a user

    Returns: Created User.
    """
    userService = User()
    created_user = userService.create(user=user, db=db)


    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = userService.create_access_token(
        data={"id": created_user.id}, db=db, expires_delta=access_token_expires
    )

    refresh_token = userService.create_refresh_token(data={"id": created_user.id}, db=db)

    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=JWT_REFRESH_EXPIRY,
            secure=True,
            httponly=True,
            samesite="strict",
        )

    return {"message": responses.SUCCESS,
            "data": user_schema.ShowUser.model_validate(created_user),
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
            }


@app.post("/login", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    response: Response,
    data: user_schema.Login,
    background_task: BackgroundTasks,
    db: Session = Depends(get_db)
):  
    """
    LOGIN

    Returns: Logged in User and access token.
    """

    userService = User()
    user = userService.authenticate_user(email=data.email, password=data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=responses.INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = userService.create_access_token(
        data={"id": user.id}, db=db, expires_delta=access_token_expires
    )

    refresh_token = userService.create_refresh_token(data={"id": user.id}, db=db)

    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=JWT_REFRESH_EXPIRY,
            secure=True,
            httponly=True,
            samesite="strict",
            path="/"
        )
    
    return {
            "data": user_schema.ShowUser.model_validate(user), 
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
            }



@app.get("/user", status_code=status.HTTP_200_OK)
async def get_user(
    user: user_schema.User = Depends(is_authenticated),
    db: Session = Depends(get_db),
):
    """
        Returns an authenticated user information
    """
    print(user)
    return user



@app.get("/refresh-access-token", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    response: Response,
    refresh_token: Union[str, None] = Cookie(default=None),
    db: Session = Depends(get_db),
):
    """Refreshes an access_token with the issued refresh_token
    Parameters
        ----------
        refresh_token : str, None
            The refresh token sent in the cookie by the client (default is None)

        Raises
        ------
        UnauthorizedError
            If the refresh token is None.
    """
    print(refresh_token)
    credentials_exception =HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if refresh_token is None:
        raise HTTPException(
            detail="Log in to authenticate user",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    valid_refresh_token = User.verify_refresh_token(
        refresh_token, db
    )

    if valid_refresh_token.email is None:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=JWT_REFRESH_EXPIRY,
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )

        print("refresh failed")
    else:
        user = (
            db.query(UserModel)
            .filter(UserModel.id == valid_refresh_token.id)
            .first()
        )

        access_token = User.create_access_token(
            {"user_id": valid_refresh_token.id}, db
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=JWT_REFRESH_EXPIRY,
            secure=IS_REFRESH_TOKEN_SECURE,
            httponly=True,
            samesite="strict",
        )
    
    # Access token expires in 15 mins,
    return {"user": user_schema.ShowUser.model_validate(user), "access_token": access_token, "expires_in": 900}



@app.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    request: Request,
    response: Response,
    user: user_schema.User = Depends(is_authenticated),
    db: Session = Depends(get_db),
):
    """
        This endpoint logs out an authenticated user.

        Returns message: User logged out successfully.
    """

    userService = User()
    access_token = request.headers.get('Authorization')

    logout = userService.logout(token=access_token, user=user, db=db)

    response.set_cookie(
        key="refresh_token",
        max_age="0",
        secure=True,
        httponly=True,
        samesite="strict",
    )

    return {"message": "User logged out successfully."}


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    user: user_schema.User = Depends(is_authenticated),
    db: Session = Depends(get_db),
):

    """
        This endpoint deletes a user from the db. (Soft delete)

        Returns message: User deleted successfully.
    """
    userService =  User()
    deleted_user = userService.delete(db=db, id=user_id)

    return {"message": "User deleted successfully."}


@app.post("/users/roles", status_code=status.HTTP_200_OK)
async def create_user_roles(
    user: user_schema.ShowUser = Depends(is_authenticated),
    db:Session = Depends(get_db)
):

    """
     Endpoint to create custom roles for users mixing permissions.

     Returns created role
    
    """
    pass