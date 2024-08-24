from typing import Annotated
from api.db.database import get_db
from api.v1.schemas.api_status import APIStatusPost
from api.v1.services.api_status import APIStatusService
from api.utils.success_response import success_response
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

api_status = APIRouter(prefix='/api-status', tags=['API Status'])


@api_status.get('', response_model=success_response, status_code=200)
async def get_api_status(db: Annotated[Session, Depends(get_db)]):
    all_status = APIStatusService.fetch_all(db)

    return success_response(
        message='All API Status fetched successfully',
        data=all_status,
        status_code=status.HTTP_200_OK
    )


@api_status.post('', response_model=success_response, status_code=201)
async def post_api_status(
    schema: APIStatusPost, 
    db: Annotated[Session, Depends(get_db)]
):
    new_status = APIStatusService.upsert(db, schema)

    return success_response(
        message='API Status created successfully',
        data=new_status,
        status_code=status.HTTP_201_CREATED
    )
