from typing import List
from pydantic import BaseModel

from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

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


class OrganizationBase(BaseModel):
    id: str


class OrganizationDetail(OrganizationBase):
    name: str
    description: str
    billing_plans: List | None = []
    invitations: List | None = []
    products: List | None = []
    users: List | None = []


class OrganizationResponse(BaseModel):
    status: str
    message: str
    data: OrganizationDetail


class OrganizationAddUser(BaseModel):
    user_id: str
