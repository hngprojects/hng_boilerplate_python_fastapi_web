from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field


# Question models
class CommunityQuestionCreate(BaseModel):
    title: str
    message: str
    user_id: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class CommunityQuestionResponse(BaseModel):
    id: str
    title: str
    message: str
    user_id: str
    timestamp: datetime
    is_resolved: bool
    
    model_config = {"from_attributes": True}


# Answer models
class CommunityAnswerCreate(BaseModel):
    message: str
    user_id: str
    question_id: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class CommunityAnswerResponse(BaseModel):
    id: str
    message: str
    user_id: str
    question_id: str
    timestamp: datetime
    is_accepted: bool
    
    model_config = {"from_attributes": True}


# Extended response models for nested data
class CommunityAnswerWithUser(CommunityAnswerResponse):
    user_name: str  # Assuming you have a user_name field


class CommunityQuestionWithAnswers(CommunityQuestionResponse):
    answers: List[CommunityAnswerWithUser] = []
    answer_count: int = 0
    
    model_config = {"from_attributes": True}