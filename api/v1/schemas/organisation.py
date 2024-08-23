from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional

from api.utils.success_response import success_response

class OrganisationBase(BaseModel):
    """Base organisation schema"""

    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    email: Optional[EmailStr] = None
    industry: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


class CreateUpdateOrganisation(BaseModel):
    """Organisation schema to create or update organisation"""

    name: str
    email: Optional[EmailStr] = None
    industry: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


class AddUpdateOrganisationRole(BaseModel):
    """Schema to update a user role in an organisation"""

    role: str
    user_id: str
    org_id: str

    @field_validator("role")
    def role_validator(cls, value):
        if value not in ["admin", "user", "guest", "owner"]:
            raise ValueError("Role has to be one of admin, guest, user, or owner")
        return value


class RemoveUserFromOrganisation(BaseModel):
    """Schema to delete a user role in an organisation"""

    user_id: str
    org_id: str


class PaginatedOrgUsers(BaseModel):
    """Describe response object for paginated users in organisation"""
    page: int
    per_page: int
    per_page: int
    total: int
    status_code: int
    success: bool
    message: str
    data: List[Dict]

class OrganisationData(BaseModel):
    """Base organisation schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    email: Optional[EmailStr] = None
    industry: Optional[str] = None
    user_role: List[str]
    type: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    organisation_id: str
