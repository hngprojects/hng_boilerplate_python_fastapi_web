from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from api.v1.schemas.request_password_reset import RequestEmail, ResetPassword
from api.db.database import get_db as get_session
from api.v1.services.request_pwd import reset_service
import logging

pwd_reset = APIRouter(prefix='/auth')

#generate password reset link
@pwd_reset.post("/request-password-reset", tags=["password reset"])
async def request_reset_link(reset_schema: RequestEmail, request: Request, session: Session = Depends(get_session)):
    return reset_service.create(reset_schema, request, session)

#process password link 
@pwd_reset.get("/reset-password", tags=["password reset"])
async def process_reset_link(token: str= Query(...), session: Session = Depends(get_session)):
    return reset_service.process_reset_link(token, session)

#change the password
@pwd_reset.post("/reset-password", tags=["password reset"])
async def reset_password(data: ResetPassword, token: str = Query(...), session: Session = Depends(get_session)):
    return reset_service.reset_password(data, token, session)
