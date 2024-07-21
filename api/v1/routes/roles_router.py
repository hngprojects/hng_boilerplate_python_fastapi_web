from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from api.db.database import get_db
from api.v1.models.roles import Role

router = APIRouter()

@router.get("/roles/all", status_code=HTTP_200_OK)
async def get_all_roles(db: Session = Depends(get_db)):
    try:
        roles = db.query(Role).all()
        if not roles:
            return {"status_code": HTTP_200_OK, "data": []}

        roles_list = [{"id": role.id, "name": role.name, "description": role.description, "created_at": role.created_at} for role in roles]

        return {"status_code": HTTP_200_OK, "data": roles_list}
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred, roles not retrieved")
