#!/usr/bin/env python3
"""Defines endpoint schemas for teams"""

from pydantic import Field, BaseModel
from datetime import datetime
from typing import Optional


class UpdateTeamMember(BaseModel):
    """Schema for update team member request"""
    role: Optional[str] = Field(
        default=None, min_length=1, title="Role of the team member")
    name: Optional[str] = Field(
        default=None, min_length=1, title="Name of the team member")
    description: Optional[str] = Field(default=None, min_length=1,
                                       title="Description of the team member")
    picture_url: Optional[str] = Field(
        default=None, min_length=1, title="URL of the team member picture")


class PostTeamMemberSchema(BaseModel):
    """Pydantic Model for adding user to waitlist"""

    name: str = Field(min_length=1, title="Name of the team member")
    role: str = Field(min_length=1, title="Role of the team member")
    description: str = Field(
        min_length=1, title="Description of the team member")
    picture_url: str = Field(
        min_length=1, title="URL of the team member picture")

    team_type: Optional[str] = Field(
        default=None, min_length=1, title="Type of team member")
    facebook_link: Optional[str] = Field(
        default=None, min_length=1, title="Facebook link")
    instagram_link: Optional[str] = Field(
        default=None, min_length=1, title="Instagram link"
    )
    xtwitter_link: Optional[str] = Field(
        default=None, min_length=1, title="Twitter link")


class TeamMemberCreateResponseSchema(PostTeamMemberSchema):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
