#!/usr/bin/env python3
"""Defines endpoint schemas for teams"""

from typing import Optional
from pydantic import BaseModel


class UpdateTeamMember(BaseModel):
    """Schema for update team member request"""
    role: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    picture_url: Optional[str] = None
