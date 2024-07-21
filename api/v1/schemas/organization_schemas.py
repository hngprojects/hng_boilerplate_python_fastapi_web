#!/usr/bin/python3
"""
Contains schemas for organisation creation
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Org_request(BaseModel):
    """
    Class defination for organization request schema
    """
    name: str
    description: str
    email: str
    industry: str
    type: str
    country: str
    address: str
    state: str


class Data(BaseModel):
    """
    Schema for organisation model
    """
    id: str
    name: str
    description: str
    owner_id: str
    slug: Optional[str] = None
    email: str
    industry: str
    type: str
    country: str
    address: str
    state: str
    created_at: datetime
    updated_at: datetime


class Response(BaseModel):
    """
    Schema for the Organization Response model
    """
    status: str = "success"
    message: str = "organisation created successfully"
    data: Data
    status_code: int = 201
