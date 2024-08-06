#!/usr/bin/env python3
"""Defines endpoint schemas for teams"""

from pydantic import EmailStr, BaseModel
from datetime import datetime
from typing import Optional


class UpdateTeamMember(BaseModel):
    """Schema for update team member request"""
    role: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    picture_url: Optional[str] = None


class PostTeamMemberSchema(BaseModel):
    """Pydantic Model for adding user to waitlist"""

    name: str
    role: str
    description: str
    picture_url: str

    team_type: Optional[str] = None
    facebook_link: Optional[str] = None
    instagram_link: Optional[str] = None
    xtwitter_link: Optional[str] = None


class TeamMemberCreateResponseSchema(PostTeamMemberSchema):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
