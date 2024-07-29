#!/usr/bin/env python3
"""Defines request and response schemas for comments endpoints"""

from datetime import datetime
from typing_extensions import Annotated
from pydantic import BaseModel, StringConstraints
from typing import Dict, Optional


class UpdateComment(BaseModel):
    """Request schema for updating a comment"""
    content: str


class Comment(BaseModel):
    """Defines a comment a comment response"""
    id: str
    content: str
    created_at: str
    updated_at: str
    user: Optional[Dict]


class CommentResponse(BaseModel):
    """Response schema for a comment"""
    success: bool
    status_code: int
    message: str
    data: Comment


class CommentCreate(BaseModel):
    content: Annotated[str,
                       StringConstraints(strip_whitespace=True, min_length=1)]


class CommentData(BaseModel):
    id: str
    user_id: str
    blog_id: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentSuccessResponse(BaseModel):
    status_code: int = 201
    message: str
    success: bool = True
    data: CommentData


class CommentDislike(BaseModel):
    id: str
    comment_id: str
    user_id: str
    ip_address: str
    created_at: datetime
    updated_at: datetime


class DislikeSuccessResponse(BaseModel):
    status_code: int = 201
    message: str
    success: bool = True
    data: CommentDislike
