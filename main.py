import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.db.database import get_db
from api.db.database import Base, engine
import os
from dotenv import load_dotenv
import jwt
import httpx  

load_dotenv()

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(auth, tags=["Auth"])
# app.include_router(users, tags=["Users"])
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    user_id: int = payload.get("user_id")
    return {"id": user_id}

@app.delete("/api/v1/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if user.id == current_user["id"]:
        user.is_active = False
        db.commit()
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post("/api/v1/auth/logout", headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to log out user")
        return {
            "status": "success",
            "message": "Deletion in progress",
        }
    else:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
