from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.comment import CommentCreate, CommentSuccessResponse
from api.v1.services.comment import comment_service 
from api.v1.services.user import user_service

comment = APIRouter(prefix="/comments", tags=["Comments"])
