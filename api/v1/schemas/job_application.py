
"""
Job application schemas
"""
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


from typing import Union, Optional
import re

class JobApplicationData(BaseModel):
    """
    Schema for job application base
    """
    job_id: str
    applicant_name: str
    applicant_email: str
    resume_link: str
    portfolio_link: Union[str, None]
    cover_letter: Union[str, None]
    application_status: str

    model_config = ConfigDict(from_attributes=True)

class SingleJobAppResponse(BaseModel):
    """
    Single job application response schema
    """
    status: str
    message: str
    status_code: int
    data: JobApplicationData

class JobApplicationBase(BaseModel):
    '''Base model for job application'''

    applicant_name: str
    applicant_email: EmailStr
    cover_letter: str
    resume_link: str
    portfolio_link: str
    application_status: str

class CreateJobApplication(BaseModel):
    '''Schema for creating job application'''

    applicant_name: str
    applicant_email: EmailStr
    cover_letter: str
    resume_link: str
    portfolio_link: Optional[str] = None
    application_status: str = 'pending'

    @field_validator('resume_link', 'portfolio_link')
    def validate_links(cls, v):
        # Regular expression pattern to match valid URLs
        url_regex = re.compile(
            r'^(https?:\/\/)?'  # optional scheme
            r'((([a-zA-Z0-9\-]+)\.)+[a-zA-Z]{2,})'  # domain
            r'(\/[^\s]*)?$'  # path
        )
        if not url_regex.match(v):
            raise ValueError('Invalid URL format')
        return v


class UpdateJobApplication(BaseModel):
    '''Schema for updating job application'''

    applicant_name: Optional[str] = None
    applicant_email: Optional[EmailStr] = None
    cover_letter: Optional[str] = None
    resume_link: Optional[str] = None
    portfolio_link: Optional[str] = None
    application_status: Optional[str] = None

    @field_validator('resume_link', 'portfolio_link')
    def validate_links(cls, v):
        # Regular expression pattern to match valid URLs
        url_regex = re.compile(
            r'^(https?:\/\/)?'  # optional scheme
            r'((([a-zA-Z0-9\-]+)\.)+[a-zA-Z]{2,})'  # domain
            r'(\/[^\s]*)?$'  # path
        )
        if not url_regex.match(v):
            raise ValueError('Invalid URL format')
        return v

