from fastapi import APIRouter, HTTPException, Depends, status
from .config import SECRET_KEY, ALGORITHM 
from jose import JWTError
from api.utils.auth import create_access_token
import jwt

data = {"username": "testuser"}
token = create_access_token(data)
print(f"Created Token: {token}")


try:
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"Decoded: {decoded}")
except JWTError as e:
    print(f"Token validation error: {e}")

