from typing import List
from pydantic import BaseModel


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
