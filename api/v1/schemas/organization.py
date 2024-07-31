from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, EmailStr, field_validator

from api.utils.success_response import success_response

class OrganizationBase(BaseModel):
    '''Base organization schema'''

    id: str
    created_at: datetime
    updated_at: datetime
    company_name: str
    company_email: EmailStr
    industry: str
    organization_type: str
    country: str
    state: str
    address: str
    lga: str
    
    class Config:
        from_attributes = True  # Enable Pydantic to read ORM attributes

class CreateUpdateOrganization(BaseModel):
    '''Organization schema to create or update organization'''

    company_name: str
    company_email: EmailStr
    industry: str
    organization_type: str
    country: str
    state: str
    address: str
    lga: str


    
    class Config:
        from_attributes = True  # Enable Pydantic to read ORM attributes
        
class AddUpdateOrganizationRole(BaseModel):
    '''Schema to update a user role in an organization'''

    role: str
    user_id: str
    org_id: str

    @field_validator('role')
    def role_validator(cls, value):
        if value not in ['admin', 'user', 'guest', 'owner']:
            raise ValueError('Role has to be one of admin, guest, user, or owner')
        return value


class RemoveUserFromOrganization(BaseModel):
    '''Schema to delete a user role in an organization'''

    user_id: str
    org_id: str


class PaginatedOrgUsers(BaseModel):
    """Describe response object for paginated users in organization"""
    page: int
    per_page: int
    per_page: int
    total: int
    status_code: int
    success: bool
    message: str
    data: List[Dict]
