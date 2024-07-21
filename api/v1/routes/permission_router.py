from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    status
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.db.database import get_db, Base, engine
from api.v1.models.permission import Permission
from api.v1.schemas.permission import PermissionCreate, Permission, PermissionUpdate
from api.v1.services.permission_service import (
    create_permission,
    get_permissions,
    get_permission,
    update_permission,
    delete_permission
)
from api.utils.auth import get_current_admin
from api.v1.models.user import User

Base.metadata.create_all(bind=engine)

class CustomException(HTTPException):
    """
    Custom error handling
    """
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")

async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "success": exc.success,
            "status_code": exc.status_code
        }
    )

router = APIRouter()

@router.post('/api/v1/permissions', tags=['Permissions'])
async def create_permission_endpoint(request: PermissionCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """
    Create a new permission
    """
    try:
        new_permission = create_permission(db, request)
        return {
            "message": "Permission created successfully.",
            "success": True,
            "status": status.HTTP_201_CREATED,
            "data": new_permission
        }
    except HTTPException as e:
        raise CustomException(
            status_code=e.status_code,
            detail={
                "message": e.detail,
                "success": False,
                "status_code": e.status_code
            }
        )

@router.get('/api/v1/permissions', tags=['Permissions'], response_model=list[Permission])
async def read_permissions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """
    Get all permissions
    """
    permissions = get_permissions(db, skip=skip, limit=limit)
    return {
        "message": "Permissions fetched successfully.",
        "success": True,
        "status": status.HTTP_200_OK,
        "data": permissions
    }

@router.get('/api/v1/permissions/{permission_id}', tags=['Permissions'], response_model=Permission)
async def read_permission(permission_id: str, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """
    Get a specific permission
    """
    db_permission = get_permission(db, permission_id)
    if db_permission is None:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Permission not found",
                "success": False,
                "status_code": 404
            }
        )
    return {
        "message": "Permission fetched successfully.",
        "success": True,
        "status": status.HTTP_200_OK,
        "data": db_permission
    }

@router.put('/api/v1/permissions/{permission_id}', tags=['Permissions'], response_model=Permission)
async def update_permission_endpoint(permission_id: str, request: PermissionUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """
    Update a specific permission
    """
    try:
        updated_permission = update_permission(db, permission_id, request)
        return {
            "message": "Permission updated successfully.",
            "success": True,
            "status": status.HTTP_200_OK,
            "data": updated_permission
        }
    except HTTPException as e:
        raise CustomException(
            status_code=e.status_code,
            detail={
                "message": e.detail,
                "success": False,
                "status_code": e.status_code
            }
        )

@router.delete('/api/v1/permissions/{permission_id}', tags=['Permissions'], response_model=Permission)
async def delete_permission_endpoint(permission_id: str, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """
    Delete a specific permission
    """
    try:
        deleted_permission = delete_permission(db, permission_id)
        return {
            "message": "Permission deleted successfully.",
            "success": True,
            "status": status.HTTP_200_OK,
            "data": deleted_permission
        }
    except HTTPException as e:
        raise CustomException(
            status_code=e.status_code,
            detail={
                "message": e.detail,
                "success": False,
                "status_code": e.status_code
            }
        )
