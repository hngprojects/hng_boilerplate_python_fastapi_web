from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.permission import Permission
from api.v1.models.org import Organization
from api.v1.models.user import User
from api.utils.dependencies import get_current_user
from api.utils.json_response import JsonResponseDict
from typing import Annotated
from uuid import UUID


org = APIRouter(prefix='/organization', tags=['Organizations'])

@org.get('/{orgId}/users')
async def get_users(
        user: Annotated[User, Depends(get_current_user)], 
        orgId: str,
        db: Session = Depends(get_db)
        ):
    try:
        orgId = UUID(orgId)
    except ValueError:
        raise HTTPException(
                detail="Id is not a valid uuid",
                status_code=status.HTTP_400_BAD_REQUEST
                )
    if not user:
        raise HTTPException(
                detail="User is not logged in",
                status_code=status.HTTP_401_UNAUTHORIZED
                )
    org = db.query(Organization).filter_by(id=orgId).first()

    if not org:
        return JsonResponseDict(
                message="Organization does not exist",
                error="Not Found",
                status_code=status.HTTP_404_NOT_FOUND
                )

    if user not in org.users:
        return JsonResponseDict(
                message="User does not have access to the organization",
                error="Forbidden access",
                status_code=status.HTTP_403_FORBIDDEN
                )

    org_users = org.users

    data = [user.to_dict() for user in org_users]
    print(data)

    return JsonResponseDict(
            message="Users retrived successfully",
            data=data,
            status_code=status.HTTP_200_OK
            )
