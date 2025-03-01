# api/v1/schemas/seed.py
from pydantic import BaseModel
from typing import Optional

class SeedUserRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superadmin: Optional[bool] = False
    is_deleted: Optional[bool] = False
    is_verified: Optional[bool] = False
    organization_name: Optional[str] = None #Add organization name