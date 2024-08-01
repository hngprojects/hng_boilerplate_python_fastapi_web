from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks
from sqlalchemy.orm import Session
from api.v1.schemas.request_password_reset import RequestEmail, ResetPassword
from api.db.database import get_db as get_session
from api.v1.services.request_pwd import reset_service
import logging

pwd_reset = APIRouter(prefix="/auth", tags=["Authentication"])


# generate password reset link
@pwd_reset.post("/request-password-reset")
async def request_reset_link(
    reset_schema: RequestEmail,
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    return await reset_service.create(reset_schema, request, session, background_tasks)


# process password link
@pwd_reset.get("/reset-password")
async def process_reset_link(
    token: str = Query(...), session: Session = Depends(get_session)
):
    return reset_service.process_reset_link(token, session)


# change the password
@pwd_reset.post("/reset-password")
async def reset_password(
    data: ResetPassword,
    token: str = Query(...),
    session: Session = Depends(get_session),
):
    return reset_service.reset_password(data, token, session)
